"""
Writing Suite - Evaluator Engine Module
Orchestra i 4 valutatori autonomi e calcola il punteggio unificato ponderato di rischio AI:
1. Emulatore GPTZero Locale (35%)
2. Linter Euristico Ponderato (35%)
3. Stilometria Accademica (15%)
4. Modulo Anti-Bypass (15%)
Restituisce output JSON strutturato e report formattato in puro Markdown.
"""

import math
from .cleaner import clean_markup, extract_sentences, extract_words
from .linter import lint_text
from .word_freq import calculate_gltr_profile, calculate_mtld
from .metrics import (
    calculate_perplexity_and_burstiness,
    calculate_stylometrics,
    check_anti_bypass,
    calculate_readability
)

def evaluate_document(text: str, file_path: str = None) -> dict:
    """Esegue l'audit completo multi-prospettiva e restituisce il report analitico."""
    cleaned_prose = clean_markup(text)
    sentences = extract_sentences(text)
    words = extract_words(text)

    if len(words) < 15:
        return {
            "error": "Testo troppo breve per una valutazione attendibile (minimo 15-20 parole).",
            "overall_ai_score": 0.0,
            "verdict": "NON_VALUTABILE"
        }

    lang = "it" if any(w in words for w in ["di", "il", "la", "che", "per", "in", "un", "con"]) else "en"

    # 1. GPTZero emulato (Perplessità locale e Burstiness di sorpresa)
    gptzero_res = calculate_perplexity_and_burstiness(sentences)
    score_gptzero = gptzero_res["risk_score"]

    # 2. GLTR Forensics (Profilazione ranghi Zipf e saturazione lessicale)
    gltr_res = calculate_gltr_profile(words, lang=lang)
    score_gltr = gltr_res["gltr_risk_score"]

    # 3. Cadence Burstiness (Deviazione standard della lunghezza delle frasi)
    s_lens = [len(extract_words(s)) for s in sentences if len(extract_words(s)) >= 2]
    if len(s_lens) >= 2:
        mean_len = round(sum(s_lens) / len(s_lens), 1)
        var_len = sum((l - mean_len) ** 2 for l in s_lens) / len(s_lens)
        std_len = round(math.sqrt(var_len), 1)
    else:
        mean_len = 15.0
        std_len = 10.0
    # Cadence risk: se std_len < 7.0 -> ritmo robotico uniforme (100%), se std_len >= 13.0 -> varianza umana (0%)
    score_cadence = round(max(0.0, min(100.0, (13.5 - std_len) * 9.0)), 1)

    # 4. Linter Euristico (50+ pattern statistici, formattazione seriale e costrutti AI)
    linter_findings = lint_text(text)
    total_linter_weight = sum(f["weight"] for f in linter_findings)
    word_count = len(words)
    findings_density = (len(linter_findings) / max(1, word_count)) * 100.0
    score_linter = min(100.0, round(total_linter_weight * 13.0 + findings_density * 4.0, 1))

    # 5. Stilometria Accademica & MTLD (Invariante rispetto alla lunghezza)
    stylometrics_res = calculate_stylometrics(words)
    mtld_val = calculate_mtld(words)
    score_mtld = max(0.0, min(100.0, (80.0 - mtld_val) * 1.5))
    score_stylo = round(0.6 * stylometrics_res["risk_score"] + 0.4 * score_mtld, 1)

    # 6. Anti-Bypass (Rilevamento frammentazione artificiale o prompt injects)
    anti_bypass_res = check_anti_bypass(text, sentences)
    score_bypass = anti_bypass_res["risk_score"]

    # Punteggio Ponderato Complessivo:
    # 35% Linter Euristico + 25% Cadence Burstiness + 25% Predittività (GPTZero + GLTR) + 15% Stilometria & MTLD
    predictability_score = (0.5 * score_gptzero) + (0.5 * score_gltr)
    base_score = (
        (0.35 * score_linter) +
        (0.25 * score_cadence) +
        (0.25 * predictability_score) +
        (0.15 * score_stylo)
    )

    # Booster additivo se rilevate anomalie da bypasser
    if score_bypass > 0:
        base_score = min(100.0, base_score + 0.25 * score_bypass)

    weighted_ai_score = round(min(100.0, max(0.0, base_score)), 1)

    # Verdetto
    if weighted_ai_score >= 65.0:
        verdict = "ALTISSIMA PROBABILITÀ DI TESTO SINTETICO / AI"
        badge = "🔴"
    elif weighted_ai_score >= 40.0:
        verdict = "PROBABILE TESTO MISTO O PESANTEMENTE EDITATO DA AI"
        badge = "🟡"
    elif weighted_ai_score >= 20.0:
        verdict = "TESTO MODERATAMENTE NATURALE CON LIEVI TIC STATISTICI"
        badge = "🟢"
    else:
        verdict = "ALTISSIMA NATURALEZZA / SCRITTURA AUTENTICA UMANA"
        badge = "🟢"

    readability_res = calculate_readability(cleaned_prose, lang=lang)

    return {
        "file_path": file_path,
        "overall_ai_score": weighted_ai_score,
        "verdict": verdict,
        "verdict_badge": badge,
        "stats": {
            "total_words": len(words),
            "total_sentences": len(sentences),
            "findings_count": len(linter_findings)
        },
        "lenses": {
            "gptzero_emulator": {
                "risk_score": score_gptzero,
                "mean_ppl": gptzero_res["mean_ppl"],
                "burstiness": gptzero_res["burstiness"],
                "most_robotic_sentence": gptzero_res["most_robotic"],
                "most_human_sentence": gptzero_res["most_human"]
            },
            "gltr_forensics": {
                "risk_score": score_gltr,
                "top_10_pct": gltr_res["top_10_pct"],
                "top_100_pct": gltr_res["top_100_pct"],
                "top_1000_pct": gltr_res["top_1000_pct"],
                "tail_pct": gltr_res["tail_pct"],
                "saturation_pct": gltr_res["saturation_pct"]
            },
            "cadence": {
                "risk_score": score_cadence,
                "mean_sentence_length": mean_len,
                "sentence_length_std": std_len
            },
            "heuristic_linter": {
                "risk_score": score_linter,
                "findings": linter_findings
            },
            "stylometrics": {
                "risk_score": score_stylo,
                "hapax_ratio": stylometrics_res["hapax_ratio"],
                "yule_k": stylometrics_res["yule_k"],
                "mtld": mtld_val
            },
            "anti_bypass": {
                "risk_score": score_bypass,
                "anomalies": anti_bypass_res["anomalies"]
            },
            "readability": readability_res
        },
        "heatmap": gptzero_res["heatmap"]
    }
