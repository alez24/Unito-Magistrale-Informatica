# ============================================================
# LAB-4 — Topic Modeling con BERTopic
# ============================================================

import os
import time
import warnings

import pandas as pd
from bertopic import BERTopic
from datasets import load_dataset
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from umap import UMAP

warnings.filterwarnings("ignore")

OUTPUT_DIR = "lab4_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. CARICAMENTO DATASET
# ============================================================
print("Caricamento dataset ArXiv NLP...")
dataset = load_dataset("MaartenGr/arxiv_nlp", split="train")
abstracts = dataset["Abstracts"]
titles = dataset["Titles"] if "Titles" in dataset.column_names else [""] * len(abstracts)
print(f"Numero abstract caricati: {len(abstracts)}")

# (Opzionale) Subset per test rapido
# abstracts = abstracts[:5000]
# titles = titles[:5000]


# ============================================================
# 2. CONFIGURAZIONI SPERIMENTALI
# Regola: varia una sola cosa per confronto.
# ============================================================
configurations = [
    {
        "nome": "Config_1_baseline",
        "embedding_model": "thenlper/gte-small",
        "umap_params": {
            "n_components": 5,
            "n_neighbors": 15,
            "min_dist": 0.0,
            "metric": "cosine",
            "random_state": 42,
        },
        "hdbscan_params": {
            "min_cluster_size": 50,
            "metric": "euclidean",
            "cluster_selection_method": "eom",
        },
    },
    {
        # Cambia SOLO il modello embedding rispetto alla baseline
        "nome": "Config_2_model_only",
        "embedding_model": "all-MiniLM-L6-v2",
        "umap_params": {
            "n_components": 5,
            "n_neighbors": 15,
            "min_dist": 0.0,
            "metric": "cosine",
            "random_state": 42,
        },
        "hdbscan_params": {
            "min_cluster_size": 50,
            "metric": "euclidean",
            "cluster_selection_method": "eom",
        },
    },
    {
        # Stesso embedding di Config_2, cambia SOLO UMAP/HDBSCAN
        "nome": "Config_3_cluster_only",
        "embedding_model": "all-MiniLM-L6-v2",
        "umap_params": {
            "n_components": 10,
            "n_neighbors": 30,
            "min_dist": 0.0,
            "metric": "cosine",
            "random_state": 42,
        },
        "hdbscan_params": {
            "min_cluster_size": 150,
            "metric": "euclidean",
            "cluster_selection_method": "eom",
        },
    },
]


# ============================================================
# 3. CACHE EMBEDDING E RIDUZIONE 2D
# ============================================================
emb_cache = {}
reduced2d_cache = {}


def get_embeddings(model_name, docs):
    if model_name in emb_cache:
        model, embeddings = emb_cache[model_name]
        return model, embeddings, 0.0, True

    t0 = time.time()
    model = SentenceTransformer(model_name)
    embeddings = model.encode(docs, show_progress_bar=True)
    elapsed = time.time() - t0
    emb_cache[model_name] = (model, embeddings)
    return model, embeddings, elapsed, False


def get_reduced_2d(model_name, embeddings):
    # UMAP 2D separata solo per visualize_documents
    if model_name in reduced2d_cache:
        return reduced2d_cache[model_name]

    umap_2d = UMAP(
        n_components=2,
        n_neighbors=15,
        min_dist=0.0,
        metric="cosine",
        random_state=42,
    )
    reduced2d = umap_2d.fit_transform(embeddings)
    reduced2d_cache[model_name] = reduced2d
    return reduced2d


# ============================================================
# 4. PIPELINE BERTopic
# ============================================================
def run_pipeline(config, docs):
    nome = config["nome"]
    print(f"\n{'=' * 70}")
    print(f"Avvio {nome}")
    print(f"{'=' * 70}")

    emb_model, embeddings, t_embedding, cache_hit = get_embeddings(config["embedding_model"], docs)
    if cache_hit:
        print(f"Embedding riusati da cache: {config['embedding_model']}")
    else:
        print(f"Embedding calcolati in {t_embedding:.1f}s con {config['embedding_model']}")

    umap_model = UMAP(**config["umap_params"])
    hdbscan_model = HDBSCAN(**config["hdbscan_params"])

    topic_model = BERTopic(
        embedding_model=emb_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        verbose=False,
    )

    t0 = time.time()
    topics, probs = topic_model.fit_transform(docs, embeddings)
    t_fit = time.time() - t0
    t_total = t_fit + t_embedding

    print(f"BERTopic fit_transform completato in {t_fit:.1f}s")
    print(f"Tempo totale config (embedding + BERTopic): {t_total:.1f}s")

    return {
        "nome": nome,
        "config": config,
        "topic_model": topic_model,
        "topics": topics,
        "probs": probs,
        "embeddings": embeddings,
        "t_embedding": t_embedding,
        "t_fit": t_fit,
        "t_total": t_total,
        "embedding_cache_hit": cache_hit,
    }


# ============================================================
# 5. ANALISI QUANTITATIVA + EXPORT
# ============================================================
def analyze_results(result, docs):
    nome = result["nome"]
    tm = result["topic_model"]

    topic_info = tm.get_topic_info()
    topic_info.to_csv(os.path.join(OUTPUT_DIR, f"{nome}_topic_info.csv"), index=False)

    valid_topics = topic_info[topic_info["Topic"] != -1]
    n_topics = len(valid_topics)

    outlier_row = topic_info[topic_info["Topic"] == -1]
    n_outliers = int(outlier_row["Count"].values[0]) if len(outlier_row) else 0
    pct_outliers = n_outliers / len(docs) * 100

    print(f"\n{'=' * 70}")
    print(f"RISULTATI: {nome}")
    print(f"{'=' * 70}")
    print(f"Numero topic: {n_topics}")
    print(f"Outliers: {n_outliers} ({pct_outliers:.1f}%)")
    print(f"Tempo embedding: {result['t_embedding']:.1f}s (cache_hit={result['embedding_cache_hit']})")
    print(f"Tempo BERTopic fit_transform: {result['t_fit']:.1f}s")
    print(f"Tempo totale: {result['t_total']:.1f}s")

    top10 = valid_topics.nlargest(10, "Count")
    print("\nTop-10 topic per numerosita (top-5 parole):")
    print(f"{'ID':>5} {'Count':>8}  Parole")
    print("-" * 70)
    for _, row in top10.iterrows():
        tid = int(row["Topic"])
        cnt = int(row["Count"])
        words = tm.get_topic(tid)
        top5 = ", ".join([w for w, _ in words[:5]]) if words else "(nessuna)"
        print(f"{tid:>5} {cnt:>8}  {top5}")

    # Artefatti per la relazione
    tm.visualize_barchart(top_n_topics=10).write_html(
        os.path.join(OUTPUT_DIR, f"{nome}_barchart.html")
    )

    return {
        "nome": nome,
        "n_topics": n_topics,
        "n_outliers": n_outliers,
        "pct_outliers": pct_outliers,
        "t_total": result["t_total"],
    }


# ============================================================
# 6. VALIDAZIONE QUALITATIVA (REQ 4)
# ============================================================
def build_abstract_index_map(docs):
    # Mappa semplice abstract -> primo indice, utile per recuperare il titolo.
    idx_map = {}
    for idx, doc in enumerate(docs):
        if doc not in idx_map:
            idx_map[doc] = idx
    return idx_map


def qualitative_validation(result, docs, doc_titles, n_topics=5, docs_per_topic=3):
    tm = result["topic_model"]
    topic_info = tm.get_topic_info()
    valid_topics = topic_info[topic_info["Topic"] != -1].nlargest(n_topics, "Count")
    idx_map = build_abstract_index_map(docs)

    print(f"\n{'=' * 70}")
    print(f"VALIDAZIONE QUALITATIVA: {result['nome']}")
    print(f"Top-{n_topics} topic, {docs_per_topic} documenti rappresentativi per topic")
    print(f"{'=' * 70}")

    rows = []
    for _, row in valid_topics.iterrows():
        tid = int(row["Topic"])
        docs_rep = tm.get_representative_docs(tid)[:docs_per_topic]
        print(f"\nTopic {tid} (Count={int(row['Count'])})")

        for rank, doc_text in enumerate(docs_rep, start=1):
            idx = idx_map.get(doc_text)
            title = doc_titles[idx] if idx is not None else "(titolo non trovato)"
            snippet = doc_text[:220].replace("\n", " ") + ("..." if len(doc_text) > 220 else "")
            print(f"  [{rank}] Titolo: {title}")
            print(f"      Abstract: {snippet}")

            rows.append(
                {
                    "config": result["nome"],
                    "topic": tid,
                    "rank": rank,
                    "title": title,
                    "abstract": doc_text,
                }
            )

    qual_df = pd.DataFrame(rows)
    qual_df.to_csv(
        os.path.join(OUTPUT_DIR, f"{result['nome']}_qualitative_validation.csv"),
        index=False,
    )


# ============================================================
# 7. ESECUZIONE + CONFRONTO FINALE
# ============================================================
results = []
summaries = []

for config in configurations:
    result = run_pipeline(config, abstracts)
    results.append(result)

    summary = analyze_results(result, abstracts)
    summaries.append(summary)

    qualitative_validation(result, abstracts, titles, n_topics=5, docs_per_topic=3)


summary_df = pd.DataFrame(summaries)
summary_df.to_csv(os.path.join(OUTPUT_DIR, "confronto_configurazioni.csv"), index=False)

print(f"\n{'=' * 70}")
print("CONFRONTO FINALE CONFIGURAZIONI")
print(f"{'=' * 70}")
print(f"{'Config':<24} {'#Topic':>7} {'Outliers':>10} {'Tempo(s)':>10}")
print("-" * 70)
for s in summaries:
    print(f"{s['nome']:<24} {s['n_topics']:>7} {s['pct_outliers']:>9.1f}% {s['t_total']:>10.1f}")


# ============================================================
# 8. VISUALIZZAZIONI DOCUMENTI (OPZIONALE)
# Ora corretto: usa riduzione 2D dedicata, non 5D/10D di clustering.
# ============================================================
# result0 = results[0]
# tm = result0["topic_model"]
# emb = result0["embeddings"]
# reduced_2d = get_reduced_2d(result0["config"]["embedding_model"], emb)
# tm.visualize_documents(abstracts, reduced_embeddings=reduced_2d).write_html(
#     os.path.join(OUTPUT_DIR, f"{result0['nome']}_documents_2d.html")
# )
# tm.visualize_hierarchy().write_html(os.path.join(OUTPUT_DIR, f"{result0['nome']}_hierarchy.html"))
# tm.visualize_heatmap().write_html(os.path.join(OUTPUT_DIR, f"{result0['nome']}_heatmap.html"))

print(f"\nArtefatti salvati in: {OUTPUT_DIR}")
