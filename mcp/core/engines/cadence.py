"""
Writing Suite - Cadence & Rhythm Diagnostic Engine
Valuta la dinamica ritmica, la dispersione sillabica e l'asimmetria periodale.
Identifica cadenze metronomiche artificiali (tipiche degli LLM) e assicura
la varianza ritmica naturale umana (target σ_len >= 10.0, presenza di clausole staccate).
"""

import math
from typing import Dict, Any, List


def analyze_cadence(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """Analizza il ritmo e la cadenza asimmetrica del testo."""
    if sentences is None:
        from ..cleaner import extract_sentences
        sentences = extract_sentences(text)

    from ..cleaner import extract_words

    if not sentences:
        return {
            "status": "warning",
            "score": 50.0,
            "cadence_sigma": 0.0,
            "mean_length": 0.0,
            "min_length": 0,
            "max_length": 0,
            "staccato_count": 0,
            "signals": ["Nessuna frase valida rilevata."],
            "prescriptions": []
        }

    lengths = [len(extract_words(s)) for s in sentences if len(extract_words(s)) > 0]

    if len(lengths) <= 1:
        single_len = lengths[0] if lengths else 0
        return {
            "status": "critical" if single_len >= 15 else "warning",
            "score": 85.0 if single_len >= 15 else 50.0,
            "cadence_sigma": 0.0,
            "mean_length": float(single_len),
            "min_length": single_len,
            "max_length": single_len,
            "staccato_count": 1 if single_len <= 8 else 0,
            "signals": ["Paragrafo a frase singola (varianza ritmica nulla, σ = 0.0)."],
            "prescriptions": [
                "Aggiungi un periodo breve di contrasto o spezza la frase per generare asimmetria ritmica."
            ]
        }

    mean_len = sum(lengths) / len(lengths)
    var = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
    sigma = math.sqrt(var)

    min_l = min(lengths)
    max_l = max(lengths)
    staccato_count = sum(1 for l in lengths if l <= 8)
    long_count = sum(1 for l in lengths if l >= 30)

    signals = []
    prescriptions = []

    # Valutazione di cadenza
    if sigma >= 10.0:
        status = "safe"
        score = 15.0
    elif sigma >= 6.5:
        status = "warning"
        score = 40.0
        signals.append(f"Cadenza moderatamente prevedibile (σ_len = {sigma:.1f} parole, atteso ≥ 10.0).")
        prescriptions.append(
            f"Varia la lunghezza delle frasi (attualmente tra {min_l} e {max_l} parole): accorcia una frase a 5-8 parole o allunga un periodo complesso."
        )
    else:
        status = "critical"
        score = 80.0
        signals.append(f"Cadenza metronomica robotica (σ_len = {sigma:.1f} parole). Le frasi hanno tutte lunghezza uniforme.")
        prescriptions.append(
            f"Ritmo metronomico (tutte le frasi durano circa {mean_len:.0f} parole): spezza una frase lunga e inserisci una proposizione staccata di 4-6 parole per rompere la prevedibilità."
        )

    # Verifica clausole staccate
    if len(sentences) >= 3 and staccato_count == 0 and min_l >= 14:
        if status != "critical":
            status = "warning"
            score = max(score, 50.0)
        signals.append("Assenza totale di clausole staccate (tutte le frasi superano 14 parole).")
        prescriptions.append("Mancanza di clausole brevi: inserisci una frase d'impatto di meno di 8 parole per dare respiro al lettore.")

    return {
        "status": status,
        "score": score,
        "cadence_sigma": round(sigma, 1),
        "mean_length": round(mean_len, 1),
        "min_length": min_l,
        "max_length": max_l,
        "staccato_count": staccato_count,
        "long_count": long_count,
        "lengths": lengths,
        "signals": signals,
        "prescriptions": prescriptions
    }
