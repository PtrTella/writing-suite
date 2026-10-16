"""
Writing Suite - Unified 4-Pillar Modern Evaluator & Visual Heatmap Engine
Combina:
1. Causal Surprisal & Perplexity (SmolLM2 MPS)
2. Pure Mathematical & Zipfian Stylometry (Zero hardcoded word lists)
3. Dense Semantic Embeddings & Latent Space Geometry
4. Macro Multi-Scale DeBERTa-v3 Transformer
Genera una heatmap visiva per paragrafo con diagnosi mirata e zero linter regex.
"""

import math
import re
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

from .cleaner import clean_markup, extract_sentences, extract_words
from .surprisal import calculate_token_surprisal, analyze_sentences_surprisal, is_causal_available
from .stylome import extract_stylometric_features
from .embedding_classifier import evaluate_embedding_and_stylome
from .neural_detector import predict_text_score, is_neural_available


def split_into_paragraphs(text: str) -> List[str]:
    """Suddivide il testo in paragrafi coerenti escludendo tabelle e macro Typst isolate."""
    raw_paras = re.split(r"\n\s*\n+", text)
    cleaned_paras = []
    for p in raw_paras:
        p_clean = clean_markup(p.strip())
        words = extract_words(p_clean)
        # Ignora blocchi minuscoli (titoli di una riga, didascalie isolate)
        if len(words) >= 15:
            cleaned_paras.append(p_clean)
    return cleaned_paras


def evaluate_paragraph(paragraph: str, para_index: int = 1) -> Dict[str, Any]:
    """Esegue l'audit completo a 4 pilastri su un singolo paragrafo."""
    words = extract_words(paragraph)
    sentences = extract_sentences(paragraph)
    word_count = len(words)

    # 1. Pilastro 1: Causal Surprisal & Perplexity (SmolLM2)
    surprisal_res = calculate_token_surprisal(paragraph)
    ppl = surprisal_res.get("perplexity", 50.0)
    burstiness = surprisal_res.get("burstiness", 3.5)
    p1_risk = surprisal_res.get("risk_score", 30.0)

    # 2. Pilastro 2: Pure Mathematical Stylometry
    stylome_res = extract_stylometric_features(paragraph)
    sigma_len = stylome_res.get("cadence_sigma", 10.0)
    mtld = stylome_res.get("mtld", 70.0)
    p2_risk = stylome_res.get("risk_score", 30.0)

    # 3. Pilastro 3: Dense Latent Embedding & Geometric Dispersion
    emb_res = evaluate_embedding_and_stylome(paragraph)
    p3_risk = emb_res.get("risk_score", 30.0)
    top_drivers = emb_res.get("top_drivers", [])

    # 4. Pilastro 4: DeBERTa-v3 Macro Transformer (se disponibile)
    p4_risk = None
    if is_neural_available():
        try:
            p4_risk = predict_text_score(paragraph)
        except Exception:
            p4_risk = None

    # Calcolo Composite Score ponderato continuo
    if p4_risk is not None:
        composite = (
            (0.35 * p1_risk) +
            (0.30 * p4_risk) +
            (0.20 * p2_risk) +
            (0.15 * p3_risk)
        )
    else:
        composite = (
            (0.45 * p1_risk) +
            (0.35 * p2_risk) +
            (0.20 * p3_risk)
        )

    # Correzione congiunta: se perplessità è eccezionalmente alta (> 100), il testo è denso e umano
    if ppl >= 90.0:
        composite = max(5.0, composite - 15.0)
    elif ppl <= 22.0:
        composite = min(98.0, composite + 15.0)

    final_risk = round(max(0.0, min(100.0, composite)), 1)

    # Identificazione della frase più critica (più prevedibile / più basso surprisal)
    critical_sentence = None
    if len(sentences) > 0 and final_risk >= 30.0:
        s_evals = analyze_sentences_surprisal(sentences)
        if s_evals:
            # Ordina per perplessità crescente (la più prevedibile ha PPL più bassa)
            s_evals.sort(key=lambda s: s["perplexity"])
            worst = s_evals[0]
            if worst["perplexity"] < 45.0:
                critical_sentence = {
                    "text": worst["sentence"],
                    "perplexity": worst["perplexity"],
                    "burstiness": worst["burstiness"],
                    "risk": worst["risk_score"]
                }

    return {
        "index": para_index,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "risk_score": final_risk,
        "perplexity": ppl,
        "burstiness": burstiness,
        "cadence_sigma": sigma_len,
        "mtld": mtld,
        "deberta_score": round(p4_risk, 1) if p4_risk is not None else None,
        "top_drivers": top_drivers,
        "critical_sentence": critical_sentence,
        "snippet": paragraph[:80] + ("..." if len(paragraph) > 80 else "")
    }


def evaluate_document_modern(text: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Esegue l'audit moderno a 4 pilastri sull'intero documento."""
    cleaned = clean_markup(text)
    paragraphs = split_into_paragraphs(cleaned)
    total_words = len(extract_words(cleaned))

    if not paragraphs:
        # Fallback a testo singolo
        single_eval = evaluate_paragraph(cleaned, 1)
        paragraphs_eval = [single_eval]
    else:
        paragraphs_eval = [evaluate_paragraph(p, idx + 1) for idx, p in enumerate(paragraphs)]

    # Media ponderata per lunghezza dei paragrafi
    total_para_words = sum(p["word_count"] for p in paragraphs_eval)
    if total_para_words > 0:
        overall_risk = sum(p["risk_score"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_ppl = sum(p["perplexity"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_burstiness = sum(p["burstiness"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_sigma = sum(p["cadence_sigma"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_mtld = sum(p["mtld"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
    else:
        overall_risk = 20.0
        avg_ppl = 80.0
        avg_burstiness = 4.0
        avg_sigma = 12.0
        avg_mtld = 75.0

    overall_risk = round(overall_risk, 1)

    # Rilevamento hotspot (paragrafi con rischio >= 40%)
    hotspots = [p for p in paragraphs_eval if p["risk_score"] >= 35.0]

    return {
        "file_path": file_path,
        "total_words": total_words,
        "total_paragraphs": len(paragraphs_eval),
        "overall_ai_risk": overall_risk,
        "avg_perplexity": round(avg_ppl, 1),
        "avg_burstiness": round(avg_burstiness, 2),
        "avg_cadence_sigma": round(avg_sigma, 1),
        "avg_mtld": round(avg_mtld, 1),
        "paragraphs": paragraphs_eval,
        "hotspots_count": len(hotspots),
        "hotspots": hotspots
    }


def render_heatmap_cli(report: Dict[str, Any]) -> str:
    """Formatta un report visivo a tabella colorata per il terminale."""
    risk = report["overall_ai_risk"]
    if risk < 25.0:
        badge = "\033[92m🟢 SICURO / UMANO AUTENTICO\033[0m"
    elif risk < 55.0:
        badge = "\033[93m🟡 MISTO / PATTERN PREVEDIBILI\033[0m"
    else:
        badge = "\033[91m🔴 ELEVATO RISCHIO AI\033[0m"

    lines = []
    lines.append("=" * 80)
    lines.append(f"          \033[1mWRITING SUITE - MODERN 4-PILLAR NEURAL & SURPRISAL AUDIT\033[0m")
    lines.append("=" * 80)
    if report.get("file_path"):
        lines.append(f"File: \033[1m{report['file_path']}\033[0m")
    lines.append(f"Parole Totali: {report['total_words']} | Paragrafi Analizzati: {report['total_paragraphs']}")
    lines.append(f"Verdetto Globale: {badge} ({risk}% Rischio AI)")
    lines.append("-" * 80)
    lines.append("METRICHE FONDAMENTALI DEL CORPUS:")
    lines.append(f"  • Causal Perplexity media (PPL) : {report['avg_perplexity']} (PPL > 75 = alta naturalezza)")
    lines.append(f"  • Token Surprisal Burstiness   : {report['avg_burstiness']} (σ sorpresa token)")
    lines.append(f"  • Cadenza Asimmetrica (σ_len)   : {report['avg_cadence_sigma']} parole (target σ ≥ 10.0)")
    lines.append(f"  • Diversità Lessicale (MTLD)   : {report['avg_mtld']} (invariante per lunghezza)")
    lines.append("-" * 80)
    lines.append("MAPPA DI CALORE PARAGRAFO PER PARAGRAFO:")
    lines.append(f"{'§':<4} | {'Parole':<6} | {'PPL':<7} | {'σ_len':<6} | {'DeBERTa':<8} | {'Rischio AI':<10} | {'Status'}")
    lines.append("-" * 80)

    for p in report["paragraphs"]:
        idx_str = f"§{p['index']:02d}"
        p_risk = p["risk_score"]
        deb_str = f"{p['deberta_score']}%" if p['deberta_score'] is not None else "N/A"
        
        if p_risk < 25.0:
            status_col = f"\033[92m🟢 {p_risk:4.1f}%\033[0m"
        elif p_risk < 55.0:
            status_col = f"\033[93m🟡 {p_risk:4.1f}%\033[0m"
        else:
            status_col = f"\033[91m🔴 {p_risk:4.1f}%\033[0m"

        lines.append(f"{idx_str:<4} | {p['word_count']:<6} | {p['perplexity']:<7.1f} | {p['cadence_sigma']:<6.1f} | {deb_str:<8} | {status_col:<19} | {p['snippet']}")

        if p.get("critical_sentence"):
            crit = p["critical_sentence"]
            lines.append(f"     \033[33m└─> Frase più prevedibile (PPL={crit['perplexity']:.1f}):\033[0m")
            lines.append(f"         \"{crit['text']}\"")
            if p.get("top_drivers"):
                lines.append(f"         \033[90m(Driver: {', '.join(p['top_drivers'])})\033[0m")

    lines.append("=" * 80)
    return "\n".join(lines)
