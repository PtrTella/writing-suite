#!/usr/bin/env python3
"""
Writing Suite - Full Pipeline Verification
Confronta la Bozza Originale (89% AI su CleverHumanizer) con la Versione Riscritta
secondo i principi di prose-humanizer e i fatti tecnici di PyChain.
Valuta sia localmente (DeBERTa + 7 lenti) sia live su CleverHumanizer.ai.
"""

import sys
import json
import asyncio
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "mcp"))

from core.evaluator_engine import evaluate_document
from core.external_detector import check_cleverhumanizer
from core.suggest import suggest_improvements

DRAFT_TEXT = (
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

REWRITTEN_TEXT = (
    "Modern software delivery relies on automated distribution networks: public registries like the Python Package Index "
    "(PyPI) push unverified third-party archives directly into build clusters and developer machines. This pipeline has become "
    "a lucrative attack surface because Python underpins contemporary machine learning engineering, from PyTorch and TensorFlow "
    "runtimes to distributed inference clusters. Standard installations run with ambient operating system privileges. "
    "When a developer issues pip install, the package manager extracts pre-built wheel archives or executes arbitrary setup.py "
    "scripts with the worker's full local permissions: production infrastructure implicitly inherits the security hygiene, "
    "credential lifecycles, and maintainer habits of every upstream dependency in the software bill of materials. "
    "PyChain addresses this systemic exposure by shifting from transport-level trust to client-side cryptographic verification. "
    "The system separates consensus governance from bulk artifact delivery: package namespace ownership, maintainer signing keys, "
    "and release manifests are committed directly to an Ethereum Layer-2 rollup contract, whereas physical archive blobs are routed "
    "across IPFS for content-addressed peer-to-peer retrieval and Software Heritage for archival durability. "
    "Verification occurs locally on the developer workstation before archives touch disk storage: the client resolver computes "
    "the cryptographic multihash of the incoming byte stream and matches it against on-chain registry commitments, terminating "
    "installation immediately if a single byte diverges from published state."
)

async def test_pipeline():
    print("=" * 95)
    print("PIPELINE TEST: ORIGINAL DRAFT vs REWRITTEN TEXT (PROSE-HUMANIZER + FACT GROUNDING)")
    print("=" * 95)

    cases = [
        ("Original Draft (Bozza Iniziale)", DRAFT_TEXT),
        ("Rewritten Text (Riscrittura Umana)", REWRITTEN_TEXT)
    ]

    for label, text in cases:
        print(f"\n>>> [VALUTAZIONE: {label}] ({len(text.split())} parole)")
        
        # 1. Suggerimenti / Diagnosi Frase per Frase
        sug_res = suggest_improvements(text)
        high_risk_sents = [s for s in sug_res["sentences"] if s["ai_probability"] >= 50.0 or len(s["flaws"]) > 0]
        print(f"  Diagnosi Suite: {sug_res['clean_sentences']}/{sug_res['total_sentences']} frasi pulite | Frasi a rischio: {len(high_risk_sents)}")
        for s in high_risk_sents:
            print(f"    - [Frase {s['index']}] {s['badge']} ({s['ai_probability']}%) -> {s['text'][:65]}...")
            for f in s['flaws']:
                print(f"      * {f['type']}: {f['diagnostic']}")

        # 2. Audit Locale (7 Lenti)
        loc_res = evaluate_document(text, target_style="academic_thesis")
        print(f"  Punteggio Locale Overall: {loc_res['overall_ai_score']}% {loc_res['verdict_badge']} | DeBERTa: {loc_res['lenses']['neural_transformer']['risk_score']}% | Cadence: {loc_res['lenses']['cadence']['risk_score']}%")

        # 3. Live CleverHumanizer Call
        print("  Esecuzione chiamata Live a CleverHumanizer.ai (Chromium Headless)...")
        live_res = await check_cleverhumanizer(text)
        live_score = live_res.get("overall_ai_score", "ERR")
        live_summary = live_res.get("verdict_summary", live_res.get("error", "N/A"))
        live_badge = live_res.get("badge", "⚪")
        print(f"  Live CleverHumanizer: {live_score}% {live_badge} -> {live_summary}")
        if live_res.get("flagged_ai_patterns"):
            print(f"  Pattern AI rilevati da CleverHumanizer: {live_res['flagged_ai_patterns']}")

    print("\n" + "=" * 95)

if __name__ == "__main__":
    asyncio.run(test_pipeline())
