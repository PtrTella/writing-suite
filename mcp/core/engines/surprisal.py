"""
Writing Suite - Causal Surprisal & Burstiness Diagnostic Engine
Calcola la perplessità a livello di token e la burstiness di sorpresa informativa
usando un modello linguistico causale (SmolLM2) accelerato su GPU Apple Silicon Metal (MPS).
Identifica le frasi a sorpresa quasi-nulla (cliché probabilistici dell'AI).
"""

from typing import Dict, Any, List
from ..surprisal import calculate_token_surprisal, analyze_sentences_surprisal, is_causal_available


def analyze_surprisal(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """Valuta la perplessità e la burstiness di sorpresa causale."""
    if sentences is None:
        from ..cleaner import extract_sentences
        sentences = extract_sentences(text)

    surprisal_res = calculate_token_surprisal(text)
    ppl = surprisal_res.get("perplexity", 50.0)
    burstiness = surprisal_res.get("burstiness", 3.5)
    raw_risk = surprisal_res.get("risk_score", 30.0)

    signals = []
    prescriptions = []

    if ppl >= 80.0:
        status = "safe"
        score = 15.0
    elif ppl >= 40.0:
        status = "warning"
        score = 45.0
        signals.append(f"Perplessità moderata (PPL = {ppl:.1f}, target naturale > 75.0).")
        prescriptions.append("Perplessità al limite: sostituisci n-grammi generici con terminologia di sistema empirica e non scontata.")
    else:
        status = "critical"
        score = 85.0
        signals.append(f"Perplessità causale molto bassa (PPL = {ppl:.1f}). Sequenza di token altamente prevedibile da un modello statistico.")
        prescriptions.append(
            "Perplessità critica (flusso di token da testo generativo): riscrivi la frase eliminando collocazioni standard e introducendo dettagli tecnici puntuali."
        )

    # Identifica la frase più prevedibile
    critical_sentence = None
    if len(sentences) > 0:
        try:
            s_evals = analyze_sentences_surprisal(sentences)
            if s_evals:
                s_evals.sort(key=lambda s: s["perplexity"])
                worst = s_evals[0]
                if worst["perplexity"] < 45.0:
                    critical_sentence = {
                        "text": worst["sentence"],
                        "perplexity": round(worst["perplexity"], 1),
                        "burstiness": round(worst["burstiness"], 2)
                    }
                    signals.append(f"Frase più prevedibile (PPL = {worst['perplexity']:.1f}): \"{worst['sentence'][:60]}...\"")
        except Exception:
            pass

    return {
        "status": status,
        "score": score,
        "perplexity": round(ppl, 1),
        "burstiness": round(burstiness, 2),
        "critical_sentence": critical_sentence,
        "signals": signals,
        "prescriptions": prescriptions
    }
