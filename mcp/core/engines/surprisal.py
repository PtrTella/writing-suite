"""
Writing Suite - Causal Surprisal & Binoculars Entropy Diagnostic Engine
Calcola la perplessità a livello di token, l'entropia predittiva di Shannon (Binoculars),
la curvatura di verosimiglianza (Fast-DetectGPT Top-1 Gap) e la burstiness
usando un modello linguistico causale (SmolLM2) accelerato su GPU Apple Silicon Metal (MPS).
Identifica le sequenze a sorpresa quasi-nulla (cliché probabilistici dell'AI).
"""

from typing import Dict, Any, List
from ..surprisal import calculate_token_surprisal, analyze_sentences_surprisal, is_causal_available


def analyze_surprisal(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """Valuta perplessità, rapporto Binoculars (PPL/Entropia) e curvatura Top-1."""
    if sentences is None:
        from ..cleaner import extract_sentences
        sentences = extract_sentences(text)

    surprisal_res = calculate_token_surprisal(text)
    ppl = surprisal_res.get("perplexity", 50.0)
    burstiness = surprisal_res.get("burstiness", 3.5)
    binoculars = surprisal_res.get("binoculars_ratio", 1.0)
    top1_gap = surprisal_res.get("top1_gap", 2.5)
    entropy = surprisal_res.get("mean_entropy_nats", 3.0)
    raw_risk = surprisal_res.get("risk_score", 30.0)

    signals = []
    prescriptions = []

    # 1. Valutazione Perplessità Causale
    if ppl >= 75.0:
        ppl_status = "safe"
    elif ppl >= 45.0:
        ppl_status = "warning"
        signals.append(f"Perplessità moderata (PPL = {ppl:.1f}, target naturale > 75.0).")
        prescriptions.append("Perplessità al limite: sostituisci n-grammi generici con terminologia di sistema empirica e non scontata.")
    else:
        ppl_status = "critical"
        signals.append(f"Perplessità causale molto bassa (PPL = {ppl:.1f}). Sequenza di token altamente prevedibile.")
        prescriptions.append(
            "Perplessità critica (flusso probabilistico uniforme): riscrivi eliminando collocazioni standard e introducendo dettagli tecnici puntuali."
        )

    # 2. Valutazione Principio Binoculars (Hans et al., ICML 2024)
    # Ratio = log(PPL) / Mean_Entropy
    if binoculars < 0.95:
        signals.append(f"Rapporto Binoculars compresso ({binoculars:.2f} < 0.95): i token seguono passivamente l'entropia del modello.")
        prescriptions.append(
            f"Firma Binoculars critica ({binoculars:.2f}): le scelte lessicali non divergono dalla distribuzione generativa; ancora il discorso a metriche empiriche o vincoli hardware."
        )
    elif binoculars > 1.15:
        signals.append(f"Divergenza Binoculars naturale ({binoculars:.2f} > 1.15): selezione lessicale asimmetrica umana autentica.")

    # 3. Valutazione Fast-DetectGPT Top-1 Gap (Bao et al., ICLR 2024)
    if top1_gap < 2.1:
        signals.append(f"Curvatura Top-1 piatta (Gap = {top1_gap:.2f}): le parole ricalcano l'argmax/greedy path del modello.")
        prescriptions.append(
            f"Top-1 Gap ridotto ({top1_gap:.2f}): varia l'apertura e il verbo reggente per allontanare la frase dalla traiettoria statistica più frequente."
        )

    # Calcolo status e score
    if ppl_status == "critical" or binoculars < 0.92 or top1_gap < 1.9:
        status = "critical"
        score = max(75.0, raw_risk)
    elif ppl_status == "warning" or binoculars < 1.0 or top1_gap < 2.3:
        status = "warning"
        score = max(40.0, raw_risk)
    else:
        status = "safe"
        score = min(25.0, raw_risk)

    # Identifica la frase più prevedibile
    critical_sentence = None
    if len(sentences) > 0:
        try:
            s_evals = analyze_sentences_surprisal(sentences)
            if s_evals:
                s_evals.sort(key=lambda s: (s.get("binoculars_ratio", 1.0), s["perplexity"]))
                worst = s_evals[0]
                if worst["perplexity"] < 50.0 or worst.get("binoculars_ratio", 1.0) < 0.98:
                    critical_sentence = {
                        "text": worst["sentence"],
                        "perplexity": round(worst["perplexity"], 1),
                        "binoculars_ratio": round(worst.get("binoculars_ratio", 1.0), 2),
                        "top1_gap": round(worst.get("top1_gap", 2.5), 2),
                        "burstiness": round(worst["burstiness"], 2)
                    }
                    signals.append(
                        f"Frase più prevedibile (PPL={worst['perplexity']:.1f}, Binoculars={worst.get('binoculars_ratio', 1.0):.2f}): \"{worst['sentence'][:60]}...\""
                    )
        except Exception:
            pass

    return {
        "status": status,
        "score": score,
        "perplexity": round(ppl, 1),
        "mean_entropy": round(entropy, 2),
        "binoculars_ratio": round(binoculars, 2),
        "top1_gap": round(top1_gap, 2),
        "burstiness": round(burstiness, 2),
        "critical_sentence": critical_sentence,
        "signals": signals,
        "prescriptions": prescriptions
    }

