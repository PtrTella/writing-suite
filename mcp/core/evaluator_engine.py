"""
Writing Suite - Evaluator Engine Module
Orchestra i 6 valutatori forensi autonomi calcolando un indice di rischio continuo (senza soglie discrete):
1. Linter Euristico Ponderato (35%): 50+ regole sintattiche, serialità elenchi markdown e costrutti AI
2. Cadence Burstiness (25%): Varianza continua della lunghezza delle frasi (Asimmetria ritmica umana vs monotonia robotica)
3. Predittività Forense (25%): GLTR (Harvard/MIT) a 5 ranghi Zipf + Emulatore Perplessità locale GPTZero
4. Stilometria Accademica & MTLD (15%): Diversità lessicale continua invariante alla lunghezza + Yule's K
5. Analizzatore Anti-Bypass: Rilevamento frammentazione artificiale e prompt injection residui
6. Indici di Leggibilità: Gulpease (Italiano) / Flesch Reading Ease (Inglese) tramite LanguageRegistry

Restituisce output strutturato (JSON compatibile MCP) e heatmap frase per frase.
"""

import math
from typing import Dict, List, Optional, Set
from .cleaner import clean_markup, extract_sentences, extract_words
from .linter import lint_text
from .word_freq import calculate_gltr_profile, calculate_mtld
from .languages import LanguageRegistry
from .metrics import (
    calculate_perplexity_and_burstiness,
    calculate_stylometrics,
    check_anti_bypass
)

STYLE_PROFILES = {
    "academic_thesis": {
        "sigma_0": 10.5,
        "k_cadence": 0.35,
        "tail_midpoint": 14.0,
        "name": "Academic Thesis / Scientific Paper"
    },
    "technical_documentation": {
        "sigma_0": 8.0,
        "k_cadence": 0.40,
        "tail_midpoint": 12.0,
        "name": "Technical Documentation / Developer Manual"
    },
    "essay": {
        "sigma_0": 11.5,
        "k_cadence": 0.35,
        "tail_midpoint": 15.0,
        "name": "Literary Essay / Editorial"
    },
    "conversational": {
        "sigma_0": 9.0,
        "k_cadence": 0.35,
        "tail_midpoint": 10.0,
        "name": "Informal / Conversational Article"
    }
}

def evaluate_document(
    text: str,
    file_path: Optional[str] = None,
    domain: Optional[str] = None,
    domain_terms: Optional[List[str]] = None,
    target_style: str = "academic_thesis",
    language: Optional[str] = None
) -> Dict:
    """Esegue l'audit diagnostico completo multi-prospettiva su testo o file con calibrazione contestuale."""
    cleaned_prose = clean_markup(text)
    sentences = extract_sentences(text)
    words = extract_words(text)

    if len(words) < 15:
        return {
            "error": "Testo troppo breve per una valutazione attendibile (minimo 15-20 parole).",
            "overall_ai_score": 0.0,
            "verdict": "NON_VALUTABILE",
            "verdict_badge": "⚪"
        }

    # Risoluzione profilo stilistico
    profile = STYLE_PROFILES.get(target_style, STYLE_PROFILES["academic_thesis"])

    # Normalizzazione termini di dominio passati dall'agente
    domain_set = {t.lower().strip() for t in domain_terms if t} if domain_terms else set()

    # Selezione o rilevamento automatico della lingua
    if language:
        pack = LanguageRegistry.get(language)
    else:
        pack = LanguageRegistry.detect_language(words)
    lang = pack.lang_code

    # 1. GPTZero emulato (Perplessità locale continua)
    gptzero_res = calculate_perplexity_and_burstiness(sentences)
    score_gptzero = gptzero_res["risk_score"]

    # 2. GLTR Forensics con calibrazione sui termini di dominio
    gltr_res = calculate_gltr_profile(
        words,
        lang=lang,
        domain_terms=domain_set,
        tail_midpoint=profile["tail_midpoint"]
    )
    score_gltr = gltr_res["gltr_risk_score"]

    # 3. Cadence Burstiness (Curva logistica calibrata sul profilo di stile atteso)
    s_lens = [len(extract_words(s)) for s in sentences if len(extract_words(s)) >= 2]
    if len(s_lens) >= 2:
        mean_len = round(sum(s_lens) / len(s_lens), 1)
        var_len = sum((l - mean_len) ** 2 for l in s_lens) / len(s_lens)
        std_len = round(math.sqrt(var_len), 1)
    else:
        mean_len = 15.0
        std_len = 10.0
    
    # Curva logistica continua con parametri del profilo (con clamping numerico anti-overflow)
    z_cadence = max(-60.0, min(60.0, profile["k_cadence"] * (std_len - profile["sigma_0"])))
    score_cadence = round(100.0 / (1.0 + math.exp(z_cadence)), 1)

    # 4. Linter Euristico (Saturazione esponenziale continua)
    linter_findings = lint_text(text)
    total_linter_weight = sum(f["weight"] for f in linter_findings)
    word_count = len(words)
    findings_density = (len(linter_findings) / max(1, word_count)) * 100.0
    z_linter = max(-60.0, min(60.0, -0.10 * total_linter_weight - 0.15 * findings_density))
    score_linter = round(100.0 * (1.0 - math.exp(z_linter)), 1)

    # 5. Stilometria Accademica & MTLD (Curva continua con MTLD bounded)
    stylometrics_res = calculate_stylometrics(words)
    raw_mtld = calculate_mtld(words)
    mtld_val = min(400.0, max(10.0, raw_mtld))
    z_mtld = max(-60.0, min(60.0, 0.04 * (mtld_val - 65.0)))
    score_mtld = 100.0 / (1.0 + math.exp(z_mtld))
    score_stylo = round(0.5 * stylometrics_res["risk_score"] + 0.5 * score_mtld, 1)

    # 6. Anti-Bypass
    anti_bypass_res = check_anti_bypass(text, sentences)
    score_bypass = anti_bypass_res["risk_score"]

    # Punteggio Ponderato Continuo Complessivo:
    # 35% Linter Euristico + 25% Cadence Burstiness + 25% Predittività (GLTR + GPTZero) + 15% Stilometria & MTLD
    predictability_score = (0.5 * score_gptzero) + (0.5 * score_gltr)
    base_score = (
        (0.35 * score_linter) +
        (0.25 * score_cadence) +
        (0.25 * predictability_score) +
        (0.15 * score_stylo)
    )

    if score_bypass > 0:
        base_score = min(100.0, base_score + 0.25 * score_bypass)

    weighted_ai_score = round(min(100.0, max(0.0, base_score)), 1)

    # Verdetto Continuo Calibrato
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

    readability_res = pack.calculate_readability(cleaned_prose, words, sentences)

    return {
        "file_path": file_path,
        "language": lang,
        "language_name": pack.name,
        "overall_ai_score": weighted_ai_score,
        "verdict": verdict,
        "verdict_badge": badge,
        "stats": {
            "total_words": len(words),
            "total_sentences": len(sentences),
            "findings_count": len(linter_findings)
        },
        "lenses": {
            "cadence": {
                "risk_score": score_cadence,
                "mean_sentence_length": mean_len,
                "sentence_length_std": std_len
            },
            "gltr_forensics": {
                "risk_score": score_gltr,
                "top_10_pct": gltr_res["top_10_pct"],
                "top_100_pct": gltr_res["top_100_pct"],
                "top_1000_pct": gltr_res["top_1000_pct"],
                "top_3000_pct": gltr_res["top_3000_pct"],
                "tail_pct": gltr_res["tail_pct"],
                "domain_terms_pct": gltr_res.get("domain_terms_pct", 0.0),
                "saturation_pct": gltr_res["saturation_pct"]
            },
            "gptzero_emulator": {
                "risk_score": score_gptzero,
                "mean_ppl": gptzero_res["mean_ppl"],
                "burstiness": gptzero_res["burstiness"],
                "most_robotic_sentence": gptzero_res["most_robotic"],
                "most_human_sentence": gptzero_res["most_human"]
            },
            "heuristic_linter": {
                "risk_score": score_linter,
                "total_weight": round(total_linter_weight, 1),
                "findings": linter_findings
            },
            "stylometrics": {
                "risk_score": score_stylo,
                "hapax_ratio": stylometrics_res["hapax_ratio"],
                "yule_k": stylometrics_res["yule_k"],
                "mtld": round(mtld_val, 1)
            },
            "anti_bypass": {
                "risk_score": score_bypass,
                "anomalies": anti_bypass_res["anomalies"]
            },
            "readability": readability_res
        },
        "context_calibration": {
            "domain": domain or "general",
            "target_style": profile["name"],
            "domain_terms_count": len(domain_set),
            "domain_terms_sample": sorted(list(domain_set))[:10]
        },
        "heatmap": gptzero_res["heatmap"]
    }
