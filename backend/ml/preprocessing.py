"""
Text cleaning & tokenization for resumes and job descriptions.

Kept dependency-light (pure regex + a small stopword list) so the pipeline
works identically whether or not NLTK/spaCy corpora are installed.
"""
import re

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to", "in",
    "on", "at", "for", "with", "as", "by", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its", "from",
    "we", "you", "he", "she", "they", "i", "our", "your", "their", "will",
    "would", "can", "could", "should", "have", "has", "had", "do", "does",
    "did", "not", "no", "yes", "about", "into", "over", "such", "than",
    "there", "here", "who", "whom", "which", "what", "when", "where", "how",
}

# Multi-word / hyphenated technical terms we don't want split incorrectly.
_KEEP_PATTERNS = [
    r"c\+\+", r"c#", r"\.net", r"node\.js", r"react\.js", r"tf-idf",
    r"machine[- ]learning", r"deep[- ]learning",
]

_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_NON_WORD_RE = re.compile(r"[^a-z0-9\+\#\.\s]")
_MULTISPACE_RE = re.compile(r"\s+")


def clean_text(raw_text: str) -> str:
    """Lowercase, strip emails/URLs/special chars, collapse whitespace."""
    if not raw_text:
        return ""
    text = raw_text.lower()
    text = _EMAIL_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _NON_WORD_RE.sub(" ", text)
    text = _MULTISPACE_RE.sub(" ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    cleaned = clean_text(text)
    tokens = [t for t in cleaned.split(" ") if t and t not in STOPWORDS and len(t) > 1]
    return tokens


def preprocess_for_vectorizer(text: str) -> str:
    """Returns a cleaned, stopword-stripped string ready for TfidfVectorizer."""
    return " ".join(tokenize(text))
