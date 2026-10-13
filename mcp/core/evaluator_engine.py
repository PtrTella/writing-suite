"""
Writing Suite - Evaluator Engine Module
Orchestra i 4 valutatori autonomi e calcola il punteggio unificato ponderato di rischio AI:
1. Emulatore GPTZero Locale (35%)
2. Linter Euristico Ponderato (35%)
3. Stilometria Accademica (15%)
4. Modulo Anti-Bypass (15%)
Restituisce output JSON strutturato e report formattato in puro Markdown.
"""

from .cleaner import clean_markup, extract_sentences, extract_words
from .linter import lint_text
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

    # 1. GPTZero emulato
    gptzero_res = calculate_perplexity_and_burstiness(sentences)
    score_gptzero = gptzero_res["risk_score"]

    # 2. Linter Euristico
    linter_findings = lint_text(text)
    total_linter_weight = sum(f["weight"] for f in linter_findings)
    # Calibrazione continua: 0 findings = 0%, 1 finding medio ~15%, 4+ findings = 80-100%
    score_linter = min(100.0, round(total_linter_weight * 12.5, 1))

    # 3. Stilometria
    stylometrics_res = calculate_stylometrics(words)
    score_stylo = stylometrics_res["risk_score"]

    # 4. Anti-Bypass
    anti_bypass_res = check_anti_bypass(text, sentences)
    score_bypass = anti_bypass_res["risk_score"]

    # Punteggio Ponderato Complessivo
    weighted_ai_score = round(
        (0.35 * score_gptzero) +
        (0.35 * score_linter) +
        (0.15 * score_stylo) +
        (0.15 * score_bypass),
        1
    )

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

    readability_res = calculate_readability(cleaned_prose, lang="it" if any(w in words for w in ["di", "il", "la", "che", "per"]) else "en")

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
            "heuristic_linter": {
                "risk_score": score_linter,
                "findings": linter_findings
            },
            "stylometrics": {
                "risk_score": score_stylo,
                "hapax_ratio": stylometrics_res["hapax_ratio"],
                "yule_k": stylometrics_res["yule_k"]
            },
            "anti_bypass": {
                "risk_score": score_bypass,
                "anomalies": anti_bypass_res["anomalies"]
            },
            "readability": readability_res
        },
        "heatmap": gptzero_res["heatmap"]
    }
