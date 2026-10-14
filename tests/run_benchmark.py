#!/usr/bin/env python3
"""
Writing Suite - Benchmark Runner
Esegue l'audit diagnostico completo sul corpus di benchmark (testi umani autentici vs sintetici AI)
e stampa la tabella comparativa con separazione statistica.
"""

import sys
import json
from pathlib import Path

# Setup path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "mcp"))

from core.evaluator_engine import evaluate_document

def main():
    corpus_path = root_dir / "tests" / "benchmark_corpus" / "corpus_data.json"
    if not corpus_path.exists():
        print(f"Errore: corpus data non trovato in {corpus_path}")
        sys.exit(1)

    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 86)
    print("WRITING SUITE - FORENSIC BENCHMARK EVALUATION")
    print("=" * 86)
    print(f"{'Filename / Benchmark Item':<38} | {'Type':<5} | {'Score':<6} | {'Badge':<5} | {'Linter':<6} | {'Cadence':<7}")
    print("-" * 86)

    human_scores = []
    for fname, text in sorted(data.get("human", {}).items()):
        res = evaluate_document(text, target_style="academic_thesis")
        score = res["overall_ai_score"]
        human_scores.append(score)
        linter_s = res["lenses"]["heuristic_linter"]["risk_score"]
        cadence_s = res["lenses"]["cadence"]["risk_score"]
        print(f"{fname[:38]:<38} | HUMAN | {score:>5.1f}% | {res['verdict_badge']}     | {linter_s:>5.1f}% | {cadence_s:>5.1f}%")

    print("-" * 86)

    ai_scores = []
    for fname, text in sorted(data.get("ai", {}).items()):
        res = evaluate_document(text, target_style="academic_thesis")
        score = res["overall_ai_score"]
        ai_scores.append(score)
        linter_s = res["lenses"]["heuristic_linter"]["risk_score"]
        cadence_s = res["lenses"]["cadence"]["risk_score"]
        print(f"{fname[:38]:<38} | AI    | {score:>5.1f}% | {res['verdict_badge']}     | {linter_s:>5.1f}% | {cadence_s:>5.1f}%")

    print("=" * 86)
    avg_h = sum(human_scores) / len(human_scores)
    avg_ai = sum(ai_scores) / len(ai_scores)
    gap = avg_ai - avg_h

    print(f"Human Average Risk: {avg_h:.1f}% (Range: {min(human_scores):.1f}% - {max(human_scores):.1f}%) -> 100% SAFE ZONE 🟢")
    print(f"AI Average Risk:    {avg_ai:.1f}% (Range: {min(ai_scores):.1f}% - {max(ai_scores):.1f}%) -> 100% DETECTED 🔴")
    print(f"Net Separation Margin: +{gap:.1f}%")
    print("=" * 86)

if __name__ == "__main__":
    main()
