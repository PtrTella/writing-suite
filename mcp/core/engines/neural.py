"""
Writing Suite - Neural Macro-Transformer Diagnostic Engine
Esegue l'inferenza del classificatore DeBERTa-v3 su spazio latente denso.
Rileva la levigatezza semantica e le correlazioni di contesto profonde.
"""

from typing import Dict, Any
from ..neural_detector import predict_text_score, is_neural_available


def analyze_neural(text: str) -> Dict[str, Any]:
    """Analizza il testo tramite il classificatore neurale DeBERTa-v3."""
    if not is_neural_available():
        return {
            "status": "safe",
            "score": None,
            "available": False,
            "signals": ["Classificatore DeBERTa non disponibile."],
            "prescriptions": []
        }

    try:
        score = predict_text_score(text)
    except Exception as e:
        return {
            "status": "warning",
            "score": None,
            "available": False,
            "signals": [f"Errore inferenza DeBERTa: {str(e)}"],
            "prescriptions": []
        }

    signals = []
    prescriptions = []

    if score <= 30.0:
        status = "safe"
    elif score <= 60.0:
        status = "warning"
        signals.append(f"DeBERTa-v3 rileva coesione artificiale intermedia ({score:.1f}%).")
        prescriptions.append("Riduci la regolarità delle connessioni tematiche: disallinea la progressione logica canonica.")
    else:
        status = "critical"
        signals.append(f"DeBERTa-v3 rileva pattern di rappresentazione neurale molto elevati ({score:.1f}%).")
        prescriptions.append(
            "Forte impronta di modello transformer: riscrivi radicalmente il paragrafo alterando la punteggiatura, l'ordine dei costituenti e l'impianto argomentativo."
        )

    return {
        "status": status,
        "score": round(score, 1),
        "available": True,
        "signals": signals,
        "prescriptions": prescriptions
    }
