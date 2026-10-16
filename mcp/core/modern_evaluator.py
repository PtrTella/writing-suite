"""
Writing Suite - Modular Multi-Engine Modern Evaluator & Prescriptive Heatmap
Orchestra i motori diagnostici indipendenti:
1. Cadence & Rhythm Engine (σ_len, staccato, pause)
2. Causal Surprisal Engine (SmolLM2 MPS Token Perplexity & Burstiness)
3. Syntax & AI Patterns Engine (Triadi, antitesi simmetriche, em-dash, cliché)
4. Lexical Diversity Engine (MTLD, verbi astratti ridondanti)
5. Neural Macro Transformer (DeBERTa-v3)
6. External Multi-Detector Consensus (Sapling + CleverHumanizer + ZeroGPT)
Genera una matrice disaggregata, prescrizioni chirurgiche e cross-validazione live.
"""

import math
import re
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

from .cleaner import clean_markup, extract_sentences, extract_words
from .engines import evaluate_paragraph_vector, analyze_external


def split_into_paragraphs(text: str) -> List[str]:
    """
    Suddivide il testo in paragrafi coerenti escludendo tabelle e macro Typst isolate.
    Raggruppa elenchi puntati consecutivi in un unico blocco logico integrato.
    """
    raw_paras = re.split(r"\n\s*\n+", text)
    merged_paras = []
    current_list_block = []

    for p in raw_paras:
        p_strip = p.strip()
        # Se il blocco inizia con un marcatore di elenco puntato o numerato
        if re.match(r"^[-*+•]|\b\d+\.\s+", p_strip):
            current_list_block.append(p_strip)
        else:
            if current_list_block:
                merged_paras.append("\n".join(current_list_block))
                current_list_block = []
            if p_strip:
                merged_paras.append(p_strip)

    if current_list_block:
        merged_paras.append("\n".join(current_list_block))

    cleaned_paras = []
    for p in merged_paras:
        p_clean = clean_markup(p.strip())
        words = extract_words(p_clean)
        # Ignora blocchi minuscoli (titoli di una riga, didascalie isolate)
        if len(words) >= 15:
            cleaned_paras.append(p_clean)
    return cleaned_paras



def evaluate_paragraph(
    paragraph: str,
    para_index: int = 1,
    run_external: bool = False
) -> Dict[str, Any]:
    """Esegue l'audit diagnostico completo su un singolo paragrafo."""
    vec_res = evaluate_paragraph_vector(paragraph, para_index, run_external=run_external)
    vec = vec_res["vector"]

    cadence = vec.get("cadence", {})
    surprisal = vec.get("surprisal", {})
    syntax = vec.get("syntax", {})
    lexical = vec.get("lexical", {})
    neural = vec.get("neural", {})
    external = vec.get("external", {})

    return {
        "index": para_index,
        "word_count": vec_res["word_count"],
        "sentence_count": vec_res["sentence_count"],
        "risk_score": vec_res["risk_score"],
        "perplexity": surprisal.get("perplexity", 50.0),
        "burstiness": surprisal.get("burstiness", 3.5),
        "binoculars_ratio": surprisal.get("binoculars_ratio", 1.0),
        "top1_gap": surprisal.get("top1_gap", 2.5),
        "cadence_sigma": cadence.get("cadence_sigma", 0.0),
        "punctuation_entropy": cadence.get("punctuation_entropy", 1.5),
        "mtld": lexical.get("mtld", 50.0),
        "hapax_ratio": lexical.get("hapax_ratio", 0.90),
        "deberta_score": neural.get("score"),
        "top_drivers": syntax.get("patterns_detected", []) + cadence.get("signals", []),
        "critical_sentence": vec_res.get("critical_sentence"),
        "snippet": vec_res["snippet"],
        "vector": vec,
        "prescriptions": vec_res.get("prescriptions", [])
    }


def evaluate_document_modern(
    text: str,
    file_path: Optional[str] = None,
    cross_validate: bool = False
) -> Dict[str, Any]:
    """Esegue l'audit diagnostico modulare sull'intero documento."""
    cleaned = clean_markup(text)
    paragraphs = split_into_paragraphs(cleaned)
    total_words = len(extract_words(cleaned))

    if not paragraphs:
        single_eval = evaluate_paragraph(cleaned, 1)
        paragraphs_eval = [single_eval]
    else:
        paragraphs_eval = [evaluate_paragraph(p, idx + 1) for idx, p in enumerate(paragraphs)]

    # Media ponderata per lunghezza dei paragrafi
    total_para_words = sum(p["word_count"] for p in paragraphs_eval)
    if total_para_words > 0:
        mean_risk = sum(p["risk_score"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_ppl = sum(p["perplexity"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_burstiness = sum(p["burstiness"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_binoculars = sum(p["binoculars_ratio"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_top1_gap = sum(p["top1_gap"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_sigma = sum(p["cadence_sigma"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_punc_entropy = sum(p["punctuation_entropy"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_mtld = sum(p["mtld"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)
        avg_hapax = sum(p["hapax_ratio"] * (p["word_count"] / total_para_words) for p in paragraphs_eval)

        # Aggregazione Multi-Scala
        sorted_risks = sorted([p["risk_score"] for p in paragraphs_eval])
        p80_idx = min(len(sorted_risks) - 1, int(len(sorted_risks) * 0.80))
        p80_risk = sorted_risks[p80_idx]
        worst_risk = sorted_risks[-1]

        if worst_risk >= 50.0:
            overall_risk = (0.45 * mean_risk) + (0.35 * p80_risk) + (0.20 * worst_risk)
        else:
            overall_risk = (0.70 * mean_risk) + (0.30 * p80_risk)
    else:
        overall_risk = 20.0
        avg_ppl = 80.0
        avg_burstiness = 4.0
        avg_binoculars = 1.20
        avg_top1_gap = 2.80
        avg_sigma = 12.0
        avg_punc_entropy = 1.80
        avg_mtld = 75.0
        avg_hapax = 0.95

    overall_risk = round(overall_risk, 1)

    # Rilevamento hotspot (paragrafi che richiedono attenzione)
    hotspots = [p for p in paragraphs_eval if p["risk_score"] >= 35.0 or len(p["prescriptions"]) >= 2]

    # Campionamento mirato di Cross-Validazione Esterna (se richiesto)
    cross_val_samples = []
    if cross_validate and paragraphs:
        # Seleziona i 2 paragrafi più critici o controversi
        sorted_candidates = sorted(paragraphs_eval, key=lambda x: (len(x["prescriptions"]), x["risk_score"]), reverse=True)
        top_candidates = sorted_candidates[:2]
        for cand in top_candidates:
            idx = cand["index"] - 1
            if 0 <= idx < len(paragraphs):
                p_text = paragraphs[idx]
                ext_res = analyze_external(p_text)
                cross_val_samples.append({
                    "index": cand["index"],
                    "snippet": cand["snippet"],
                    "internal_risk": cand["risk_score"],
                    "vector": cand["vector"],
                    "external_res": ext_res
                })

    return {
        "file_path": file_path,
        "total_words": total_words,
        "total_paragraphs": len(paragraphs_eval),
        "overall_ai_risk": overall_risk,
        "avg_perplexity": round(avg_ppl, 1),
        "avg_burstiness": round(avg_burstiness, 2),
        "avg_binoculars_ratio": round(avg_binoculars, 2),
        "avg_top1_gap": round(avg_top1_gap, 2),
        "avg_cadence_sigma": round(avg_sigma, 1),
        "avg_punctuation_entropy": round(avg_punc_entropy, 2),
        "avg_mtld": round(avg_mtld, 1),
        "avg_hapax_ratio": round(avg_hapax, 3),
        "paragraphs": paragraphs_eval,
        "hotspots_count": len(hotspots),
        "hotspots": hotspots,
        "cross_validation_samples": cross_val_samples
    }



def _get_badge(status: str) -> str:
    if status == "safe":
        return "\033[92m🟢\033[0m"
    elif status == "warning":
        return "\033[93m🟡\033[0m"
    else:
        return "\033[91m🔴\033[0m"


def render_heatmap_cli(report: Dict[str, Any]) -> str:
    """Formatta un report visivo multidimensionale a motori disaggregati per il terminale."""
    risk = report["overall_ai_risk"]
    if risk < 25.0:
        badge = "\033[92m🟢 SICURO / UMANO AUTENTICO\033[0m"
    elif risk < 50.0:
        badge = "\033[93m🟡 MISTO / PATTERN PREVEDIBILI\033[0m"
    else:
        badge = "\033[91m🔴 ELEVATO RISCHIO AI\033[0m"

    lines = []
    lines.append("=" * 86)
    lines.append(f"          \033[1mWRITING SUITE - DISAGGREGATED MULTI-ENGINE DIAGNOSTIC AUDIT\033[0m")
    lines.append("=" * 86)
    if report.get("file_path"):
        lines.append(f"File: \033[1m{report['file_path']}\033[0m")
    lines.append(f"Parole Totali: {report['total_words']} | Paragrafi Analizzati: {report['total_paragraphs']}")
    lines.append(f"Verdetto Globale Stimato: {badge} ({risk}% Rischio AI)")
    lines.append("-" * 86)
    lines.append("METRICHE FONDAMENTALI DEL CORPUS (SOTA Multi-Engine):")
    lines.append(f"  • Causal Perplexity media (PPL) : {report['avg_perplexity']} (PPL > 75 = alta naturalezza)")
    lines.append(f"  • Token Surprisal Burstiness   : {report['avg_burstiness']} (σ sorpresa token)")
    lines.append(f"  • Ratio Binoculars (PPL/Entr.) : {report.get('avg_binoculars_ratio', 1.0):.2f} (B > 1.05 = asimmetria umana naturale)")
    lines.append(f"  • Curvatura Top-1 Gap (Detect) : {report.get('avg_top1_gap', 2.5):.2f} (Gap > 2.5 = divergenza da greedy path)")
    lines.append(f"  • Cadenza Asimmetrica (σ_len)   : {report['avg_cadence_sigma']} parole (target σ ≥ 10.0)")
    lines.append(f"  • Entropia Punteggiatura (H_p) : {report.get('avg_punctuation_entropy', 1.8):.2f} bit (H ≥ 1.6 = respiro articolato)")
    lines.append(f"  • Diversità Lessicale (MTLD)   : {report['avg_mtld']} (invariante per lunghezza)")
    lines.append(f"  • Hapax Legomena (Coda Zipf)   : {report.get('avg_hapax_ratio', 0.90):.1%} (V1/N > 90% = vocabolario ricco non troncato)")
    lines.append("-" * 86)
    lines.append("MATRICE DIAGNOSTICA DISAGGREGATA PER PARAGRAFO:")

    lines.append(f"{'§':<4} | {'Parole':<6} | {'Cadenza':<7} | {'Surprisal':<9} | {'Sintassi':<8} | {'DeBERTa':<8} | {'Status':<10} | {'Snippet'}")
    lines.append("-" * 86)

    for p in report["paragraphs"]:
        idx_str = f"§{p['index']:02d}"
        p_risk = p["risk_score"]
        deb_val = p.get("deberta_score")
        deb_str = f"{deb_val:.1f}%" if deb_val is not None else "N/A"

        vec = p.get("vector", {})
        cad_b = _get_badge(vec.get("cadence", {}).get("status", "safe"))
        sur_b = _get_badge(vec.get("surprisal", {}).get("status", "safe"))
        syn_b = _get_badge(vec.get("syntax", {}).get("status", "safe"))
        deb_b = "\033[92m🟢\033[0m" if (deb_val is None or deb_val < 35) else ("\033[93m🟡\033[0m" if deb_val < 65 else "\033[91m🔴\033[0m")

        if p_risk < 25.0:
            status_col = f"\033[92m🟢 {p_risk:4.1f}%\033[0m"
        elif p_risk < 50.0:
            status_col = f"\033[93m🟡 {p_risk:4.1f}%\033[0m"
        else:
            status_col = f"\033[91m🔴 {p_risk:4.1f}%\033[0m"

        lines.append(
            f"{idx_str:<4} | {p['word_count']:<6} | {cad_b} {p['cadence_sigma']:4.1f} | "
            f"{sur_b} {p['perplexity']:5.1f} | {syn_b} {len(vec.get('syntax',{}).get('signals',[])):<6} | "
            f"{deb_b} {deb_str:<6} | {status_col:<19} | {p['snippet']}"
        )

        # Se ci sono prescrizioni chirurgiche attive, stampale subito sotto il paragrafo
        if p.get("prescriptions"):
            lines.append(f"     \033[1;33m└─> CHIRURGIA DEL TESTO (Prescrizioni Operative):\033[0m")
            for pres in p["prescriptions"][:3]:
                lines.append(f"         \033[33m• {pres}\033[0m")
            if p.get("critical_sentence"):
                crit = p["critical_sentence"]
                lines.append(f"         \033[90m[Frase più prevedibile (PPL={crit['perplexity']:.1f}): \"{crit['text'][:75]}...\"]\033[0m")

    # Sezione Cross-Validazione Live (se campionata)
    if report.get("cross_validation_samples"):
        lines.append("\n" + "=" * 86)
        lines.append("     \033[1;36mCROSS-VALIDAZIONE ESTERNA LIVE (Campioni Critici su Rete)\033[0m")
        lines.append("=" * 86)
        for s in report["cross_validation_samples"]:
            ext = s["external_res"]
            score = ext.get("score", "N/A")
            dets = ext.get("detectors", {})
            sap = dets.get("sapling", {}).get("overall_ai_score", "N/A")
            clev = dets.get("cleverhumanizer", {}).get("overall_ai_score", "N/A")
            zero = dets.get("zerogpt", {}).get("overall_ai_score", "N/A")

            lines.append(f"Paragrafo §{s['index']:02d}: \"{s['snippet']}\"")
            lines.append(f"  • Rischio Interno Combinato : {s['internal_risk']}%")
            lines.append(f"  • Consenso Esterno Live    : \033[1m{score}%\033[0m [Sapling: {sap}% | Clever: {clev}% | ZeroGPT: {zero}%]")
            if ext.get("signals"):
                for sig in ext["signals"][:2]:
                    lines.append(f"    └─ {sig}")
            lines.append("-" * 86)

    lines.append("=" * 86)
    return "\n".join(lines)
