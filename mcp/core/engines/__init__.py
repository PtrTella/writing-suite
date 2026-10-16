"""
Writing Suite - Modular Multi-Pillar Diagnostic Engine Framework
Esporta tutti i motori diagnostici indipendenti e la funzione di orchestrazione
del Vettore Diagnostico Disaggregato.
"""

from typing import Dict, Any, List, Optional
from ..cleaner import clean_markup, extract_sentences, extract_words
from .cadence import analyze_cadence
from .surprisal import analyze_surprisal
from .syntax_patterns import analyze_syntax_patterns
from .lexical import analyze_lexical_diversity
from .neural import analyze_neural
from .external import analyze_external


def evaluate_paragraph_vector(
    paragraph: str,
    para_index: int = 1,
    run_external: bool = False
) -> Dict[str, Any]:
    """
    Esegue l'audit diagnostico disaggregato a motori indipendenti su un singolo paragrafo.
    Restituisce un vettore multidimensionale completo e un piano prescrittivo d'azione.
    """
    words = extract_words(paragraph)
    sentences = extract_sentences(paragraph)
    word_count = len(words)

    # 1. Motore Cadenza & Ritmo
    cadence_res = analyze_cadence(paragraph, sentences)

    # 2. Motore Causal Surprisal (SmolLM2 MPS)
    surprisal_res = analyze_surprisal(paragraph, sentences)

    # 3. Motore Pattern Sintattici & Simmetrie AI (Triadi, antitesi, em-dash)
    syntax_res = analyze_syntax_patterns(paragraph, sentences)

    # 4. Motore Diversità Lessicale (MTLD, verbi astratti)
    lexical_res = analyze_lexical_diversity(paragraph, words)

    # 5. Motore Neurale Macro Transformer (DeBERTa-v3)
    neural_res = analyze_neural(paragraph)

    # 6. Motore Validatori Esterni (Opzionale / Campionato)
    external_res = None
    if run_external and word_count >= 30:
        external_res = analyze_external(paragraph)

    # Raccogli tutte le prescrizioni operative per l'agente / utente
    prescriptions = []
    prescriptions.extend(syntax_res.get("prescriptions", []))
    prescriptions.extend(cadence_res.get("prescriptions", []))
    prescriptions.extend(surprisal_res.get("prescriptions", []))
    prescriptions.extend(lexical_res.get("prescriptions", []))
    prescriptions.extend(neural_res.get("prescriptions", []))
    if external_res:
        prescriptions.extend(external_res.get("prescriptions", []))

    # Calcolo Composite Score calibrato per compatibilità a valle
    # La priorità assoluta va a chi rileva anomalie critiche (principio forense non compensativo)
    p_cadence = cadence_res.get("score", 30.0)
    p_surprisal = surprisal_res.get("score", 30.0)
    p_syntax = syntax_res.get("score", 15.0)
    p_lexical = lexical_res.get("score", 20.0)
    p_neural = neural_res.get("score")
    if p_neural is None:
        p_neural = 35.0

    # Ponderazione diagnostica
    base_score = (
        0.25 * p_cadence +
        0.25 * p_surprisal +
        0.20 * p_syntax +
        0.15 * p_neural +
        0.15 * p_lexical
    )

    # Se ci sono pattern sintattici critici (es. triadi pesanti o monoriga)
    if syntax_res.get("status") == "critical":
        base_score = max(base_score, 75.0)
    elif cadence_res.get("status") == "critical" and p_neural > 60.0:
        base_score = max(base_score, 78.0)

    # Calibrazione per testi scientifici ad alta perplessità e cadenza naturale
    if surprisal_res.get("perplexity", 50.0) >= 110.0 and cadence_res.get("cadence_sigma", 0.0) >= 9.0 and not syntax_res.get("patterns_detected"):
        base_score = min(base_score, 24.0)

    final_risk = round(max(0.0, min(100.0, base_score)), 1)

    snippet = paragraph[:85] + ("..." if len(paragraph) > 85 else "")

    return {
        "index": para_index,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "risk_score": final_risk,
        "snippet": snippet,
        "vector": {
            "cadence": cadence_res,
            "surprisal": surprisal_res,
            "syntax": syntax_res,
            "lexical": lexical_res,
            "neural": neural_res,
            "external": external_res
        },
        "critical_sentence": surprisal_res.get("critical_sentence"),
        "prescriptions": prescriptions
    }
