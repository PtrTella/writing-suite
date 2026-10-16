"""
Writing Suite - Lexical Diversity & Lemmatized Vocabulary Diagnostic Engine
Calcola l'indice MTLD (Measure of Textual Lexical Diversity, invariante per lunghezza),
la densità semantica e la concentrazione statistica di lemmi tramite lemmatizzatore leggero (WordNet).
Completamente indipendente da liste di parole hardcoded.
"""

from typing import Dict, Any, List
from collections import Counter
from ..stylome import calculate_mtld, calculate_hapax_ratio, calculate_yule_k
from ..cleaner import extract_words

_HAS_LEMMATIZER = False
try:
    from nltk.stem import WordNetLemmatizer
    _LEMMATIZER = WordNetLemmatizer()
    _HAS_LEMMATIZER = True
except Exception:
    _HAS_LEMMATIZER = False


def analyze_lexical_diversity(text: str, words: List[str] = None) -> Dict[str, Any]:
    """Analizza la ricchezza del vocabolario, l'indice MTLD, Hapax Legomena e la concentrazione statistica di lemmi."""
    if words is None:
        words = extract_words(text)

    if not words:
        return {
            "status": "warning",
            "score": 50.0,
            "mtld": 0.0,
            "hapax_ratio": 0.0,
            "yule_k": 100.0,
            "unique_words": 0,
            "ttr": 0.0,
            "overused_tokens": [],
            "signals": ["Nessuna parola valida rilevata."],
            "prescriptions": []
        }

    mtld = calculate_mtld(words)
    hapax_ratio = calculate_hapax_ratio(words)
    yule_k = calculate_yule_k(words)
    total_words = len(words)
    lower_words = [w.lower() for w in words if w.isalpha()]

    # Lemmatizzazione se disponibile (altrimenti fallback su lower_words)
    if _HAS_LEMMATIZER:
        try:
            lemmas = [_LEMMATIZER.lemmatize(w) for w in lower_words]
        except Exception:
            lemmas = lower_words
    else:
        lemmas = lower_words

    unique_lemmas = len(set(lemmas))
    ttr = (unique_lemmas / total_words) if total_words > 0 else 0.0

    # Rilevamento statistico puro di concentrazione lessicale sui lemmi
    content_lemma_counts = Counter(l for l in lemmas if len(l) >= 5)
    overused_tokens = [
        f"'{l}' ({c}x)"
        for l, c in content_lemma_counts.most_common(4)
        if c >= 3 or (total_words <= 70 and c >= 2 and len(l) >= 6)
    ]

    signals = []
    prescriptions = []

    # 1. Valutazione MTLD
    if mtld >= 85.0:
        status = "safe"
        score = 15.0
    elif mtld >= 55.0:
        status = "warning"
        score = 45.0
        signals.append(f"Diversità lessicale moderata (MTLD = {mtld:.1f}, target naturale > 80.0).")
        prescriptions.append("Espandi il vocabolario tecnico: evita di riutilizzare gli stessi sostantivi o aggettivi nel medesimo paragrafo.")
    else:
        status = "critical"
        score = 80.0
        signals.append(f"Povertà lessicale statistica (MTLD = {mtld:.1f}). Concentrazione anomala di lemmi identici.")
        prescriptions.append("Vocabolario ristretto: sostituisci le parole ripetute con terminologia scientifica precisa o sinonimi di registro superiore.")

    # 2. Valutazione Coda di Zipf (Hapax Legomena Ratio V1 / N)
    if total_words >= 35:
        if hapax_ratio < 0.85:
            if status != "critical":
                status = "warning"
                score = max(score, 50.0)
            signals.append(f"Coda di Zipf compressa (Hapax Ratio = {hapax_ratio:.1%}, atteso > 90%): troncamento tipico di campionamento generativo.")
            prescriptions.append("Arricchisci la coda lessicale: sostituisci termini generici ripetuti con lemmi tecnici puntuali usati una sola volta.")
        elif hapax_ratio >= 0.94:
            score = max(5.0, score - 10.0)

    # 3. Lemmi overused
    if overused_tokens:
        signals.append(f"Lemmi con concentrazione statistica anomala: {', '.join(overused_tokens)}.")
        prescriptions.append(f"Elimina le ripetizioni ravvicinate di {', '.join(overused_tokens)} variando i termini d'azione.")

    return {
        "status": status,
        "score": score,
        "mtld": round(mtld, 1),
        "hapax_ratio": round(hapax_ratio, 3),
        "yule_k": round(yule_k, 1),
        "total_words": total_words,
        "unique_words": unique_lemmas,
        "ttr": round(ttr, 3),
        "overused_tokens": overused_tokens,
        "signals": signals,
        "prescriptions": prescriptions
    }
