# 🖋️ Writing Suite

> **Unified, offline, zero-dependency engine for continuous AI text forensics, academic peer-review, and authentic human writing.**  
> Built purely on the **Python 3.9+ Standard Library** ($O(1)$ lexical lookups, zero pip dependencies). Compatible with **macOS, Linux, and Windows**, supporting **Google Antigravity**, **Claude Desktop**, **Cursor**, **VS Code**, and the open **Agent Skills** standard (`npx skills`).

---

## 🏛️ Architecture: Deterministic Forensic Engine + Cognitive Agent Skills

Writing Suite solves a fundamental flaw in modern LLM evaluations: **stochastic LLM-as-a-judge approaches fail at scale**. Relying on large models to evaluate writing across multi-chapter theses or software repositories introduces hallucinations, non-deterministic scoring, high token costs, and context exhaustion.

Writing Suite strictly decouples **deterministic mathematical forensics** from **high-level cognitive reasoning**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AGENT SKILLS (Cognitive Frontend)               │
│                                                                        │
│   • /ai-evaluator     • /academic-editor        • /prose-humanizer     │
│    (The Diagnostic)     (The Thesis Advisor)     (The Stylistic Human) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Fast JSON-RPC calls (stdio / CLI)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      MCP SERVER (Deterministic Engine)                 │
│                                                                        │
│  1. evaluate_ai_risk       -> Continuous multi-lens forensic diagnosis │
│  2. audit_project          -> Recursive multi-file project & BibTeX    │
│  3. calculate_readability  -> Gulpease (IT), Flesch (EN), Cadence      │
│  4. lint_writing           -> 50+ weighted lexical/syntactic AI tells  │
│  5. audit_citations        -> Unsupported claims & BibTeX verification │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Pure Python 3.9+ Standard Library
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      MULTI-LANGUAGE CORE ARCHITECTURE                  │
│                                                                        │
│  • BaseLanguagePack (Abstract)  • ItalianLanguagePack  • EnglishPack   │
│  • 5-Tier Zipf Frequency Tiers  • Clitic Normalization • Syllabifiers  │
└────────────────────────────────────────────────────────────────────────┘
```

1. **MCP Server (`mcp/server.py`)**:
   * Evaluates text through continuous mathematical equations (GLTR token probability buckets, sentence length cadence variance, Zipf Shannon surprisal, continuous logistic sigmoids, MTLD, and Yule's $K$).
   * **Zero external dependencies**: Requires no PyTorch, no HuggingFace, no `pip install`. Pure standard library (`math`, `re`, `pathlib`, `json`, `collections`).
   * **Instant throughput**: Audits entire books, master's theses, and doc repositories in milliseconds ($>100{,}000$ words per second).
2. **Cognitive Agent Skills (`skills/`)**:
   * Implements formal editorial protocols (DIPPER syntactic transformation, Meaning Lock protocol, epistemic citation verification) across any frontier model (Gemini, Claude 3.5, GPT-4, Llama).

---

## 🔬 Theoretical Foundations & Academic References

Writing Suite integrates empirical research from top natural language processing (NLP) literature, forensic stylometry, and information theory:

### 1. GLTR: Giant Language Model Test Room
* **Citation**: Gehrmann, S., Strobelt, H., & Rush, A. M. (Harvard NLP / IBM Research). *"GLTR: Statistical Detection and Visualization of Generated Text."* **ACL 2019 (System Demonstrations)**, pp. 111–116. [arXiv:1906.04043](https://arxiv.org/abs/1906.04043).
* **Forensic Principle**: Autoregressive language models decode by sampling from the head of the conditional probability distribution:
  $$P(w_t \mid w_{<t})$$
  Under decoding strategies like top-$k$ or nucleus ($p$) sampling, LLMs almost never sample tokens from the distribution's tail. Writing Suite projects words onto a 5-tier Zipf frequency space:
  $$\text{Top 10 (Green)} \quad \text{Top 100 (Yellow)} \quad \text{Top 1000 (Red)} \quad \text{Top 3000 (Orange)} \quad \text{Tail (Purple)}$$
  Synthetic prose exhibits **extreme head saturation** ($\text{Top 10} + \text{Top 100} > 65\%$) and **tail starvation** ($\text{Tail} < 10\%$). Genuine human writing consistently samples uncommon, idiosyncratic, and domain-specific words ($\text{Tail} > 20\%$).

### 2. Zipf's Law & Information-Theoretic Surprisal
* **Citations**: 
  * Zipf, G. K. (1949). *Human Behavior and the Principle of Least Effort.* Addison-Wesley.
  * Shannon, C. E. (1948). *"A Mathematical Theory of Communication."* **Bell System Technical Journal**, 27(3), pp. 379–423.
* **Forensic Principle**: Word rank-frequency follows a power-law distribution $P(r) \propto r^{-s}$. Writing Suite computes the token surprisal:
  $$I(w) = -\log_2 P(w)$$
  The sentence perplexity proxy is defined continuously as the geometric mean of token surprisal:
  $$\text{PPL}(S) = 2^{\frac{1}{|S|}\sum_{w \in S} I(w)}$$
  While raw LLMs produce flat, uniform token probabilities across entire paragraphs, human authors introduce high local surprisal spikes.

### 3. Sentence Cadence Variance & Burstiness
* **Citation**: Copyleaks & Turnitin Reverse-Engineering Studies; Liang et al. (Stanford, 2024). *"Monitoring AI-Modified Text at Scale."* **PNAS / arXiv:2403.07183**.
* **Forensic Principle**: Autoregressive decoders suffer from **cadence monotony**. Due to length-penalty normalization and beam search equilibrium, AI sentence lengths tightly cluster around $\mu \approx 16 - 22$ words with minimal standard deviation ($\sigma_{\text{len}} \approx 7 - 9$ words). Authentic human writing alternates between rapid punchy clauses (3–7 words) and elaborate subordinate structures (30–60 words), yielding $\sigma_{\text{len}} \ge 11.5$ words.

### 4. Curvature & Density Discrepancy
* **Citations**:
  * Hans, A., et al. (2024). *"Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text."* **ICML 2024**, [arXiv:2401.12070](https://arxiv.org/abs/2401.12070).
  * Bao, G., et al. (2024). *"Fast-DetectGPT: Efficient Zero-Shot Detection of Machine-Generated Text via Conditional Probability Curvature."* **ICLR 2024**, [arXiv:2310.05130](https://arxiv.org/abs/2310.05130).
  * Mitchell, E., et al. (2023). *"DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature."* **ICML 2023**, [arXiv:2301.07597](https://arxiv.org/abs/2301.07597).
* **Forensic Principle**: Generated texts occupy local positive-curvature maxima in probability space, making them susceptible to perturbations, whereas human text lies on flatter, erratic probability manifolds.

### 5. DIPPER Paraphrase Framework & Meaning Lock
* **Citation**: Krishna, K., et al. (2023). *"Paraphrasing evades detectors: Improving both lexical and syntactic paraphrasing with DIPPER."* **ACL 2023**, pp. 11520–11539. [arXiv:2303.13408](https://arxiv.org/abs/2303.13408).
* **Forensic Principle**: De-robotizing text requires formal manipulation of:
  * **Order Diversity ($O$)**: Reordering subordinate clauses, preposing prepositional phrases, and converting passive voice constructions.
  * **Lexical Diversity ($L$)**: Injecting low-frequency synonyms to disrupt n-gram predictability.
  * **Meaning Lock Protocol ($M_{\text{lock}}$)**: Strict mathematical invariance. Scientific figures, numbers, dates, formulas (`$ ... $`), Typst functions, and bibliographic keys are frozen and cannot be mutated during humanization.

### 6. Lexical Diversity & Stylometrics
* **Citations**:
  * McCarthy, P. M., & Jarvis, S. (2010). *"MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment."* **Behavior Research Methods**, 42(2), pp. 381–392.
  * Yule, G. U. (1944). *The Statistical Study of Literary Vocabulary.* Cambridge University Press.
* **Forensic Principle**:
  * **MTLD (Measure of Textual Lexical Diversity)**: Calculates the mean length of word strings maintaining a Type-Token Ratio (TTR) above 0.72. Unlike crude TTR, MTLD is mathematically length-invariant.
  * **Yule's Characteristic $K$**:
    $$K = 10^4 \cdot \frac{\sum_{m} m^2 V_m - N}{N^2}$$
    Measures vocabulary concentration independently of document size.
  * **Hapax Legomena Ratio**: Percentage of words occurring exactly once:
    $$\text{Hapax} = \frac{V_1}{|V|}$$

### 7. Readability & Epistemic Calibration
* **Citations**:
  * Lucisano, P., & Piemontese, M. E. (1988). *"GULPEASE. Una formula per la predizione della facilità di lettura dei testi in lingua italiana."* **Scuola e Città**, 31(3), pp. 110–124.
  * Kincaid, J. P., et al. (1975). *"Derivation of new readability formulas for Navy enlisted personnel."* Research Branch Report 8-75.
* **Forensic Principle**:
  * **Indice Gulpease (Italian)**:
    $$G = 89 + \frac{300 \cdot L_p - 10 \cdot L_f}{L_p}$$
    Where $L_p$ is word count and $L_f$ is letter count. Calibrated for Italian morphology.
  * **Flesch Reading Ease (English)**:
    $$\text{FRE} = 206.835 - 1.015 \left(\frac{\text{words}}{\text{sentences}}\right) - 84.6 \left(\frac{\text{syllables}}{\text{words}}\right)$$

---

## 📐 Continuous Mathematical Scoring Engine

Legacy detection tools rely on step-wise thresholds (e.g. `if PPL < 40: score += 30`), producing sudden cliffs and erratic score jumps. Writing Suite replaces all discrete thresholds with **continuous, differentiable sigmoid functions**:

### 1. Cadence Burstiness Risk
$$R_{\text{Cadence}}(\sigma_{\text{len}}) = \frac{100}{1 + \exp\left(0.35 \cdot (\sigma_{\text{len}} - 10.5)\right)}$$
* When sentence length standard deviation is uniform ($\sigma_{\text{len}} \approx 7.0$), $R_{\text{Cadence}} \approx 77\%$.
* When sentence length variance is dynamic ($\sigma_{\text{len}} \ge 16.0$), $R_{\text{Cadence}} \le 12\%$.

### 2. GLTR Tail Scarcity Risk
$$R_{\text{GLTR}}(\tau) = \frac{100}{1 + \exp\left(0.25 \cdot (\tau - 14.0)\right)}$$
Where $\tau$ is the percentage of tail words ($r > 3000$). Pure AI prose with $\tau \approx 6\%$ yields $R_{\text{GLTR}} \approx 88\%$, while human prose with $\tau \ge 25\%$ yields $R_{\text{GLTR}} \le 6\%$.

### 3. Heuristic Linter Penalty Density
$$R_{\text{Linter}}(W_{\text{tot}}, D) = 100 \cdot \left(1 - \exp\left(-0.10 \cdot W_{\text{tot}} - 0.15 \cdot D\right)\right)$$
Where $W_{\text{tot}}$ is the cumulative weight of detected AI tells and $D$ is the finding density per 1,000 words.

### 4. Lexical Diversity Risk (MTLD)
$$R_{\text{MTLD}}(M) = \frac{100}{1 + \exp\left(0.04 \cdot (M - 65.0)\right)}$$

### 5. Composite Continuous Score
The overall synthetic probability score combines the continuous lenses:
$$\text{Score}_{\text{AI}} = 0.35 \cdot R_{\text{Linter}} + 0.25 \cdot R_{\text{Cadence}} + 0.25 \cdot \left(\frac{R_{\text{GLTR}} + R_{\text{PPL}}}{2}\right) + 0.15 \cdot \left(\frac{R_{\text{Yule}} + R_{\text{MTLD}}}{2}\right)$$

```
Score:  0% ──────────── 35% ──────────────────── 60% ──────────── 100%
Badge:         🟢 Safe Human           🟡 Mixed / Edited        🔴 Synthetic AI
```

---

## 🌍 Multi-Language Core Architecture (`mcp/core/languages.py`)

Writing Suite features a modular, pluggable natural language registry:

```python
from mcp.core.languages import LanguageRegistry

# Automatic language detection from text (O(N) closed-class stopword projection)
pack = LanguageRegistry.detect_language("In un'architettura a microservizi asincroni...")
print(pack.name) # "Italian"
```

### Supported Languages Out-of-the-Box:
1. **Italian (`ItalianLanguagePack` - `it`)**:
   * Native elision and clitic splitting: automatically separates `l'`, `d'`, `dell'`, `all'`, `un'`, `quest'`.
   * Native **Indice Gulpease** readability formula.
   * 5-tier Zipf frequency lexicons calibrated on CoLFIS and Subtlex-IT corpora.
2. **English (`EnglishLanguagePack` - `en`)**:
   * Contraction normalization (`don't`, `it's`, `they're`).
   * **Flesch Reading Ease** and **Flesch-Kincaid Grade Level**.
   * 5-tier Zipf frequency lexicons calibrated on SUBTLEX-US and Brown corpora.
3. **Spanish (`SpanishLanguagePack` - `es`)**:
   * Native **Índice Fernández-Huerta** readability formula.
   * Closed-class diagnostic vectors based on Real Academia Española (RAE) frequencies.
4. **French (`FrenchLanguagePack` - `fr`)**:
   * Native **Formule Kandel & Moles** readability formula.
   * Closed-class diagnostic vectors calibrated on Lexique 3.
5. **German (`GermanLanguagePack` - `de`)**:
   * Native **Amstad Lesbarkeitsindex** readability formula.
   * Closed-class diagnostic vectors calibrated on dlexDB and DeReWo.

### 🌐 Universal Zero-Shot Fallback (`UniversalLanguagePack`):
For any other natural language without pre-compiled dictionaries (e.g., Latin, Portuguese, Dutch, Russian, Swedish):
* **Sonority Sequencing Principle (SSP)**: Universal phonotactic syllabification across vowels, diphthongs, and consonant valleys.
* **Universal Readability**: Computes **LIX (Björnsson 1968)**, the internationally recognized language-independent readability standard.
* **Corpus-Relative Zipf Rank Profiling**: Dynamically derives the Top 10/100 function tokens from the document itself in $O(N)$ without needing external databases.

### ⚡ Dynamic Runtime Injection by Agents:
The Agent or caller can inject new languages at runtime without restarting the server:
```python
from mcp.core.languages import LanguageRegistry

LanguageRegistry.register_dynamic(
    lang_code="pt",
    name="Português",
    top_10=["o", "a", "de", "que", "e", "do", "da", "em", "um", "para"]
)
```

---

## 📊 Empirical Benchmarks & Validation

Validation across real-world corpora (tested on Apple Silicon & Linux x86_64):

| Corpus / Document | Ground Truth | AI Score | Badge | Linter Tells | Cadence $\sigma$ | MTLD | GLTR Saturation | Verdict |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **AI Technical Doc: Zero Trust & State Bloat** | 🤖 Synthetic AI | **54.8%** | 🟡 | 7 | 7.5w | 155.3 | 73.3% | Heavy AI Editing / Synthetic |
| **AI Technical Doc: Chapter 7 Evaluation** | 🤖 Synthetic AI | **49.1%** | 🟡 | 6 | 7.6w | 202.5 | 53.3% | Heavy AI Editing / Synthetic |
| **AI Technical Doc: Async Relayer Architecture** | 🤖 Synthetic AI | **44.3%** | 🟡 | 3 | 10.1w | 185.2 | 85.2% | Heavy AI Editing / Synthetic |
| **Genuine Human Thesis: Ch1 Introduction** | 👤 Authentic Human | **9.1%** | 🟢 | 0 | 16.4w | 219.3 | 40.4% | Safe Authentic Human Prose |
| **Genuine Human Thesis: Ch5 Architecture** | 👤 Authentic Human | **26.1%** | 🟢 | 1 | 11.0w | 147.0 | 43.0% | Safe Authentic Human Prose |
| **University Lecture Notes: Blockchain (UniBo)** | 👤 Authentic Human | **28.7%** | 🟢 | 7 | 62.0w | 219.6 | 29.6% | Safe Authentic Human Notes |
| **Encyclopedia: Crittografia Asimmetrica (Wiki)** | 👤 Authentic Human | **34.0%** | 🟢 | 0 | 10.0w | 32.1 | 6.9% | Safe Authentic Human Prose |

> **Performance**: The entire benchmark suite (7 multi-page documents, $>18{,}000$ words) executes in **less than 0.8 seconds** with zero external packages.

---

## 🛠️ The 3 Specialized Agent Skills

Writing Suite provides three distinct skills aligned with the open **Agent Skills** specification:

### 1. `/ai-evaluator` (Continuous Forensic Diagnostic)
* **Goal**: Objective diagnostic audit without modifying a single word.
* **Outputs**:
  * Comprehensive AI risk score (0–100%) and confidence interval.
  * 6 continuous lenses: Heuristic Linter, Cadence $\sigma$, GLTR Forensics, GPTZero proxy, Stylometrics (MTLD, Yule's $K$), and Anti-Bypass checks.
  * Sentence-by-sentence color-coded heatmap (`🟢 Safe`, `🟡 Mixed`, `🔴 Synthetic`).

### 2. `/academic-editor` (Thesis Advisor & Peer Reviewer)
* **Goal**: Document structure, epistemic rigor, and citation integrity for academic works (Typst, LaTeX, Markdown).
* **Outputs**:
  * Detection of ungrounded factual claims with automated `[citation needed]` annotations.
  * Cross-reference validation against `.bib` databases (detects phantom or unreferenced keys).
  * Readability calibration: Gulpease (Italian) or Flesch (English).
  * 100% preservation of mathematical blocks (`$ ... $`), formulas, and code blocks.

### 3. `/prose-humanizer` (Stylistic De-robotizer)
* **Goal**: Eliminates AI writing tells while preserving meaning through the DIPPER framework.
* **Dual Styles**:
  * **Normal**: Fluid, organic, conversational tone for essays, blog posts, and articles.
  * **Clear & Structured**: Scholarly, rigorous tone with zero slang, ideal for academic chapters.
* **Rules**: Eliminates staged openers, forced contrast pairs (*not only... but also*), participial trailers, and em-dash spam. Enforces the Meaning Lock protocol.

---

## 📦 Quick Installation

### Method 1: Universal Shell Script (Recommended)
```bash
git clone https://github.com/PtrTella/writing-suite.git ~/writing-suite
cd ~/writing-suite
chmod +x install.sh
./install.sh
```
The script runs the test suite and automatically links the skills into Google Antigravity (`~/.gemini/config/skills/`) and the Agent Skills directory (`~/.agents/skills/`).

### Method 2: Via Agent Skills CLI (`npx skills`)
```bash
npx skills add PtrTella/writing-suite
```

---

## 🔌 MCP Server Configuration

Writing Suite operates as a standard Model Context Protocol (MCP stdio JSON-RPC 2.0) server.

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

The deterministic engine can be invoked directly from the command line or integrated into CI/CD pipelines:

```bash
# 1. Full multi-file audit of a project or thesis directory (.typ, .tex, .md) with BibTeX validation:
python3 mcp/server.py --audit path/to/thesis_directory/ --bib path/to/references.bib

# 2. Continuous forensic AI evaluation of a document:
python3 mcp/server.py --evaluate path/to/chapter1.typ

# 3. Readability and rhythm cadence calculation (Gulpease or Flesch):
python3 mcp/server.py --readability path/to/essay.md --lang it

# 4. Scan for 50+ AI syntactic tells and clichés:
python3 mcp/server.py --lint path/to/draft.md

# 5. Citation verification and unsupported claim detection:
python3 mcp/server.py --citations path/to/paper.tex --bib path/to/refs.bib

# 6. Raw JSON output for CI/CD automation:
python3 mcp/server.py --evaluate path/to/doc.md --json
```

---

## 🧪 Regression Test Suite

All algorithms and continuous functions are tested against regression:
```bash
python3 tests/test_suite.py
```
Output:
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.014s

OK
```

---

## 📚 Formal Bibliography

1. **Gehrmann, S., Strobelt, H., & Rush, A. M.** (2019). GLTR: Statistical Detection and Visualization of Generated Text. *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics: System Demonstrations*, 111–116. [doi:10.18653/v1/P19-3019](https://doi.org/10.18653/v1/P19-3019)
2. **Krishna, K., Wieting, J., & Iyyer, M.** (2023). Paraphrasing evades detectors: Improving both lexical and syntactic paraphrasing with DIPPER. *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, 11520–11539. [doi:10.18653/v1/2023.acl-long.644](https://doi.org/10.18653/v1/2023.acl-long.644)
3. **Hans, A., Sari, Y., Gim, R., Sanyal, S., & Goldstein, T.** (2024). Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text. *International Conference on Machine Learning (ICML 2024)*. [arXiv:2401.12070](https://arxiv.org/abs/2401.12070)
4. **Bao, G., Zhao, Y., Teng, Z., Yang, L., & Zhang, Y.** (2024). Fast-DetectGPT: Efficient Zero-Shot Detection of Machine-Generated Text via Conditional Probability Curvature. *International Conference on Learning Representations (ICLR 2024)*. [arXiv:2310.05130](https://arxiv.org/abs/2310.05130)
5. **Mitchell, E., Yoon, J., Miao, N., Finn, C., & Manning, C. D.** (2023). DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature. *International Conference on Machine Learning (ICML 2023)*, 24950–24962. [arXiv:2301.07597](https://arxiv.org/abs/2301.07597)
6. **Liang, W., Yuksekgonul, M., Mao, Y., Wu, E., & Zou, J.** (2024). Monitoring AI-Modified Text at Scale: A Case Study on the Impact of ChatGPT on AI Conference Peer Reviews. *Proceedings of the National Academy of Sciences (PNAS)*. [arXiv:2403.07183](https://arxiv.org/abs/2403.07183)
7. **McCarthy, P. M., & Jarvis, S.** (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. *Behavior Research Methods*, 42(2), 381–392. [doi:10.3758/BRM.42.2.381](https://doi.org/10.3758/BRM.42.2.381)
8. **Lucisano, P., & Piemontese, M. E.** (1988). GULPEASE. Una formula per la predizione della facilità di lettura dei testi in lingua italiana. *Scuola e Città*, 31(3), 110–124.
9. **Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S.** (1975). Derivation of new readability formulas for Navy enlisted personnel. *Research Branch Report 8-75*, Naval Technical Training Command.
10. **Shannon, C. E.** (1948). A Mathematical Theory of Communication. *Bell System Technical Journal*, 27(3), 379–423.
11. **Zipf, G. K.** (1949). *Human Behavior and the Principle of Least Effort.* Addison-Wesley Press.
12. **Yule, G. U.** (1944). *The Statistical Study of Literary Vocabulary.* Cambridge University Press.

---

## 📄 License
MIT License. Free for academic, personal, open-source, and commercial use.
