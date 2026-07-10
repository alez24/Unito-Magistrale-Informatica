import itertools
import re
import string

import numpy as np
import pandas as pd
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords, wordnet as wn
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
	from sentence_transformers import SentenceTransformer
	_HAS_SBERT = True
except Exception:
	_HAS_SBERT = False


# ---------------------------------------------------------------------------
# 1) CONFIG
# ---------------------------------------------------------------------------
DATASET_PATH = "Dataset definizioni-spurio.csv"
OUTPUT_PATH = "risultati_lab2_wordnet_genus.csv"

# Use SBERT when available, otherwise fallback to TF-IDF.
SIMILARITY_BACKEND = "sbert" if _HAS_SBERT else "tfidf"
SBERT_MODEL_NAME = "all-MiniLM-L6-v2"

GENUS_DEPTH = 3           # livelli di iponimi scesi dal genus (1 lascia irraggiungibili molti target)
MAX_CANDIDATES = 300      # cap: un genus troppo generico (es. "object") farebbe esplodere i candidati


# ---------------------------------------------------------------------------
# 2) NLTK RESOURCES + PREPROCESSING
# ---------------------------------------------------------------------------
RESOURCES = {
	"corpora/stopwords": "stopwords",
	"corpora/wordnet": "wordnet",
	"corpora/omw-1.4": "omw-1.4",
	"taggers/averaged_perceptron_tagger_eng": "averaged_perceptron_tagger_eng",
	"tokenizers/punkt_tab": "punkt_tab",
}

for resource_path, resource_name in RESOURCES.items():
	try:
		nltk.data.find(resource_path)
	except LookupError:
		nltk.download(resource_name)

STOPWORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


def _wordnet_pos(treebank_pos):
	if treebank_pos.startswith("J"):
		return wn.ADJ
	if treebank_pos.startswith("V"):
		return wn.VERB
	if treebank_pos.startswith("N"):
		return wn.NOUN
	if treebank_pos.startswith("R"):
		return wn.ADV
	return wn.NOUN


def clean_text(text):
	if not isinstance(text, str):
		return ""

	text = text.lower()
	text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
	tokens = [tok for tok in text.split() if tok.isalpha() and len(tok) > 2 and tok not in STOPWORDS]

	if not tokens:
		return ""

	tagged = pos_tag(tokens)
	lemmas = [LEMMATIZER.lemmatize(tok, _wordnet_pos(pos)) for tok, pos in tagged]
	return " ".join(lemmas)


# ---------------------------------------------------------------------------
# 3) GENUS EXTRACTION
# ---------------------------------------------------------------------------
def extract_genus(definition):
	if not isinstance(definition, str):
		return None

	# Rule 1: noun immediately after copula ("is/are")
	m = re.search(r"\b(?:is|are)\b\s+(?:an?\s+)?([a-zA-Z-]+)", definition.lower())
	if m:
		candidate = m.group(1)
		if wn.synsets(candidate, pos=wn.NOUN):
			return candidate

	# Rule 2: first noun in the definition
	tokens = [t for t in word_tokenize(definition.lower()) if t.isalpha()]
	if not tokens:
		return None

	tagged = pos_tag(tokens)
	for tok, pos in tagged:
		if pos.startswith("NN") and wn.synsets(tok, pos=wn.NOUN):
			return tok

	return None


# ---------------------------------------------------------------------------
# 4) WORDNET CANDIDATE RETRIEVAL (GENUS PRINCIPLE)
# ---------------------------------------------------------------------------
def get_candidates_from_genus(genus, depth=GENUS_DEPTH, max_candidates=MAX_CANDIDATES):
	if not genus:
		return []

	genus_synsets = wn.synsets(genus, pos=wn.NOUN)
	if not genus_synsets:
		return []

	# con un solo livello di iponimi molti target sono strutturalmente irraggiungibili
	# (es. "teapot" e' tre livelli sotto il genus "container": teapot < pot < vessel < container).
	# Si scende fino a `depth` livelli, con uscita anticipata al raggiungimento del cap:
	# un genus troppo generico (es. "object") avrebbe altrimenti una closure enorme.
	seen = set()
	unique = []

	def add(syn):
		if syn.name() not in seen:
			seen.add(syn.name())
			unique.append(syn)

	for syn in genus_synsets:
		add(syn)
		if len(unique) >= max_candidates:
			break
		for hypo in syn.closure(lambda s: s.hyponyms(), depth=depth):
			add(hypo)
			if len(unique) >= max_candidates:
				break
		if len(unique) >= max_candidates:
			break

	return unique


# ---------------------------------------------------------------------------
# 5) SIMILARITY
# ---------------------------------------------------------------------------
class SimilarityScorer:
	def __init__(self, backend="tfidf", sbert_model_name="all-MiniLM-L6-v2"):
		self.backend = backend
		self.sbert_model_name = sbert_model_name
		self.model = None
		if self.backend == "sbert":
			self.model = SentenceTransformer(self.sbert_model_name)

	def score(self, definition, candidates):
		if not candidates:
			return None, 0.0, "no_candidates"

		def_clean = clean_text(definition)
		if not def_clean:
			return None, 0.0, "empty_definition"

		glosses = [clean_text(s.definition()) for s in candidates]
		if not any(glosses):
			return None, 0.0, "empty_glosses"

		try:
			if self.backend == "sbert":
				corpus = [def_clean] + glosses
				embs = self.model.encode(corpus)
				sims = cosine_similarity([embs[0]], embs[1:])[0]
			else:
				corpus = [def_clean] + glosses
				tfidf = TfidfVectorizer()
				mat = tfidf.fit_transform(corpus)
				sims = cosine_similarity(mat[0:1], mat[1:])[0]

			max_val = float(np.max(sims))
			winners = np.where(sims == max_val)[0]
			if len(winners) != 1:
				return None, max_val, "tie"

			best = candidates[int(winners[0])]
			return best, max_val, "ok"

		except Exception:
			return None, 0.0, "scoring_error"


# ---------------------------------------------------------------------------
# 6) DATASET MAPPING + GOLD LABELS
# ---------------------------------------------------------------------------
COLUMN_MAP = {
	"music": "(AG) Definizione del concetto ASTRATTO e GENERICO",
	"ethics": "(AS) Definizione del concetto ASTRATTO e SPECIFICO",
	"tree": "(CG) Definizione del concetto CONCRETO e GENERICO",
	"teapot": "(CS) Definizione del concetto CONCRETO e SPECIFICO",
}

# Gold synsets used only for evaluation. Piu' di un synset accettabile per "ethics":
# le definizioni dei compagni oscillano tra "principi di giusto/sbagliato di un gruppo"
# (ethic.n.01) e "studio filosofico dei valori morali" (ethics.n.01/morality.n.01),
# ed entrambe le letture sono legittime a seconda di come e' stata scritta la definizione.
TARGET_SYNSETS = {
	"music": {"music.n.01"},
	"ethics": {"ethic.n.01", "ethics.n.01", "morality.n.01"},
	"tree": {"tree.n.01"},
	"teapot": {"teapot.n.01"},
}


def evaluate_concept(df, concept, column, scorer):
	rows = []
	target = TARGET_SYNSETS[concept]

	definitions = df[column].dropna().tolist()
	for idx, definition in enumerate(definitions, start=1):
		genus = extract_genus(definition)
		candidates = get_candidates_from_genus(genus)
		best, score, status = scorer.score(definition, candidates)

		best_name = best.name() if best else None
		is_correct = best_name in target if best_name else False
		# diagnostica: il target era anche solo raggiungibile tra i candidati?
		# separa il fallimento di retrieval (target assente) da quello di ranking
		# (target presente ma non vincente)
		target_reachable = any(c.name() in target for c in candidates)

		rows.append(
			{
				"concept": concept,
				"def_id": idx,
				"definition": definition,
				"genus": genus,
				"n_candidates": len(candidates),
				"pred_synset": best_name,
				"pred_gloss": best.definition() if best else None,
				"target_synset": "/".join(sorted(target)),
				"target_reachable": bool(target_reachable),
				"score": round(float(score), 6),
				"status": status,
				"is_correct": bool(is_correct),
			}
		)

	return rows


def print_summary(results_df):
	print("\n" + "=" * 78)
	print("LAB-2 | Content-to-Form con WordNet reale (genus + iponimi)")
	print(f"Backend similarita: {SIMILARITY_BACKEND}")
	print("=" * 78)

	# Accuracy includes failures/ties as wrong: no inflated fallback.
	acc = results_df["is_correct"].mean() if len(results_df) else 0.0
	# scompone l'errore in due fasi distinte: retrieval (il target non era neanche
	# tra i candidati) vs ranking (era tra i candidati ma non ha vinto la similarita')
	coverage = results_df["target_reachable"].mean() if len(results_df) else 0.0
	reachable_df = results_df[results_df["target_reachable"]]
	acc_given_reachable = reachable_df["is_correct"].mean() if len(reachable_df) else float("nan")

	print(f"Accuracy globale: {acc:.4f}")
	print(f"Coverage (target raggiungibile tra i candidati): {coverage:.4f}")
	print(f"Accuracy condizionata alla raggiungibilita' (solo dove il target era tra i candidati): {acc_given_reachable:.4f}")

	by_concept = results_df.groupby("concept").agg(
		accuracy=("is_correct", "mean"),
		coverage=("target_reachable", "mean"),
	).sort_index()
	print("\nAccuracy / coverage per concetto:")
	for concept, row in by_concept.iterrows():
		print(f"- {concept}: accuracy={row['accuracy']:.4f}  coverage={row['coverage']:.4f}")

	print("\nDistribuzione status:")
	status_counts = results_df["status"].value_counts(dropna=False)
	for status, cnt in status_counts.items():
		print(f"- {status}: {cnt}")


def main():
	df = pd.read_csv(DATASET_PATH)

	scorer = SimilarityScorer(
		backend=SIMILARITY_BACKEND,
		sbert_model_name=SBERT_MODEL_NAME,
	)

	all_rows = []
	for concept, column in COLUMN_MAP.items():
		if column not in df.columns:
			raise KeyError(f"Colonna mancante nel dataset: {column}")
		concept_rows = evaluate_concept(df, concept, column, scorer)
		all_rows.extend(concept_rows)

	results_df = pd.DataFrame(all_rows)
	results_df.to_csv(OUTPUT_PATH, index=False)

	print_summary(results_df)
	print(f"\nRisultati dettagliati salvati in: {OUTPUT_PATH}")


if __name__ == "__main__":
	main()
