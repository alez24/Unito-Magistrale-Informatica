import itertools
import re
import string

import numpy as np
import pandas as pd
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


# ---------------------------------------------------------------------------
# 2) NLTK RESOURCES + PREPROCESSING
# ---------------------------------------------------------------------------
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
def get_candidates_from_genus(genus):
	if not genus:
		return []

	genus_synsets = wn.synsets(genus, pos=wn.NOUN)
	if not genus_synsets:
		return []

	candidates = []
	for syn in genus_synsets:
		candidates.append(syn)
		# one-level hyponyms (direct descendants) for constrained search
		candidates.extend(syn.hyponyms())

	# de-duplicate while preserving order
	seen = set()
	unique = []
	for syn in candidates:
		if syn.name() not in seen:
			seen.add(syn.name())
			unique.append(syn)
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

# Gold synsets used only for evaluation.
TARGET_SYNSET = {
	"music": "music.n.01",
	"ethics": "ethic.n.01",
	"tree": "tree.n.01",
	"teapot": "teapot.n.01",
}


def evaluate_concept(df, concept, column, scorer):
	rows = []
	target = TARGET_SYNSET[concept]

	definitions = df[column].dropna().tolist()
	for idx, definition in enumerate(definitions, start=1):
		genus = extract_genus(definition)
		candidates = get_candidates_from_genus(genus)
		best, score, status = scorer.score(definition, candidates)

		best_name = best.name() if best else None
		is_correct = (best_name == target)

		rows.append(
			{
				"concept": concept,
				"def_id": idx,
				"definition": definition,
				"genus": genus,
				"n_candidates": len(candidates),
				"pred_synset": best_name,
				"pred_gloss": best.definition() if best else None,
				"target_synset": target,
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
	print(f"Accuracy globale: {acc:.4f}")

	by_concept = (
		results_df.groupby("concept")["is_correct"]
		.mean()
		.sort_index()
	)
	print("\nAccuracy per concetto:")
	for concept, val in by_concept.items():
		print(f"- {concept}: {val:.4f}")

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
