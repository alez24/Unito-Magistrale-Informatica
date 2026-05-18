# ============================================================
# LAB-4 — Topic Modeling con BERTopic
# TLN 2025/2026 - Prof. Luigi Di Caro / Prof. Radicioni
# ============================================================

# ============================================================
# 0. INSTALLAZIONE DIPENDENZE
# ============================================================
# Esegui questo blocco una volta sola (su Colab o terminale):
#
# pip install bertopic sentence-transformers umap-learn hdbscan datasets

# ============================================================
# 1. IMPORT
# ============================================================
import time
import warnings
warnings.filterwarnings("ignore")

from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic


# ============================================================
# 2. CARICAMENTO DATASET
# ============================================================
print("Caricamento dataset ArXiv NLP...")
dataset = load_dataset("MaartenGr/arxiv_nlp", split="train")
abstracts = dataset["Abstracts"]
print(f"Numero abstract caricati: {len(abstracts)}")

# (Opzionale) Subset per test rapido — commenta per usare tutto il dataset
# abstracts = abstracts[:5000]


# ============================================================
# 3. CONFIGURAZIONI DA TESTARE
# ============================================================
# Definiamo 3 configurazioni con parametri diversi.
# Ogni configurazione è un dizionario con:
#   - nome           : etichetta per i log
#   - embedding_model: modello SentenceTransformer
#   - umap_params    : dizionario parametri UMAP
#   - hdbscan_params : dizionario parametri HDBSCAN

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
        "nome": "Config_2_minilm_fine",
        "embedding_model": "all-MiniLM-L6-v2",
        "umap_params": {
            "n_components": 10,
            "n_neighbors": 10,
            "min_dist": 0.0,
            "metric": "cosine",
            "random_state": 42,
        },
        "hdbscan_params": {
            "min_cluster_size": 30,
            "metric": "euclidean",
            "cluster_selection_method": "eom",
        },
    },
    {
        "nome": "Config_3_minilm_coarse",
        "embedding_model": "all-MiniLM-L6-v2",
        "umap_params": {
            "n_components": 5,
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
# 4. FUNZIONE PIPELINE
# ============================================================
def run_pipeline(config, abstracts):
    """
    Esegue la pipeline completa BERTopic per una configurazione.
    Restituisce il topic_model, i topic, le probabilità e i
    reduced_embeddings per la visualizzazione.
    """
    nome = config["nome"]
    print(f"\n{'='*60}")
    print(f"  Avvio: {nome}")
    print(f"{'='*60}")

    # --- Embedding ---
    print(f"[1/4] Embedding con '{config['embedding_model']}'...")
    t0 = time.time()
    emb_model = SentenceTransformer(config["embedding_model"])
    embeddings = emb_model.encode(abstracts, show_progress_bar=True)
    t_emb = time.time() - t0
    print(f"      Completato in {t_emb:.1f}s — shape: {embeddings.shape}")

    # --- UMAP ---
    print(f"[2/4] Riduzione dimensionalità con UMAP...")
    t1 = time.time()
    umap_model = UMAP(**config["umap_params"])
    reduced = umap_model.fit_transform(embeddings)
    t_umap = time.time() - t1
    print(f"      Completato in {t_umap:.1f}s — shape: {reduced.shape}")

    # --- HDBSCAN ---
    print(f"[3/4] Clustering con HDBSCAN...")
    t2 = time.time()
    hdbscan_model = HDBSCAN(**config["hdbscan_params"])
    clusters = hdbscan_model.fit_predict(reduced)
    t_hdbscan = time.time() - t2
    n_clusters_raw = len(set(clusters)) - (1 if -1 in clusters else 0)
    n_outliers = (clusters == -1).sum()
    pct_outliers = n_outliers / len(clusters) * 100
    print(f"      Completato in {t_hdbscan:.1f}s")
    print(f"      Cluster trovati (raw): {n_clusters_raw}")
    print(f"      Outliers: {n_outliers} ({pct_outliers:.1f}%)")

    # --- BERTopic ---
    print(f"[4/4] Fit BERTopic...")
    t3 = time.time()
    topic_model = BERTopic(
        embedding_model=emb_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        verbose=False,
    )
    topics, probs = topic_model.fit_transform(abstracts, embeddings)
    t_bert = time.time() - t3

    t_total = time.time() - t0
    print(f"      Completato in {t_bert:.1f}s")
    print(f"  Tempo totale: {t_total:.1f}s")

    return {
        "nome": nome,
        "topic_model": topic_model,
        "topics": topics,
        "probs": probs,
        "reduced": reduced,
        "embeddings": embeddings,
        "t_embedding": t_emb,
        "t_umap": t_umap,
        "t_hdbscan": t_hdbscan,
        "t_total": t_total,
    }


# ============================================================
# 5. FUNZIONE ANALISI OUTPUT
# ============================================================
def analyze_results(result, abstracts):
    """
    Stampa le metriche richieste dal lab per una configurazione.
    """
    nome = result["nome"]
    tm = result["topic_model"]

    topic_info = tm.get_topic_info()

    # Escludi topic -1 (outliers)
    valid_topics = topic_info[topic_info["Topic"] != -1]
    n_topics = len(valid_topics)

    # Outlier count
    outlier_row = topic_info[topic_info["Topic"] == -1]
    n_outliers = int(outlier_row["Count"].values[0]) if len(outlier_row) > 0 else 0
    pct_outliers = n_outliers / len(abstracts) * 100

    print(f"\n{'='*60}")
    print(f"  RISULTATI: {nome}")
    print(f"{'='*60}")
    print(f"  Numero topic:        {n_topics}")
    print(f"  Outliers:            {n_outliers} ({pct_outliers:.1f}%)")
    print(f"  Tempo totale:        {result['t_total']:.1f}s")
    print(f"    - Embedding:       {result['t_embedding']:.1f}s")
    print(f"    - UMAP:            {result['t_umap']:.1f}s")
    print(f"    - HDBSCAN:         {result['t_hdbscan']:.1f}s")

    # Top-10 topic per popolarità → top-5 parole ciascuno
    top10 = valid_topics.nlargest(10, "Count")
    print(f"\n  Top-10 topic (per numero documenti) — Top-5 parole:")
    print(f"  {'ID':>4}  {'Count':>6}  Parole")
    print(f"  {'-'*50}")
    for _, row in top10.iterrows():
        tid = row["Topic"]
        count = row["Count"]
        words = tm.get_topic(tid)
        if words:
            top5 = ", ".join([w for w, _ in words[:5]])
        else:
            top5 = "(nessuna)"
        print(f"  {tid:>4}  {count:>6}  {top5}")

    return {
        "nome": nome,
        "n_topics": n_topics,
        "n_outliers": n_outliers,
        "pct_outliers": pct_outliers,
        "t_total": result["t_total"],
    }


# ============================================================
# 6. ESECUZIONE
# ============================================================
results = []
summaries = []

for config in configurations:
    result = run_pipeline(config, abstracts)
    results.append(result)
    summary = analyze_results(result, abstracts)
    summaries.append(summary)


# ============================================================
# 7. TABELLA COMPARATIVA
# ============================================================
print(f"\n{'='*60}")
print("  CONFRONTO FINALE TRA CONFIGURAZIONI")
print(f"{'='*60}")
print(f"  {'Config':<28} {'#Topic':>6}  {'Outliers':>8}  {'Tempo(s)':>8}")
print(f"  {'-'*56}")
for s in summaries:
    print(
        f"  {s['nome']:<28} {s['n_topics']:>6}  "
        f"{s['pct_outliers']:>7.1f}%  {s['t_total']:>8.1f}"
    )


# ============================================================
# 8. VISUALIZZAZIONI (opzionale — funziona su Jupyter/Colab)
# ============================================================
# Decommentare le righe che si vogliono usare.
# Sostituire 0/1/2 con l'indice della configurazione desiderata.

# tm = results[0]["topic_model"]
# reduced = results[0]["reduced"]

# Barchart top-N parole per topic
# tm.visualize_barchart().show()

# Mappa documenti nello spazio 2D
# tm.visualize_documents(abstracts, reduced_embeddings=reduced).show()

# Gerarchia tra topic
# tm.visualize_hierarchy().show()

# Heatmap similarità tra topic
# tm.visualize_heatmap().show()


# ============================================================
# 9. DOCUMENTI RAPPRESENTATIVI (esempio per topic 4)
# ============================================================
# print(results[0]["topic_model"].get_representative_docs(4))
