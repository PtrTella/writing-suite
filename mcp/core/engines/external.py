"""
Writing Suite - External Multi-Detector Consensus Diagnostic Engine
Interroga in parallelo i 3 principali validatori commerciali:
1. Sapling.ai (Stanford / Berkeley deep NLP)
2. CleverHumanizer.ai (detector euristico + patterns)
3. ZeroGPT.com (perplessità ed n-gram statistici)
Fornisce il controllo di cross-validazione oggettivo della rete.
"""

import asyncio
from typing import Dict, Any
from ..external_detector import check_multi_detector


def analyze_external(text: str) -> Dict[str, Any]:
    """Esegue la cross-validazione esterna su Sapling, ZeroGPT e CleverHumanizer."""
    words = text.strip().split()
    if len(words) < 25:
        return {
            "status": "warning",
            "score": None,
            "available": False,
            "signals": [f"Testo troppo breve per i detector esterni ({len(words)} parole, attese ≥ 25)."],
            "prescriptions": []
        }

    try:
        res = asyncio.run(check_multi_detector(text))
    except Exception as e:
        return {
            "status": "warning",
            "score": None,
            "available": False,
            "signals": [f"Errore durante l'interrogazione esterna: {str(e)}"],
            "prescriptions": []
        }

    score = res.get("consensus_score")
    badge = res.get("consensus_badge", "🟡")
    verdict = res.get("consensus_verdict", "Uncertain")
    detectors = res.get("detectors", {})

    signals = []
    prescriptions = []

    sapling = detectors.get("sapling", {}).get("overall_ai_score")
    clever = detectors.get("cleverhumanizer", {}).get("overall_ai_score")
    zerogpt = detectors.get("zerogpt", {}).get("overall_ai_score")

    signals.append(f"Consenso Esterno: {badge} {score}% ({verdict}) [Sapling: {sapling}%, Clever: {clever}%, ZeroGPT: {zerogpt}%]")

    # Se CleverHumanizer ha segnalato specifici pattern
    clever_patterns = detectors.get("cleverhumanizer", {}).get("flagged_ai_patterns", [])
    if clever_patterns:
        signals.append(f"Pattern commerciali rilevati: {', '.join(clever_patterns)}")
        for pat in clever_patterns:
            if "rhythm" in pat.lower() or "pattern" in pat.lower():
                prescriptions.append("Validatori esterni rilevano ritmo/pattern ripetitivi: altera la struttura delle proposizioni.")
            elif "personal voice" in pat.lower():
                prescriptions.append("Validatori esterni rilevano mancanza di voce naturale: inserisci osservazioni dialettiche o asimmetriche.")

    if score is not None:
        if score < 35.0:
            status = "safe"
        elif score < 65.0:
            status = "warning"
            prescriptions.append("Punteggio esterno in zona incerta: elimina elenchi simmetrici e varia la lunghezza del periodo.")
        else:
            status = "critical"
            prescriptions.append("Validatori esterni segnalano forte impronta AI: riscrivi il paragrafo rompendo simmetrie sintattiche ed elenchi a tre.")
    else:
        status = "warning"

    return {
        "status": status,
        "score": score,
        "available": True,
        "detectors": detectors,
        "signals": signals,
        "prescriptions": prescriptions
    }
