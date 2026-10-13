# 🖋️ Writing Suite

> **Unified, offline, zero-dependency toolkit for AI text diagnosis, academic review, and authentic human writing.**  
> Compatible with **macOS, Linux, and Windows**, supporting **Google Antigravity**, **Claude Desktop**, **Cursor**, **VS Code**, and the open **Agent Skills** standard (`npx skills`).

---

## 🏛️ Architecture: MCP Server (Deterministic Engine) + Agent Skills (Cognitive Interface)

`Writing Suite` decouples mathematical determinism from high-level LLM guidance:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AGENT SKILLS (Cognitive Frontend)               │
│                                                                        │
│   • /ai-evaluator     • /academic-editor        • /prose-humanizer     │
│    (The Diagnostic)     (The Thesis Advisor)     (The Stylistic Human) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Fast JSON-RPC calls
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      MCP SERVER (Deterministic Engine)                 │
│                                                                        │
│  1. evaluate_ai_risk       -> PPL, Burstiness, Yule's K, 50+ AI Tells  │
│  2. calculate_readability  -> Gulpease (IT), Flesch (EN), Cadence      │
│  3. lint_writing           -> 50+ weighted lexical and syntactic rules │
│  4. audit_citations        -> Unsupported claims & BibTeX / Typst check│
└────────────────────────────────────────────────────────────────────────┘
```

1. **MCP Server (`mcp/server.py`)**:
   * Runs reproducible mathematical calculations (continuous PPL proxy, burstiness standard deviation, Gulpease/Flesch indices, Yule's K, and 50+ syntactic regex rules).
   * **Zero external dependencies**: Built purely on Python 3.9+ standard library. Works on any computer out of the box without `pip install` or virtual environments.
2. **Agent Skills (`skills/`)**:
   * Instructs any AI model (Gemini, Claude 3.5, GPT-4, local Llama) with standardized behavioral rules, guaranteeing consistent review criteria across models and machines.

---

## 🔬 Scientific Foundations & Empirical Research

The suite integrates insights from leading NLP research and commercial detection engines:

* **Excess Vocabulary Studies (Liang et al., Stanford/PNAS 2024 - arXiv:2403.07183)**:
  * Over 14 million PubMed and arXiv abstracts analyzed, proving statistically massive surges in LLM marker vocabulary (*delve*, *testament*, *pivotal*, *intricate*, *beacon*).
* **Copyleaks & Turnitin Reverse-Engineering**:
  * Token probability density mapping and flat perplexity penalty.
  * **Burstiness**: Human writing exhibits high sentence length variance (4 to 35 words); LLMs cluster monotonously around 18–22 words.
  * **Syllable Dispersion & Trailing Participial Riders** (`", highlighting the importance of"`).
* **CleverHumanizer.ai Signal Catalog**:
  * 50+ diagnostic signals across staging, artificial symmetry, theatrical closers, and boilerplate openings.
  * **Dual-Style Architecture**: *Normal* (fluid conversational) vs. *Clear & Structured* (scholarly, zero slang).
* **DIPPER Paraphrase Framework (Krishna et al., ACL 2023 - arXiv:2303.13408)**:
  * **Order Diversity ($O$)**: Clause hierarchy restructuring and active-voice inversion.
  * **Lexical Diversity ($L$)**: High-probability beam-search avoidance.
  * **Meaning Lock Protocol**: Absolute invariance of empirical facts, numbers, dates, equations (`$ ... $`), and citations.

---

## 🛠️ The 3 Skills

### 1. `/ai-evaluator` (Diagnostic Termometer)
* **Role**: Evaluates synthetic text probability without modifying a single word.
* **Output**:
  * Weighted AI Risk Score (0–100%) with status badge (`🟢` Human, `🟡` Mixed, `🔴` AI).
  * 4-Lens Breakdown: GPTZero emulator, 50+ rule linter, stylometrics (Yule/Hapax), anti-bypass.
  * Sentence-by-sentence heatmap (`🟢🟡🔴`) and key outlier sentences.

### 2. `/academic-editor` (Thesis Advisor & Peer Reviewer)
* **Role**: Reviews academic theses (Typst/LaTeX), journal papers, and technical reports.
* **Output**:
  * Readability metric (Gulpease for Italian, Flesch for English).
  * Automatic flagging of ungrounded assertions with `[citation needed]`.
  * Cross-reference validation against `.bib` reference files.
  * 100% preservation of math syntax (`$ ... $`), Typst functions, and technical terminology.

### 3. `/prose-humanizer` (Stylistic Humanizer)
* **Role**: De-robotizes artificial prose into authentic, natural writing.
* **Features**:
  * Mode selection: **Normal** (blogs, essays, emails) vs. **Clear & Structured** (academic, technical).
  * DIPPER syntactic variance injection.
  * Closed-loop verification with `ai-evaluator` ensuring the final score drops below 20%.

---

## 📦 Quick Installation

### Method 1: Automated Script (Recommended)
```bash
git clone https://github.com/PtrTella/writing-suite.git ~/writing-suite
cd ~/writing-suite
chmod +x install.sh
./install.sh
```
The script runs the test suite and links the skills into Google Antigravity (`~/.gemini/config/skills/`) and the global Agent Skills directory (`~/.agents/skills/`).

### Method 2: Via Agent Skills CLI (`npx skills`)
```bash
npx skills add PtrTella/writing-suite
```

---

## 🔌 MCP Server Configuration

To use the deterministic tools in your favorite editors:

### Google Antigravity (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "writing-suite": {
      "command": "python3",
      "args": ["/Users/tella/Workspace/writing-suite/mcp/server.py", "--mcp"]
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "writing-suite": {
      "command": "python3",
      "args": ["/Users/tella/Workspace/writing-suite/mcp/server.py", "--mcp"]
    }
  }
}
```

### Cursor (`.cursor/mcp.json`) / VS Code
```json
{
  "mcpServers": {
    "writing-suite": {
      "command": "python3",
      "args": ["/Users/tella/Workspace/writing-suite/mcp/server.py", "--mcp"]
    }
  }
}
```

---

## 💻 Direct CLI Usage

The engine can also be used directly from the command line:

```bash
# Evaluate a Typst or Markdown chapter:
python3 mcp/server.py --evaluate path/to/chapter1.typ

# Calculate readability and cadence:
python3 mcp/server.py --readability path/to/text.txt --lang en

# Scan for AI cliches and syntactic tells:
python3 mcp/server.py --lint path/to/draft.md

# Verify citations and check against BibTeX:
python3 mcp/server.py --citations path/to/paper.tex --bib path/to/refs.bib
```

---

## 🧪 Automated Test Suite

All core components are covered by regression tests:
```bash
python3 tests/test_suite.py
```
Expected output:
```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.005s

OK
```

---

## 📄 License
MIT License. Free for academic, personal, and professional use.
