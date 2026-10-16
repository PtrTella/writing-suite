"""
Writing Suite - Syntax & AI Patterns Diagnostic Engine
Analizza la sintassi fine per rilevare i pattern di simmetria sintattica che innescano
i rilevatori commerciali (Sapling, CleverHumanizer, GPTZero):
1. Triadic Parallelism (Elenchi ternari perfettamente bilanciati A, B, and C)
2. Symmetrical Antithesis (Contrapposizioni bilanciate "cannot X; rather Y")
3. Em-dash Explanatory Clauses (Incisi esplicativi "--- as demonstrated by...")
4. Passive Hedges & Vague Attribution ("plays a crucial role", "is widely recognized")
5. Formulaic Transitional Openings ("Moreover,", "Furthermore,", "Consequently,")
6. Single-Sentence Zero-Variance Blocks (Paragrafi monoriga isolati)
"""

import re
from typing import Dict, Any, List

# Pattern regex per il rilevamento fine
RE_TRIADIC_LIST = re.compile(
    r"(?:(?:\b[a-zA-Z\-]+\s+){1,4}[a-zA-Z\-]+,\s+){2}(?:and|or)\s+(?:(?:\b[a-zA-Z\-]+\s+){1,4}[a-zA-Z\-]+)",
    re.IGNORECASE
)

RE_SYMMETRICAL_ANTITHESIS = re.compile(
    r"\b(?:not|cannot|neither|fails?\s+to)\b[^;.\n]+;\s*(?:their|its|it|the|rather|instead)\b[^.\n]+(?:rather\s+than|instead\s+of|whereas)",
    re.IGNORECASE
)

RE_EMDASH_EXPLANATION = re.compile(
    r"(?:---|—|--)\s*(?:as\s+(?:demonstrated|evidenced|illustrated|seen|shown)|which\s+(?:highlights|underscores|demonstrates|proves)|illustrating|underscoring)",
    re.IGNORECASE
)

RE_PASSIVE_HEDGES = re.compile(
    r"\b(?:plays?\s+(?:a\s+)?(?:crucial|pivotal|vital|key|fundamental)\s+role|"
    r"serves?\s+as\s+a\s+testament|"
    r"is\s+(?:widely|commonly)\s+(?:recognized|acknowledged|believed)|"
    r"underscores?\s+the\s+(?:importance|need|criticality)|"
    r"delves?\s+into|tapestry\s+of|fosters?\s+collaboration)\b",
    re.IGNORECASE
)

RE_FORMULAIC_TRANSITIONS = re.compile(
    r"^(?:Moreover|Furthermore|Consequently|Additionally|Importantly|Crucially|Ultimately|In\s+summary|In\s+conclusion),\s+",
    re.IGNORECASE | re.MULTILINE
)


def analyze_syntax_patterns(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """Analizza il testo per identificare pattern sintattici simmetrici tipici dell'AI."""
    if sentences is None:
        from ..cleaner import extract_sentences
        sentences = extract_sentences(text)

    signals = []
    prescriptions = []
    detected_patterns = []

    # 1. Paragrafo a frase singola (varianza zero)
    if len(sentences) == 1 and len(text.split()) >= 12:
        signals.append({
            "type": "single_sentence_block",
            "severity": "critical",
            "description": "Paragrafo monoriga a varianza ritmica zero (σ_len = 0.0)."
        })
        prescriptions.append(
            "Paragrafo a frase singola: integralo nel flusso argomentativo o espandilo con dettagli tecnici e variazioni di lunghezza."
        )
        detected_patterns.append("Single-Sentence Zero-Variance")

    # 2. Elenchi ternari (Triadic Lists)
    triadic_matches = RE_TRIADIC_LIST.findall(text)
    if triadic_matches:
        for match in triadic_matches[:2]:
            signals.append({
                "type": "triadic_list",
                "severity": "warning",
                "snippet": match.strip(),
                "description": "Elenco ternario perfettamente bilanciato (A, B, and C)."
            })
        prescriptions.append(
            f"Trovati {len(triadic_matches)} elenchi ternari: rompi la simmetria a tre (elencane solo due o trasforma il terzo elemento in una frase subordinata causale)."
        )
        detected_patterns.append(f"Triadic Parallelism ({len(triadic_matches)})")

    # 3. Contrapposizioni simmetriche
    antithesis_matches = RE_SYMMETRICAL_ANTITHESIS.findall(text)
    if antithesis_matches:
        for match in antithesis_matches[:2]:
            signals.append({
                "type": "symmetrical_antithesis",
                "severity": "warning",
                "snippet": match.strip()[:80] + "...",
                "description": "Contrapposizione simmetrica formale (cannot X; rather Y)."
            })
        prescriptions.append(
            "Contrapposizione simmetrica: elimina la struttura binaria rigida con punto e virgola; usa un'affermazione diretta o una domanda retorica."
        )
        detected_patterns.append("Symmetrical Antithesis")

    # 4. Incisi con em-dash esplicativi
    emdash_matches = RE_EMDASH_EXPLANATION.findall(text)
    if emdash_matches:
        for match in emdash_matches[:2]:
            signals.append({
                "type": "emdash_explanation",
                "severity": "warning",
                "snippet": match.strip(),
                "description": "Inciso esplicativo appositivo con em-dash (--- as demonstrated by...)."
            })
        prescriptions.append(
            "Inciso con em-dash: rimuovi la formula '--- as demonstrated by/which highlights' e formula la prova sperimentale in un periodo autonomo."
        )
        detected_patterns.append("Explanatory Em-dash")

    # 5. Passive hedges / Cliché accademici
    hedges = RE_PASSIVE_HEDGES.findall(text)
    if hedges:
        for h in hedges[:2]:
            signals.append({
                "type": "passive_hedge",
                "severity": "critical",
                "snippet": h,
                "description": "Cliché accademico sintetico o attenuazione passiva."
            })
        prescriptions.append(
            f"Rilevati cliché/hedges ({', '.join(set(hedges))}): sostituiscili con sostantivi operativi concreti ed evidenze empiriche."
        )
        detected_patterns.append(f"AI Clichés ({len(hedges)})")

    # 6. Aperture transizionali formulaiche
    transitions = RE_FORMULAIC_TRANSITIONS.findall(text)
    if transitions:
        prescriptions.append(
            f"Aperture transizionali prevedibili ({', '.join(set(t.strip() for t in transitions))}): elimina il connettore iniziale e inizia direttamente con il soggetto o il fatto."
        )
        detected_patterns.append("Formulaic Transitions")

    # Determinazione dello status
    has_critical = any(s["severity"] == "critical" for s in signals)
    has_warning = any(s["severity"] == "warning" for s in signals)

    if has_critical or len(signals) >= 3:
        status = "critical"
        score = 80.0
    elif has_warning or len(signals) >= 1:
        status = "warning"
        score = 45.0
    else:
        status = "safe"
        score = 10.0

    return {
        "status": status,
        "score": score,
        "patterns_detected": detected_patterns,
        "signals": signals,
        "prescriptions": prescriptions
    }
