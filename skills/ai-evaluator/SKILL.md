---
name: ai-evaluator
description: |
  Runs a comprehensive, multi-lens diagnostic audit on English, Italian, or any natural language text to evaluate AI generation risk.
  Combines 6 autonomous engines: continuous GLTR forensics (Zipf rank distribution), cadence burstiness (sentence length std dev),
  local GPTZero emulator (sentence surprisal), heuristic linter (50+ weighted lexical and syntactic tells),
  academic stylometrics (MTLD and Yule's K), and anti-bypass detection.
  Supports dynamic context injection (domain glossary whitelisting and style profiling) without model bias.
  100% deterministic, offline, and safe. Never modifies the user's text; returns an objective report and visual heatmap.
license: MIT
metadata:
  version: "4.2.0"
---

# AI Evaluator: Multi-Lens Synthetic Text Diagnostic

You act as an objective **Diagnostic Thermometer**. You evaluate text for AI generation patterns without altering, editing, or rewriting a single character of the original text. You provide mathematical, reproducible diagnostics using the local `writing-suite` engine.

---

## 🎯 Context-Injection Protocol (Anti-Bias & Domain Whitelisting)

To prevent domain-specific jargon (e.g. *zk-SNARKs*, *cholecystectomy*, *res judicata*) from artificially skewing the statistical Zipf tail or perplexity metrics, follow this two-step cognitive protocol:

1. **Objective Domain & Glossary Extraction**:
   * Inspect the title, headings, and abstract to identify the **domain** (e.g. `cryptography`, `blockchain`, `biomedical`, `legal`, `machine_learning`, `general`).
   * **Crucial Anti-Bias Rule**: Do NOT evaluate whether the text "sounds like AI" during this step. Do NOT select words to manipulate the score. Strictly extract 5–15 **neutral domain technical terms, proper nouns, and acronyms** that define the topic (e.g., `["ERC-4337", "zk-SNARKs", "Sepolia", "Merkle DAG", "calldata", "EVM"]`).
   * These terms will be recognized by the deterministic engine as legitimate domain vocabulary, ensuring the forensic evaluation focuses on the **syntactic glue, cadence, and connecting prose**.

2. **Select Target Style**:
   * `academic_thesis`: Master's theses, academic dissertations, scientific journal papers ($\sigma_0 = 10.5$).
   * `technical_documentation`: API specifications, READMEs, developer documentation ($\sigma_0 = 8.0$).
   * `essay`: Literary essays, opinion editorials, articles ($\sigma_0 = 11.5$).
   * `conversational`: Informal blog posts, conversational dialogues ($\sigma_0 = 9.0$).

---

## ⚙️ Operational Workflow

1. **Execute Diagnostic**:
   * **Via MCP Tool**:
     ```json
     evaluate_ai_risk({
       "text": "<full_text>",
       "domain": "<detected_domain>",
       "domain_terms": ["<term1>", "<term2>", ...],
       "target_style": "academic_thesis"
     })
     ```
   * **Via CLI**:
     ```bash
     python3 /Users/tella/Workspace/writing-suite/mcp/server.py --evaluate "<file_path>" \
       --domain "<domain>" --terms "term1,term2,term3" --style "<target_style>"
     ```

2. **Generate Visual Diagnostic Report**:
   Present the diagnostic findings clearly and rigorously (replying in the language of the user's prompt):
   * **Context Calibration Badge**:
     * `Domain`: e.g. `Blockchain & Distributed Systems`
     * `Target Style`: e.g. `Academic Thesis / Scientific Paper`
     * `Domain Terms Whitelisted`: e.g. `zkTLS, Sepolia, Merkle DAG, ERC-4337 (4 terms)`
   * **Overall Weighted AI Score** (0–100%) with status badge:
     * `🟢` **Authentic Human Text** (< 20%)
     * `🟡` **Mixed / Heavily AI-Edited** (20–65%)
     * `🔴` **High Probability Synthetic / AI** (> 65%)
   * **6-Lens Forensic Breakdown**:
     1. *Cadence Burstiness*: Sentence word length standard deviation ($\sigma_{\text{len}}$) and rhythmic variance (human $> 13$w vs robot $< 8$w).
     2. *GLTR Forensics (MIT/Harvard)*: Token probability distribution across Top 10 (Green), Top 100 (Yellow), Top 1000 (Red), Orange (Top 3000), Domain Terms %, and Tail (Purple).
     3. *GPTZero Emulator*: Mean Perplexity (PPL) and Surprise Burstiness ($\sigma_{\text{PPL}}$).
     4. *Heuristic Linter*: Density and severity of 50+ weighted structural, syntactic, and markdown tells.
     5. *Academic Stylometrics & MTLD*: Measure of Textual Lexical Diversity (length-invariant), Hapax Legomena ratio, and Yule's Characteristic K.
     6. *Anti-Bypass Filter*: Anomaly check for artificial micro-sentence fragmentation or forced conversational openers.
   * **Sentence-by-Sentence Heatmap**:
     * 🟢 High surprise / natural human variation (PPL >= 55)
     * 🟡 Moderate surprise / mixed phrasing (40 <= PPL < 55)
     * 🔴 Low surprise / predictable linear LLM completion (PPL < 40)
   * **Key Outliers**:
     * Most predictable / robotic sentence
     * Most human / high-surprise sentence
   * **Detailed Findings Table**: Line/sentence number, rule ID, category, detected snippet, and rationale.
