import warnings

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import seaborn as sns
from nltk.corpus import wordnet as wn
from scipy.stats import entropy as scipy_entropy

warnings.filterwarnings("ignore")

nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

# ─────────────────────────────────────────────
# CONFIGURAZIONE
# ─────────────────────────────────────────────

# (inglese, italiano, spagnolo, categoria)
# Nota: table -> mesa per allineare il senso "tavolo" (non "tabla" = asse/tabella)
LEMMI = [
    ("bank", "banca", "banco", "sostantivo"),
    ("hand", "mano", "mano", "sostantivo"),
    ("head", "testa", "cabeza", "sostantivo"),
    ("line", "linea", "linea", "sostantivo"),
    ("key", "chiave", "llave", "sostantivo"),
    ("table", "tavolo", "mesa", "sostantivo"),
    ("mouth", "bocca", "boca", "sostantivo"),
    ("foot", "piede", "pie", "sostantivo"),
    ("run", "correre", "correr", "verbo"),
    ("give", "dare", "dar", "verbo"),
    ("take", "prendere", "tomar", "verbo"),
    ("see", "vedere", "ver", "verbo"),
    ("break", "rompere", "romper", "verbo"),
    ("turn", "girare", "girar", "verbo"),
    ("light", "leggero", "ligero", "aggettivo"),
    ("hard", "duro", "duro", "aggettivo"),
    ("free", "libero", "libre", "aggettivo"),
    ("right", "giusto", "correcto", "aggettivo"),
    ("open", "aperto", "abierto", "aggettivo"),
    ("deep", "profondo", "profundo", "aggettivo"),
]

LINGUE = {"eng": "Inglese", "ita": "Italiano", "spa": "Spagnolo"}
POS_MAP = {
    "sostantivo": wn.NOUN,
    "verbo": wn.VERB,
    "aggettivo": wn.ADJ,
}

plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.size"] = 11
sns.set_style("whitegrid")


# ─────────────────────────────────────────────
# 1. ESTRAZIONE E METRICHE
# ─────────────────────────────────────────────

def english_sense_counts(lemma_en, synsets):
    """
    Per EN usa i count di WordNet/SemCor: per ogni synset,
    somma i count dei lemmi che matchano il lemma target.
    """
    target = lemma_en.lower().replace(" ", "_")
    counts = []
    for syn in synsets:
        c = sum(l.count() for l in syn.lemmas() if l.name().lower() == target)
        counts.append(c)
    return counts


def calcola_metriche(synsets, lemma, lang_code):
    """
    EN: entropia reale da frequenze SemCor (lemma.count).
    IT/ES: OMW non fornisce frequenze robuste -> distribuzione uniforme.
    """
    n = len(synsets)
    if n <= 1:
        return {
            "n_sensi": n,
            "entropia": 0.0,
            "top1_share": 1.0,
            "metodo_entropia": "degenerate",
        }

    if lang_code == "eng":
        counts = np.array(english_sense_counts(lemma, synsets), dtype=float)
        if counts.sum() > 0:
            dist = counts / counts.sum()
            ent = float(scipy_entropy(dist, base=2))
            top1 = float(dist.max())
            return {
                "n_sensi": n,
                "entropia": round(ent, 4),
                "top1_share": round(top1, 4),
                "metodo_entropia": "real_semcor",
            }

    dist = np.ones(n) / n
    ent = float(scipy_entropy(dist, base=2))
    return {
        "n_sensi": n,
        "entropia": round(ent, 4),
        "top1_share": round(1 / n, 4),
        "metodo_entropia": "uniform_fallback",
    }


def costruisci_dataframe():
    righe = []
    for lemma_en, lemma_it, lemma_es, categoria in LEMMI:
        lemmi_per_lingua = {"eng": lemma_en, "ita": lemma_it, "spa": lemma_es}
        wn_pos = POS_MAP[categoria]
        for lang_code, lang_nome in LINGUE.items():
            lemma = lemmi_per_lingua[lang_code]
            synsets = wn.synsets(lemma, pos=wn_pos, lang=lang_code)
            metriche = calcola_metriche(synsets, lemma, lang_code)
            righe.append(
                {
                    "lemma_en": lemma_en,
                    "lemma": lemma,
                    "lingua": lang_nome,
                    "lingua_code": lang_code,
                    "categoria": categoria,
                    "wn_pos": wn_pos,
                    **metriche,
                }
            )
    return pd.DataFrame(righe)


# ─────────────────────────────────────────────
# 2. STATISTICHE DESCRITTIVE
# ─────────────────────────────────────────────

def stampa_statistiche(df):
    print("\n" + "=" * 55)
    print("STATISTICHE DESCRITTIVE PER LINGUA")
    print("=" * 55)
    stats = (
        df.groupby("lingua")
        .agg(
            media_sensi=("n_sensi", "mean"),
            mediana_sensi=("n_sensi", "median"),
            max_sensi=("n_sensi", "max"),
            media_entropia=("entropia", "mean"),
            media_top1=("top1_share", "mean"),
            monosemici=("n_sensi", lambda x: (x <= 1).sum()),
        )
        .round(3)
    )
    stats = stats.reindex(["Inglese", "Italiano", "Spagnolo"])
    print(stats.to_string())


def stampa_asimmetrie(pivot):
    print("\n" + "=" * 55)
    print("TOP 10 ASIMMETRIE CROSS-LINGUISTICHE")
    print("=" * 55)
    top = pivot.sort_values("asimmetria", ascending=False).head(10)
    print(
        top[
            ["Inglese", "Italiano", "Spagnolo", "asimmetria", "ratio_en_it", "ratio_en_es"]
        ].to_string()
    )

    print("\n" + "=" * 55)
    print("LEMMI CON BASSA ASIMMETRIA (comportamento simile)")
    print("=" * 55)
    bottom = pivot.sort_values("asimmetria", ascending=True).head(5)
    print(bottom[["Inglese", "Italiano", "Spagnolo", "asimmetria"]].to_string())


def mostra_sensi(lemma_en, lemma_it, lemma_es, categoria, n_max=4):
    """Stampa i primi N sensi per ciascuna lingua con filtro POS."""
    lemmi_map = {"eng": lemma_en, "ita": lemma_it, "spa": lemma_es}
    nomi_map = {"eng": "Inglese", "ita": "Italiano", "spa": "Spagnolo"}
    wn_pos = POS_MAP[categoria]

    print(f"\n{'=' * 60}")
    print(f"LEMMA: {lemma_en.upper()} / {lemma_it} / {lemma_es} [{categoria}]")
    print(f"{'=' * 60}")
    for lang, nome in nomi_map.items():
        syns = wn.synsets(lemmi_map[lang], pos=wn_pos, lang=lang)
        print(f"\n  [{nome}] — {len(syns)} sensi")
        for i, syn in enumerate(syns[:n_max]):
            gloss = syn.definition()[:80] + ("..." if len(syn.definition()) > 80 else "")
            print(f"    {i + 1}. [{syn.name()}] {gloss}")
        if len(syns) > n_max:
            print(f"    ... e altri {len(syns) - n_max} sensi")


def stampa_limiti_metodologici(df):
    print("\n" + "=" * 55)
    print("NOTE METODOLOGICHE")
    print("=" * 55)
    print("- Entropia EN calcolata con frequenze SemCor (lemma.count) quando disponibili.")
    print("- Entropia IT/ES: fallback uniforme, per limite dati frequenziali in OMW.")
    print("- Lemmi cross-linguistici allineati manualmente (es. table->mesa).")
    print("- Parte dell'asimmetria residua puo dipendere da disallineamento traduttivo, non solo da polisemia.")

    print("\nDistribuzione metodo entropia per lingua:")
    tab = df.groupby(["lingua", "metodo_entropia"]).size().rename("n").reset_index()
    print(tab.to_string(index=False))


# ─────────────────────────────────────────────
# 3. GRAFICI
# ─────────────────────────────────────────────

COLORI_LINGUA = {"Inglese": "#2196F3", "Italiano": "#4CAF50", "Spagnolo": "#FF5722"}
COLORI_CAT = {"sostantivo": "#E91E63", "verbo": "#9C27B0", "aggettivo": "#FF9800"}


def plot_heatmap(df):
    pivot = df.pivot_table(index="lemma_en", columns="lingua", values="n_sensi")
    pivot = pivot.reindex(columns=["Inglese", "Italiano", "Spagnolo"])
    pivot = pivot.sort_values("Inglese", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".0f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": "Numero di sensi"},
    )
    ax.set_title("Numero di Sensi per Lemma e Lingua", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Lingua")
    ax.set_ylabel("Lemma (EN)")
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)
    plt.tight_layout()
    plt.savefig("heatmap_sensi.png", bbox_inches="tight")
    plt.close(fig)
    print("Salvato: heatmap_sensi.png")


def plot_barplot_entropia(df):
    pivot_idx = df.pivot_table(index="lemma_en", columns="lingua", values="n_sensi")
    pivot_idx = pivot_idx.reindex(columns=["Inglese", "Italiano", "Spagnolo"])
    lemmi_ord = pivot_idx.sort_values("Inglese", ascending=False).index.tolist()

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(lemmi_ord))
    width = 0.28

    for i, (lingua, colore) in enumerate(COLORI_LINGUA.items()):
        valori = (
            df[df["lingua"] == lingua]
            .set_index("lemma_en")
            .reindex(lemmi_ord)["entropia"]
            .values
        )
        ax.bar(
            x + (i - 1) * width,
            valori,
            width,
            label=lingua,
            color=colore,
            alpha=0.85,
            edgecolor="white",
        )

    ax.set_xlabel("Lemma")
    ax.set_ylabel("Entropia di Shannon (bit)")
    ax.set_title("Entropia Polisemica per Lemma e Lingua", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(lemmi_ord, rotation=45, ha="right")
    ax.legend(title="Lingua")
    ax.grid(axis="y", alpha=0.4)
    plt.tight_layout()
    plt.savefig("barplot_entropia.png", bbox_inches="tight")
    plt.close(fig)
    print("Salvato: barplot_entropia.png")


def plot_scatter_asimmetria(df):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    en_data = df[df["lingua"] == "Inglese"].set_index("lemma_en")

    for ax, lingua2, titolo in zip(
        axes,
        ["Italiano", "Spagnolo"],
        ["EN vs IT", "EN vs ES"],
    ):
        l2 = df[df["lingua"] == lingua2].set_index("lemma_en")
        comuni = en_data.index.intersection(l2.index)
        for lemma in comuni:
            x_val = en_data.loc[lemma, "n_sensi"]
            y_val = l2.loc[lemma, "n_sensi"]
            cat = en_data.loc[lemma, "categoria"]
            ax.scatter(x_val, y_val, color=COLORI_CAT.get(cat, "gray"), s=80, zorder=3)
            ax.annotate(
                lemma,
                (x_val, y_val),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
                alpha=0.8,
            )
        max_val = max(en_data.loc[comuni, "n_sensi"].max(), l2.loc[comuni, "n_sensi"].max()) + 2
        ax.plot([0, max_val], [0, max_val], "k--", alpha=0.3, label="parita")
        ax.set_xlabel("N sensi Inglese")
        ax.set_ylabel(f"N sensi {lingua2}")
        ax.set_title(titolo, fontsize=13, fontweight="bold")
        ax.legend(["parita EN=L2"], fontsize=9)
        ax.grid(alpha=0.3)

    patches = [mpatches.Patch(color=c, label=l) for l, c in COLORI_CAT.items()]
    fig.legend(handles=patches, title="Categoria", loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.08), fontsize=10)
    plt.suptitle("Asimmetria Polisemica: Inglese vs Lingue Romanze", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig("scatter_asimmetria.png", bbox_inches="tight")
    plt.close(fig)
    print("Salvato: scatter_asimmetria.png")


def plot_boxplot(df):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    sns.boxplot(
        data=df,
        x="lingua",
        y="n_sensi",
        order=["Inglese", "Italiano", "Spagnolo"],
        palette=list(COLORI_LINGUA.values()),
        ax=axes[0],
        width=0.5,
    )
    axes[0].set_title("Distribuzione N sensi per Lingua", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("Lingua")
    axes[0].set_ylabel("N sensi")

    sns.boxplot(
        data=df,
        x="categoria",
        y="n_sensi",
        hue="lingua",
        hue_order=["Inglese", "Italiano", "Spagnolo"],
        palette=list(COLORI_LINGUA.values()),
        ax=axes[1],
        width=0.6,
    )
    axes[1].set_title("N sensi per Categoria e Lingua", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("Categoria grammaticale")
    axes[1].set_ylabel("N sensi")
    axes[1].legend(title="Lingua", fontsize=9)

    plt.tight_layout()
    plt.savefig("boxplot_distribuzione.png", bbox_inches="tight")
    plt.close(fig)
    print("Salvato: boxplot_distribuzione.png")


def plot_asimmetrie(pivot):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    ratio_df = pivot[["ratio_en_it", "ratio_en_es"]].dropna().sort_values("ratio_en_it", ascending=False)
    x = np.arange(len(ratio_df))
    ax.bar(x - 0.2, ratio_df["ratio_en_it"], 0.35, label="EN/IT", color="#4CAF50", alpha=0.85)
    ax.bar(x + 0.2, ratio_df["ratio_en_es"], 0.35, label="EN/ES", color="#FF5722", alpha=0.85)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, alpha=0.5, label="parita")
    ax.set_xticks(x)
    ax.set_xticklabels(ratio_df.index, rotation=45, ha="right")
    ax.set_ylabel("Ratio EN/altra lingua")
    ax.set_title("Rapporto N sensi EN vs Lingue Romanze", fontsize=12, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    ax2 = axes[1]
    top8 = pivot.sort_values("asimmetria", ascending=False).head(8)
    x2 = np.arange(len(top8))
    ax2.bar(x2 - 0.25, top8["Inglese"], 0.25, label="Inglese", color="#2196F3", alpha=0.85)
    ax2.bar(x2, top8["Italiano"], 0.25, label="Italiano", color="#4CAF50", alpha=0.85)
    ax2.bar(x2 + 0.25, top8["Spagnolo"], 0.25, label="Spagnolo", color="#FF5722", alpha=0.85)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(top8.index, rotation=45, ha="right")
    ax2.set_ylabel("N sensi")
    ax2.set_title("Top 8 Lemmi per Asimmetria Cross-Linguistica", fontsize=12, fontweight="bold")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("asimmetrie.png", bbox_inches="tight")
    plt.close(fig)
    print("Salvato: asimmetrie.png")


# ─────────────────────────────────────────────
# 4. MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("Estrazione sensi da Open Multilingual WordNet con filtro POS...")
    df = costruisci_dataframe()
    print(f"Record estratti: {len(df)} ({len(LEMMI)} lemmi x {len(LINGUE)} lingue)")

    stampa_statistiche(df)
    stampa_limiti_metodologici(df)

    pivot = df.pivot_table(index="lemma_en", columns="lingua", values="n_sensi").fillna(0)
    pivot = pivot.reindex(columns=["Inglese", "Italiano", "Spagnolo"])
    pivot["asimmetria"] = pivot.max(axis=1) - pivot.min(axis=1)
    pivot["ratio_en_it"] = (pivot["Inglese"] / pivot["Italiano"].replace(0, np.nan)).round(2)
    pivot["ratio_en_es"] = (pivot["Inglese"] / pivot["Spagnolo"].replace(0, np.nan)).round(2)
    stampa_asimmetrie(pivot)

    print("\n\nANALISI QUALITATIVA DEI CASI PIU ASIMMETRICI")
    for en, it, es, cat in [
        ("bank", "banca", "banco", "sostantivo"),
        ("line", "linea", "linea", "sostantivo"),
        ("break", "rompere", "romper", "verbo"),
        ("run", "correre", "correr", "verbo"),
    ]:
        mostra_sensi(en, it, es, cat)

    print("\n\nGenerazione grafici...")
    plot_heatmap(df)
    plot_barplot_entropia(df)
    plot_scatter_asimmetria(df)
    plot_boxplot(df)
    plot_asimmetrie(pivot)

    df.to_csv("risultati_polisemia.csv", index=False)
    pivot.to_csv("asimmetrie.csv")
    print("\nFile CSV esportati: risultati_polisemia.csv, asimmetrie.csv")
    print("\nDone.")
