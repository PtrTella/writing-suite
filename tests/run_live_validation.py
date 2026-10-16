#!/usr/bin/env python3
"""
Writing Suite - Live vs Local Precision & Severity Cross-Validation
Confronta i risultati del motore neurale e causale a 4 pilastri locale
con le chiamate live a CleverHumanizer.ai (Chromium Headless) su:
1. Sample AI puro (benchmark corpus)
2. Sample Umano accademico autentico (benchmark corpus)
3. Sample Tesi humanized (PyChain ch1_intro.typ)
"""

import sys
import json
import asyncio
from pathlib import Path

# Paths
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "mcp"))

from core.modern_evaluator import evaluate_document_modern
from core.external_detector import check_cleverhumanizer

async def run_live_comparison():
    corpus_path = root_dir / "tests" / "benchmark_corpus" / "corpus_data.json"
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    # 1. AI sample (English)
    ai_text = corpus["ai"]["ai_bio_crispr.txt"]
    # 2. Human samples (English)
    shannon_text = corpus["human"]["human_math_shannon_1948.txt"]
    lamport_text = corpus["human"]["human_cs_lamport_1978.txt"]
    
    # 3. Chapter 1 Thesis Sample (PyChain Section 1.0 Intro certified)
    thesis_file = Path("/Users/tella/Workspace/PyChain/thesis_typst/chapters/ch1_intro.typ")
    thesis_content = thesis_file.read_text(encoding="utf-8")
    thesis_sample = (
        "Public package repositories such as the Python Package Index (PyPI) and npm distribute third-party archives "
        "directly to developer machines, enterprise networks, and cloud clusters. Python serves as the foundational substrate "
        "for modern artificial intelligence frameworks, including PyTorch, TensorFlow, Hugging Face Transformers, and distributed inference engines. "
        "As a consequence, the software supply chain has become a primary target for sophisticated threat actors. Traditional workflows require "
        "running a single pip install command that unpacks pre-compiled binary wheels or executes arbitrary build scripts from source archives with ambient privileges."
    )

    samples = [
        ("AI Benchmark (CRISPR)", "AI_SYNTHETIC", ai_text),
        ("Human Classic (Shannon 1948)", "HUMAN_ORIGINAL", shannon_text),
        ("Human Classic (Lamport 1978)", "HUMAN_ORIGINAL", lamport_text),
        ("Thesis Ch1 Intro (PyChain §01)", "THESIS_CERTIFIED", thesis_sample)
    ]

    print("=" * 105)
    print("WRITING SUITE vs LIVE COMMERCIAL DETECTOR (CLEVERHUMANIZER / COPYLEAKS STANDARD)")
    print("Cross-Validation: Modern 4-Pillar Neural Engine vs Live Chromium External Call")
    print("=" * 105)

    results = []
    for name, cat, text in samples:
        print(f"\n[Testing: {name}] ({len(text.split())} words)...")
        # Local evaluation
        loc_res = evaluate_document_modern(text)
        loc_overall = loc_res["overall_ai_risk"]
        loc_ppl = loc_res["avg_perplexity"]
        loc_sigma = loc_res["avg_cadence_sigma"]
        
        # Live CleverHumanizer evaluation
        live_res = await check_cleverhumanizer(text)
        live_score = live_res.get("overall_ai_score", "ERR")
        live_summary = live_res.get("verdict_summary", live_res.get("error", "N/A"))

        results.append({
            "name": name,
            "category": cat,
            "local_overall": loc_overall,
            "local_ppl": loc_ppl,
            "local_sigma": loc_sigma,
            "live_score": live_score,
            "live_summary": live_summary
        })

    print("\n" + "=" * 105)
    print(f"{'Sample Name':<30} | {'Category':<16} | {'Local Risk':<11} | {'Local PPL':<10} | {'Live Clever':<11} | {'Live Verdict'}")
    print("-" * 105)
    for r in results:
        live_str = f"{r['live_score']}%" if isinstance(r['live_score'], (int, float)) else str(r['live_score'])
        print(f"{r['name']:<30} | {r['category']:<16} | {r['local_overall']:>9.1f}% | {r['local_ppl']:>9.1f} | {live_str:>9} | {r['live_summary']}")
    print("=" * 105)

if __name__ == "__main__":
    asyncio.run(run_live_comparison())
