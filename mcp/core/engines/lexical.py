"""
Writing Suite - Lexical Diversity & Vocabulary Richness Diagnostic Engine
Calcola l'indice MTLD (Measure of Textual Lexical Diversity, invariante per lunghezza),
la densità semantica e la frequenza di lemmi ripetitivi astratti.
"""

from typing import Dict, Any, List
from collections import Counter
from ..stylome import calculate_mtld
from ..cleaner import extract_words

REPEATED_ABSTRACT_VERBS = {
    "ensure", "ensures", "ensuring", "ensured",
    "guarantee", "guarantees", "guaranteeing", "guaranteed",
    "provide", "provides", "providing", "provided",
    "facilitate", "facilitates", "facilitating", "facilitated",
    "leverage", "leverages", "leveraging", "leveraged",
    "mitigate", "mitigates", "mitigating", "mitigated",
    "enhance", "enhances", "enhancing", "enhanced",
    "demonstrate", "demonstrates", "demonstrating", "demonstrated",
    "foster", "fosters", "fostering", "fostered",
    "underpin", "underpins", "underpinning", "underpinned",
}


def analyze_lexical_diversity(text: str, words: List[str] = None) -> Dict[str, Any]:
    """Analizza la ricchezza del vocabolario e l'indice MTLD."""
    if words is None:
        words = extract_words(text)

    if not words:
        return {
            "status": "warning",
            "score": 50.0,
            "mtld": 0.0,
            "unique_words": 0,
            "ttr": 0.0,
            "repeated_abstract_verbs": [],
            "signals": ["Nessuna parola valida rilevata."],
            "prescriptions": []
        }

    mtld = calculate_mtld(words)
    total_words = len(words)
    unique_words = len(set(w.lower() for w in words))
    ttr = (unique_words / total_words) if total_words > 0 else 0.0

    # Rilevamento verbi astratti ripetuti
    lower_words = [w.lower() for w in words]
    counts = Counter(lower_words)
    flagged_verbs = [f"{w} ({c}x)" for w, c in counts.items() if w in REPEATED_ABSTRACT_VERBS and c >= 2]

    signals = []
    prescriptions = []

    if mtld >= 90.0:
        status = "safe"
        score = 15.0
    elif mtld >= 55.0:
        status = "warning"
        score = 45.0
        signals.append(f"Diversità lessicale moderata (MTLD = {mtld:.1f}, target naturale > 80.0).")
        prescriptions.append("Espandi il vocabolario tecnico: evita di riutilizzare gli stessi sostantivi o aggettivi generici nel medesimo paragrafo.")
    else:
        status = "critical"
        score = 80.0
        signals.append(f"Povertà lessicale (MTLD = {mtld:.1f}). Ripetitività frequente degli stessi lemmi.")
        prescriptions.append("Vocabolario ristretto: sostituisci le parole ripetute con terminologia scientifica precisa o sinonimi di registro superiore.")

    if flagged_verbs:
        signals.append(f"Verbi astratti generici ripetuti: {', '.join(flagged_verbs)}.")
        prescriptions.append(f"Elimina i verbi astratti ridondanti ({', '.join(flagged_verbs)}): usa verbi d'azione specifici (es. 'calcola', 'scarta', 'intercetta', 'scrive su disco').")

    return {
        "status": status,
        "score": score,
        "mtld": round(mtld, 1),
        "total_words": total_words,
        "unique_words": unique_words,
        "ttr": round(ttr, 3),
        "repeated_abstract_verbs": flagged_verbs,
        "signals": signals,
        "prescriptions": prescriptions
    }
