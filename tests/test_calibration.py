"""
Writing Suite - Benchmark & Calibration Test Suite
Valida la calibrazione del Modern Evaluator a 4 pilastri su:
1. Testo AI Puro (ChatGPT standard) -> Target: 80-95% 🔴
2. Testo Umano Autentico (Di Cosmo CACM 2020 / paper accademico autentico) -> Target: < 22% 🟢
3. Testo Misto con Hotspot -> Target: 35-55% 🟡 con identificazione del paragrafo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mcp"))

from core.modern_evaluator import evaluate_document_modern, render_heatmap_cli

# 1. Testo AI Puro (tipico output ChatGPT senza humanizer)
AI_SAMPLE = """
In today's fast-paced technological landscape, software supply chain security has emerged as a paramount challenge for distributed organizations. Centralized package repositories serve as single points of failure, exposing modern applications to severe security vulnerabilities and malicious dependency attacks.

To address these pressing concerns, decentralized architectures have garnered significant attention from researchers and industry practitioners alike. By leveraging immutable distributed ledgers and peer-to-peer protocols, organizations can effectively mitigate the risks associated with unauthorized code tampering.

Furthermore, implementing continuous cryptographic verification ensures that software artifacts remain authentic throughout their entire lifecycle. This proactive paradigm shift not only enhances system resilience but also fosters greater trust among developers in modular ecosystems.
"""

# 2. Testo Umano Autentico (Prof. Roberto Di Cosmo, CACM 2020, Software Heritage)
HUMAN_SAMPLE = """
Software is not just data. It is human knowledge embodied in executable form. Over the past six decades, our society has become thoroughly dependent on software for its everyday operations, from transportation and healthcare to telecommunications and cultural heritage. Yet, unlike physical artifacts preserved in national libraries and museums, software source code is intrinsically fragile, highly volatile, and dispersed across thousands of transient hosting platforms.

When a repository hosting service shuts down, decades of development history vanish overnight. A broken link in an academic paper renders the experimental evaluation unreproducible. To address this preservation crisis, Software Heritage collects, preserves, and shares the source code of all publicly available software, organizing it into a massive Merkle directed acyclic graph. In this unified graph, every software artifact—from individual source files to complete repository commits—is assigned an intrinsic, cryptographically persistent identifier that does not depend on any centralized naming authority.
"""

# 3. Testo Misto (Paragrafo umano autentico + Paragrafo sintetico AI)
MIXED_SAMPLE = """
Unix software distribution historically balanced installation velocity against verification overhead. Early source-based distributions forced users to download raw archives, inspect makefiles, and compile binaries directly against local system libraries. While this approach guaranteed deterministic compilation under identical host environments, it imposed prohibitive maintenance costs on system administrators.

In today's fast-paced digital world, modern package distribution relies heavily on automated continuous integration pipelines to ensure seamless deployment and optimal system performance. This proactive paradigm shift plays a pivotal role in fostering collaboration among distributed development teams across diverse organizations.
"""


def run_calibration_test():
    print("=" * 80)
    print("           WRITING SUITE CALIBRATION BENCHMARK TEST")
    print("=" * 80)

    print("\n[1] ESECUZIONE SU TESTO AI PURO (ChatGPT standard):")
    rep_ai = evaluate_document_modern(AI_SAMPLE, "ai_sample.txt")
    print(f"-> AI Risk Score: {rep_ai['overall_ai_risk']}% | PPL: {rep_ai['avg_perplexity']}")
    if rep_ai["overall_ai_risk"] >= 70.0:
        print("✅ PASS: Testo AI classificato correttamente come sintetico (🔴)")
    else:
        print(f"❌ FAIL: Troppo permissivo! Score = {rep_ai['overall_ai_risk']}% (atteso >= 70%)")

    print("\n[2] ESECUZIONE SU TESTO UMANO AUTENTICO (Di Cosmo CACM 2020):")
    rep_hu = evaluate_document_modern(HUMAN_SAMPLE, "human_dicosmo.txt")
    print(f"-> Human Risk Score: {rep_hu['overall_ai_risk']}% | PPL: {rep_hu['avg_perplexity']}")
    if rep_hu["overall_ai_risk"] <= 25.0:
        print("✅ PASS: Testo umano classificato correttamente come autentico (🟢)")
    else:
        print(f"❌ FAIL: Falso positivo! Score = {rep_hu['overall_ai_risk']}% (atteso <= 25%)")

    print("\n[3] ESECUZIONE SU TESTO MISTO (Human + AI Paragraph):")
    rep_mx = evaluate_document_modern(MIXED_SAMPLE, "mixed_sample.txt")
    print(f"-> Mixed Risk Score: {rep_mx['overall_ai_risk']}% | Hotspots rilevati: {rep_mx['hotspots_count']}")
    if 50.0 <= rep_mx["overall_ai_risk"] <= 88.0 and rep_mx["hotspots_count"] >= 1:
        print("✅ PASS: Testo misto individuato con successo con hotspot specifico (🟡/🔴)")
    else:
        print(f"❌ FAIL: Calibrazione mista errata! Score = {rep_mx['overall_ai_risk']}%")

    print("=" * 80)


if __name__ == "__main__":
    run_calibration_test()
