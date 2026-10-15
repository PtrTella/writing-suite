#!/usr/bin/env python3
"""
Writing Suite - Live vs Local Precision & Severity Cross-Validation
Confronta i risultati del detector neurale locale (DeBERTa sliding window + trigram context + composite)
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

from core.evaluator_engine import evaluate_document
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
    
    # 3. Chapter 1 Thesis Sample (PyChain Section 1.0 Intro)
    thesis_file = Path("/Users/tella/Workspace/PyChain/thesis_typst/chapters/ch1_intro.typ")
    thesis_content = thesis_file.read_text(encoding="utf-8")
    thesis_sample = (
        "Public package repositories, including the Python Package Index (PyPI) and npm, stream untrusted "
        "third-party code straight onto developer workstations, cloud clusters, and continuous integration pipelines. "
        "Because Python serves as the foundational substrate for modern Artificial Intelligence and Machine Learning "
        "engineering (powering frameworks such as PyTorch, TensorFlow, Hugging Face Transformers, and distributed inference engines), "
        "the software supply chain has become a primary target for sophisticated adversaries. In traditional workflows, "
        "running a single pip install command unpacks pre-compiled binary wheels or executes arbitrary build scripts "
        "from source distributions with ambient user privileges. This operational design creates a structural vulnerability: "
        "application trust is entirely transitive, forcing production systems to inherit the operational habits, "
        "vulnerability lifecycles, and maintainer security postures of every direct and transitive library across their software bill of materials. "
        "We present PyChain, a decentralized package distribution framework that replaces perimeter trust assumptions "
        "with client-verifiable cryptographic proofs. PyChain decouples consensus state from bulk binary storage, "
        "reconciling ledger throughput constraints with large software payloads. The architecture records package namespace ownership, "
        "maintainer identities, and release commitments on an Ethereum Layer-2 smart contract, delegating physical distribution "
        "to IPFS and archival persistence to Software Heritage. We place the verification boundary directly on the developer's workstation: "
        "our client enforces a strict zero-trust perimeter locally by testing each retrieved byte stream against on-chain multihash commitments, "
        "halting execution whenever incoming payload data deviates from the authoritative registry state."
    )

    samples = [
        ("AI Benchmark (CRISPR)", "AI_SYNTHETIC", ai_text),
        ("Human Classic (Shannon 1948)", "HUMAN_ORIGINAL", shannon_text),
        ("Human Classic (Lamport 1978)", "HUMAN_ORIGINAL", lamport_text),
        ("Thesis Ch1 Intro (PyChain Draft)", "THESIS_DRAFT", thesis_sample)
    ]

    print("=" * 100)
    print("WRITING SUITE vs LIVE COMMERCIAL DETECTOR (CLEVERHUMANIZER / COPYLEAKS STANDARD)")
    print("Cross-Validation: Local Multi-Scale DeBERTa + 7-Lens Engine vs Live Chromium External Call")
    print("=" * 100)

    results = []
    for name, cat, text in samples:
        print(f"\n[Testing: {name}] ({len(text.split())} words)...")
        # Local evaluation
        loc_res = evaluate_document(text, target_style="academic_thesis")
        loc_overall = loc_res["overall_ai_score"]
        loc_deberta = loc_res["lenses"]["neural_transformer"]["risk_score"]
        loc_linter = loc_res["lenses"]["heuristic_linter"]["risk_score"]
        loc_cadence = loc_res["lenses"]["cadence"]["risk_score"]
        
        # Live CleverHumanizer evaluation
        live_res = await check_cleverhumanizer(text)
        live_score = live_res.get("overall_ai_score", "ERR")
        live_summary = live_res.get("verdict_summary", live_res.get("error", "N/A"))

        results.append({
            "name": name,
            "category": cat,
            "local_overall": loc_overall,
            "local_deberta": loc_deberta,
            "local_linter": loc_linter,
            "local_cadence": loc_cadence,
            "live_score": live_score,
            "live_summary": live_summary
        })

    print("\n" + "=" * 100)
    print(f"{'Sample Name':<30} | {'Category':<16} | {'Local Overall':<13} | {'Local DeBERTa':<13} | {'Live Clever':<11} | {'Live Verdict'}")
    print("-" * 100)
    for r in results:
        live_str = f"{r['live_score']}%" if isinstance(r['live_score'], (int, float)) else str(r['live_score'])
        print(f"{r['name']:<30} | {r['category']:<16} | {r['local_overall']:>11.1f}% | {r['local_deberta']:>11.1f}% | {live_str:>9} | {r['live_summary']}")
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(run_live_comparison())
