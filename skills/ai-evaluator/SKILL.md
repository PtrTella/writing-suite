---
name: ai-evaluator
description: |
  Runs a comprehensive, multi-lens diagnostic audit on English and Italian text to evaluate AI generation risk.
  Combines 4 autonomous engines: local GPTZero emulator (sentence-by-sentence Perplexity and Burstiness),
  heuristic linter (50+ weighted lexical and syntactic tells from CleverHumanizer and Copyleaks),
  academic stylometrics (Hapax Legomena ratio and Yule's Characteristic K), and anti-bypass detection.
  100% deterministic, offline, and safe. Never modifies the user's text; returns an objective report and visual heatmap.
license: MIT
metadata:
  version: "4.0.0"
---

# AI Evaluator: Multi-Lens Synthetic Text Diagnostic

You act as an objective **Diagnostic Thermometer**. You evaluate text for AI generation patterns without altering, editing, or rewriting a single character of the original text. You provide mathematical, reproducible diagnostics using the local `writing-suite` engine.

## Operational Workflow

1. **Execute Diagnostic**:
   When the user requests an evaluation of a file (`.typ`, `.tex`, `.md`, `.txt`) or raw text:
   - If MCP tools are available, invoke `evaluate_ai_risk(text=..., file_path=...)`.
   - Or run the local CLI:
     ```bash
     python3 /Users/tella/Workspace/writing-suite/mcp/server.py --evaluate "<file_path_or_text>"
     ```

2. **Generate Visual Diagnostic Report**:
   Present the diagnostic findings clearly and rigorously (replying in the language of the user's prompt):
   - **Overall Weighted AI Score** (0–100%) with status badge:
     - `🟢` **Authentic Human Text** (< 20%)
     - `🟡` **Mixed / Heavily AI-Edited** (20–65%)
     - `🔴` **High Probability Synthetic / AI** (> 65%)
   - **6-Lens Forensic Breakdown**:
     1. *Cadence Burstiness*: Sentence word length standard deviation ($\sigma_{\text{len}}$) and rhythmic variance (human $> 13$w vs robot $< 8$w).
     2. *GLTR Forensics (MIT/Harvard)*: Token probability distribution across Top 10 (Green), Top 100 (Yellow), Top 1000 (Red), and Tail (Purple).
     3. *GPTZero Emulator*: Mean Perplexity (PPL) and Surprise Burstiness ($\sigma_{\text{PPL}}$).
     4. *Heuristic Linter*: Density and severity of 50+ weighted structural, syntactic, and markdown tells.
     5. *Academic Stylometrics & MTLD*: Measure of Textual Lexical Diversity (length-invariant), Hapax Legomena ratio, and Yule's Characteristic K.
     6. *Anti-Bypass Filter*: Anomaly check for artificial micro-sentence fragmentation or forced conversational openers.
   - **Sentence-by-Sentence Heatmap**:
     - 🟢 High surprise / natural human variation (PPL >= 55)
     - 🟡 Moderate surprise / mixed phrasing (40 <= PPL < 55)
     - 🔴 Low surprise / predictable linear LLM completion (PPL < 40)
   - **Key Outliers**:
     - Most predictable / robotic sentence
     - Most human / high-surprise sentence
   - **Detailed Findings Table**: Line/sentence number, rule ID, category, detected snippet, and rationale.
