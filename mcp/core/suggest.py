"""
Writing Suite - Actionable Writing Improver & Sentence-by-Sentence Advisor
Analizza i periodi marcati ad alto rischio AI da DeBERTa-v3 MPS o dal linter euristico,
spiegando l'esatta causa strutturale (cadenza metronomica, subordinata a sinistra, aforisma sintetico)
e suggerendo la ristrutturazione sintattica ottimale ispirata ai principi DIPPER e CleverHumanizer.
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.cleaner import extract_sentences, extract_words
from core.neural_detector import predict_sentences_batch, is_neural_available
from core.linter import lint_text


# Pattern strutturali tipici dei modelli LLM
LEFT_BRANCHING_PREFIXES = [
    (r"^(?:Instead of|Rather than)\s+([a-zA-Z]+ing)\b", "Apertura subordinata gerundiva di contrasto ('Instead of doing X, Y does Z'). Rende il periodo prevedibile."),
    (r"^(?:While|Although|Whereas)\s+[a-zA-Z]+\b", "Apertura concessiva stereotipata ('While X does Y...'). Divide artificialmente il periodo."),
    (r"^(?:Because|Since|Given that)\s+[a-zA-Z]+\b", "Apertura causale a sinistra ('Because X does Y, Z occurs'). Gli LLM aprono sistematicamente subordinando prima dell'asserzione principale."),
    (r"^(?:By|Through)\s+([a-zA-Z]+ing)\b", "Apertura strumentale con participio/gerundio ('By doing X, Y is achieved')."),
    (r"^(?:In order to|To)\s+([a-zA-Z]+)\b", "Incipit finale programmatico ('To reduce this friction, X did Y')."),
]

SYNTHETIC_SLOGANS = [
    r"^[A-Z][a-z]+\s+(?:is|remains)\s+(?:absolute|sustainable|paramount|essential)\.?$",
    r"^[A-Z][a-z]+\s+replaces\s+[a-z]+\.?$",
    r"^[A-Z][a-z]+\s+defeats\s+[a-z]+\.?$",
    r"^[A-Z][a-z]+\s+precedes\s+[a-z]+\.?$",
]


def analyze_sentence_flaws(
    sentence: str,
    ai_prob: float,
    prev_sentence: Optional[str] = None,
    next_sentence: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> List[Dict[str, str]]:
    """Identifica i difetti sintattici specifici di una singola frase calata nel suo contesto."""
    flaws = []
    trimmed = sentence.strip()
    words = extract_words(trimmed)
    word_count = len(words)
    meta = meta or {}

    # 0. Incipit generico ChatGPT ('Modern software engineering relies heavily on...')
    if re.search(r"^(?:Modern\s+[a-z\s]+(?:relies\s+heavily\s+on|practices\s+favor|engineering\s+relies|development\s+relies|approaches\s+depend|systems\s+rely))\b", trimmed, re.IGNORECASE):
        flaws.append({
            "type": "CHATGPT_INTRO_OPENER",
            "severity": "CRITICAL",
            "diagnostic": "Incipit stereotipato generico ('Modern software engineering relies heavily on...'). Cliché assoluto dei modelli generativi."
        })

    # 1. Rilevamento della Slogan Trap (3-6 parole isolate ad effetto drammatico)
    if word_count <= 6 and not trimmed.startswith("=") and not trimmed.startswith("#") and not trimmed.startswith("-"):
        flaws.append({
            "type": "ISOLATED_SHORT_SLOGAN",
            "severity": "HIGH",
            "diagnostic": f"Mini-frase isolata da sole {word_count} parole ('{trimmed}'). Genera pattern di chiusura prevedibile ('predictable sentence endings')."
        })

    for pat in SYNTHETIC_SLOGANS:
        if re.search(pat, trimmed, re.IGNORECASE) and not any(f["type"] == "ISOLATED_SHORT_SLOGAN" for f in flaws):
            flaws.append({
                "type": "SLOGAN_TRAP",
                "severity": "CRITICAL",
                "diagnostic": "Aforisma sintetico lapidario da 3-4 parole."
            })

    # 2. Rilevamento Aperture Subordinate a Sinistra (Left-Branching)
    for pat, desc in LEFT_BRANCHING_PREFIXES:
        if re.search(pat, trimmed, re.IGNORECASE):
            flaws.append({
                "type": "LEFT_BRANCHING_SUBORDINATE",
                "severity": "HIGH",
                "diagnostic": desc
            })
            break

    # 3. Ripetitività Apertura rispetto alla Frase Precedente (Contextual Flaw)
    if prev_sentence:
        prev_w = extract_words(prev_sentence.strip())
        if len(prev_w) >= 2 and len(words) >= 2:
            if [w.lower() for w in prev_w[:2]] == [w.lower() for w in words[:2]]:
                flaws.append({
                    "type": "REPETITIVE_CONSECUTIVE_OPENER",
                    "severity": "HIGH",
                    "diagnostic": f"Apertura consecutiva identica con la frase precedente ('{' '.join(words[:2])}...')."
                })

    # 4. Monotonia di Cadenza a Coppie (Metronomo consecutivo)
    if prev_sentence:
        prev_len = len(extract_words(prev_sentence.strip()))
        if 18 <= prev_len <= 26 and 18 <= word_count <= 26 and abs(prev_len - word_count) <= 2:
            flaws.append({
                "type": "CADENCE_MONOTONY_PAIR",
                "severity": "MEDIUM",
                "diagnostic": f"Due periodi consecutivi di identica lunghezza ({prev_len} e {word_count} parole). Genera cadenza metronomica."
            })

    # 5. Anomalia Contestuale Neurale (Context Penalty)
    if meta.get("context_anomaly"):
        penalty = meta.get("context_penalty", 0.0)
        p_sing = meta.get("standalone_probability", 0.0)
        p_ctx = meta.get("context_probability", 0.0)
        flaws.append({
            "type": "HIGH_CONTEXT_ROBOTICITY",
            "severity": "HIGH",
            "diagnostic": f"Discrepanza contestuale (+{penalty}% nel flusso): la frase è neutrale da sola ({p_sing}%), ma in sequenza raggiunge il {p_ctx}%."
        })

    # 6. Trattini em multipli
    if "—" in trimmed or " -- " in trimmed:
        flaws.append({
            "type": "EM_DASH_CRUTCH",
            "severity": "HIGH",
            "diagnostic": "Uso del trattino em come scorciatoia sintattica."
        })

    # 7. Picco di Robotismo Neurale (DeBERTa-v3 MPS)
    p_sing = meta.get("standalone_probability", ai_prob)
    if ai_prob >= 65.0 or p_sing >= 65.0:
        flaws.append({
            "type": "NEURAL_ROBOTICITY_SPIKE",
            "severity": "CRITICAL",
            "diagnostic": f"Rischio AI neurale elevato ({max(ai_prob, p_sing):.1f}% rilevato da DeBERTa). Struttura proposizionale con forte prevedibilità statistica."
        })

    # 8. Transizione generica da saggio AI
    transitions = [r"^Consequently,", r"^Moreover,", r"^Furthermore,", r"^Additionally,", r"^In addition,", r"^Therefore,", r"^Specifically,", r"^Importantly,"]
    for pat in transitions:
        if re.search(pat, trimmed, re.IGNORECASE):
            flaws.append({
                "type": "GENERIC_TRANSITION_CRUTCH",
                "severity": "HIGH",
                "diagnostic": f"Connettivo transizionale generico in apertura ('{trimmed.split()[0]}'). Tipico intercalare da saggio scolastico LLM."
            })
            break

    return flaws


def suggest_improvements(text: str, domain_terms: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Esegue la scansione microscopica e macroscopica del testo:
    - Analisi neurale contestuale (trigrammi) su Metal MPS
    - Hotspot discovery tramite Sliding Window a 512 token
    - Diagnosi dei difetti sintattici inter-periodo
    """
    sentences = extract_sentences(text)
    if not sentences:
        return {"error": "Nessun periodo estratto dal testo."}

    valid_sents = [s for s in sentences if len(s.split()) >= 3]
    neural_results = []
    chunk_diagnostics = {"chunks": [], "hotspots": []}

    if is_neural_available():
        try:
            from core.neural_detector import predict_sliding_window_chunks
            chunk_diagnostics = predict_sliding_window_chunks(text)
            neural_results = predict_sentences_batch(valid_sents, with_context=True)
        except Exception as e:
            neural_results = []

    prob_map = {r["text"]: r for r in neural_results}

    sentence_diagnostics = []
    high_risk_count = 0

    for idx, s in enumerate(sentences):
        trimmed = s.strip()
        neural_info = prob_map.get(trimmed, {})
        prob = neural_info.get("ai_probability", 50.0)

        prev_s = sentences[idx - 1] if idx > 0 else None
        next_s = sentences[idx + 1] if idx + 1 < len(sentences) else None

        flaws = analyze_sentence_flaws(
            trimmed,
            prob,
            prev_sentence=prev_s,
            next_sentence=next_s,
            meta=neural_info
        )

        if prob >= 65.0:
            badge = "🔴"
            status = "AI"
            high_risk_count += 1
        elif prob >= 35.0:
            badge = "🟡"
            status = "MIXED"
        else:
            badge = "🟢"
            status = "HUMAN"

        sentence_diagnostics.append({
            "index": idx + 1,
            "text": trimmed,
            "word_count": len(extract_words(trimmed)),
            "ai_probability": prob,
            "standalone_probability": neural_info.get("standalone_probability", prob),
            "context_probability": neural_info.get("context_probability", prob),
            "context_penalty": neural_info.get("context_penalty", 0.0),
            "context_anomaly": neural_info.get("context_anomaly", False),
            "badge": badge,
            "status": status,
            "flaws": flaws,
            "needs_rewrite": prob >= 55.0 or len(flaws) > 0
        })

    hotspots = chunk_diagnostics.get("hotspots", [])

    return {
        "total_sentences": len(sentences),
        "high_risk_sentences": high_risk_count,
        "clean_sentences": len(sentences) - high_risk_count,
        "hotspots_count": len(hotspots),
        "hotspots": hotspots,
        "overall_health": "OTTIMO" if high_risk_count == 0 and len(hotspots) == 0 else ("MEDIO" if high_risk_count <= 2 else "CRITICO"),
        "sentences": sentence_diagnostics,
        "action_plan": [
            "1. Sostituire le aperture con subordinate gerundive/concessive ('Instead of...', 'While...') con asserzioni dirette seguite da due punti esplicativi (:).",
            "2. Inserire frasi 'respiro' brevi e riflessive (10-12 parole) tra periodi lunghi da 30+ parole per rompere il metronomo.",
            "3. Riconvertire formule astratte in conseguenze operative reali sull'ingegnere o sull'operatore di sistema.",
            "4. Verificare che non siano rimasti aforismi sintetici da 3-4 parole a chiusura di paragrafo.",
            "5. Eliminare aperture consecutive identiche su periodi adiacenti (es. 'The system... The system...')."
        ]
    }

