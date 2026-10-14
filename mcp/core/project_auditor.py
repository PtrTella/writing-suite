"""
Writing Suite - Project & Corpus Auditor Module
Scans entire directories (theses, paper repositories, book chapters) and produces
comprehensive multi-file audits, cross-referencing citations and formatting tabular reports.
Eliminates the need for external boilerplate or scratch scripts.
"""

import os
from pathlib import Path
from typing import Any, Optional

from .citations import audit_citations
from .cleaner import extract_sentences, extract_words
from .evaluator_engine import evaluate_document
from .linter import lint_text
from .metrics import calculate_readability

SUPPORTED_EXTENSIONS = {".typ", ".tex", ".md", ".markdown", ".txt"}
EXCLUDE_DIRS = {
    ".git",
    ".system_generated",
    "node_modules",
    "target",
    "build",
    "dist",
    "scratch",
}


def audit_directory(
    directory_path: str, bib_path: Optional[str] = None, lang: str = "en"
) -> dict[str, Any]:
    """
    Audits all academic/prose files in a directory recursively or at root level.
    Cross-checks citations against a .bib file if found or provided.
    Returns structured results and a pre-formatted Markdown summary table.
    """
    dir_p = Path(directory_path).resolve()
    if not dir_p.is_dir():
        raise ValueError(f"Path is not a valid directory: {directory_path}")

    # Auto-detect .bib file if not explicitly provided
    if not bib_path:
        bib_candidates = list(dir_p.glob("*.bib")) + list(dir_p.glob("**/*.bib"))
        if bib_candidates:
            bib_path = str(bib_candidates[0])

    # Find all supported files
    all_files: list[Path] = []
    for root, dirs, files in os.walk(dir_p):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for file in files:
            p = Path(root) / file
            if p.suffix.lower() in SUPPORTED_EXTENSIONS and not file.startswith("."):
                all_files.append(p)

    # Sort files naturally (main first or chapters sorted by name)
    def file_sort_key(p: Path):
        name = p.name.lower()
        if "main" in name or "thesis" in name:
            return (0, name)
        if name.startswith(("ch", "cap")):
            return (1, name)
        if name.startswith("app"):
            return (2, name)
        return (3, str(p))

    all_files.sort(key=file_sort_key)

    file_results = []
    total_words = 0
    total_sentences = 0
    weighted_score_accum = 0.0
    weighted_ppl_accum = 0.0

    all_lint_findings = {}
    all_missing_bib = {}
    all_unsupported_claims = {}

    for f in all_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel_path = str(f.relative_to(dir_p))
        eval_res = evaluate_document(content, file_path=rel_path)
        read_res = calculate_readability(content, lang=lang)
        lint_res = lint_text(content)
        cite_res = audit_citations(content, bib_path=bib_path)

        words = len(extract_words(content))
        sents = len(extract_sentences(content))
        ai_score = eval_res.get("overall_ai_score", 0.0)
        ppl = (
            eval_res.get("lenses", {}).get("gptzero_emulator", {}).get("mean_ppl", 0.0)
        )
        burst = (
            eval_res
            .get("lenses", {})
            .get("gptzero_emulator", {})
            .get("burstiness", 0.0)
        )

        total_words += words
        total_sentences += sents
        weighted_score_accum += ai_score * words
        weighted_ppl_accum += ppl * words

        # Collect detailed findings
        if lint_res:
            all_lint_findings[rel_path] = lint_res
        if cite_res.get("missing_in_bib"):
            all_missing_bib[rel_path] = cite_res["missing_in_bib"]
        if cite_res.get("unsupported_claims"):
            all_unsupported_claims[rel_path] = cite_res["unsupported_claims"]

        file_results.append({
            "file": f.name,
            "rel_path": rel_path,
            "words": words,
            "sentences": sents,
            "ai_score": ai_score,
            "badge": eval_res.get("verdict_badge", "🟢"),
            "verdict": eval_res.get("verdict", "N/A"),
            "ppl": ppl,
            "burstiness": burst,
            "flesch": read_res.get("flesch_reading_ease"),
            "gulpease": read_res.get("gulpease"),
            "lint_count": len(lint_res),
            "missing_bib_count": len(cite_res.get("missing_in_bib", [])),
            "unsupported_count": len(cite_res.get("unsupported_claims", [])),
        })

    corpus_ai_score = round(weighted_score_accum / max(1, total_words), 1)
    corpus_mean_ppl = round(weighted_ppl_accum / max(1, total_words), 1)

    if corpus_ai_score < 20.0:
        corpus_verdict = "Authentic Human Writing"
        corpus_badge = "🟢"
    elif corpus_ai_score < 65.0:
        corpus_verdict = "Mixed / Heavily AI-Edited"
        corpus_badge = "🟡"
    else:
        corpus_verdict = "High Probability Synthetic / AI"
        corpus_badge = "🔴"

    # Generate Markdown Summary Table
    table_lines = [
        f"| {'File / Chapter':<35} | {'AI Risk %':<10} | {'PPL':<6} | {'Burst':<6} | {'Readability':<11} | {'Lints':<5} | {'Citations':<12} |",
        f"|:{'-' * 35}-|:{'-' * 10}:|:{'-' * 6}:|:{'-' * 6}:|:{'-' * 11}:|:{'-' * 5}:|:{'-' * 12}:|",
    ]

    for item in file_results:
        read_val = (
            f"G:{item['gulpease']:.1f}"
            if item["gulpease"] is not None
            else f"F:{item['flesch']:.1f}"
        )
        cite_val = f"bib:{item['missing_bib_count']}, uns:{item['unsupported_count']}"
        table_lines.append(
            f"| `{item['rel_path']:<33}` | {item['badge']} {item['ai_score']:>5.1f}% | {item['ppl']:>5.1f} | {item['burstiness']:>5.1f} | {read_val:>10} | {item['lint_count']:>5} | {cite_val:<12} |"
        )

    summary_table = "\n".join(table_lines)

    return {
        "directory": str(dir_p),
        "bib_path": bib_path,
        "total_files": len(file_results),
        "total_words": total_words,
        "total_sentences": total_sentences,
        "corpus_ai_score": corpus_ai_score,
        "corpus_mean_ppl": corpus_mean_ppl,
        "corpus_badge": corpus_badge,
        "corpus_verdict": corpus_verdict,
        "summary_table": summary_table,
        "files": file_results,
        "detailed_findings": {
            "lints": all_lint_findings,
            "missing_bib": all_missing_bib,
            "unsupported_claims": all_unsupported_claims,
        },
    }
