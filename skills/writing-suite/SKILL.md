---
name: writing-suite
description: |
  Official operational and forensic evaluation CLI for academic theses and technical documents.
  Executes the disaggregated multi-engine diagnostic suite (Cadence, MPS Causal Surprisal, Binoculars Ratio,
  Fast-DetectGPT Top-1 Gap, NLTK POS Transitions, Lexical Diversity, Hapax Legomena, DeBERTa-v3, and Live Tri-Consensus).
  Generates paragraph-by-paragraph Visual Heatmaps with actionable text surgery prescriptions,
  runs BibTeX citation audits, and compiles Typst documents into PDF with 0 errors.
license: MIT
metadata:
  version: "3.1.0"
---

# Writing Suite 3.1: SOTA Disaggregated Multi-Engine Forensic Architecture

Located in `/Users/tella/Workspace/writing-suite`. This suite abandons simplistic, single-scalar abstractions in favor of an **objective, disaggregated Multi-Engine Diagnostic Matrix** with **Chirurgia del Testo (Actionable Prescriptions)** and integrated **External Live Cross-Validation** (Sapling.ai, CleverHumanizer.ai, ZeroGPT.com).

---

## 1. The Disaggregated Diagnostic Engines

Writing Suite evaluates every paragraph through independent, specialized diagnostic engines:

1. **Cadence & Rhythm Engine (`mcp/core/engines/cadence.py`)**:
   * Measures sentence length standard deviation ($\sigma_{\text{len}}$) and min/max length span.
   * **Punctuation Shannon Entropy ($H_{\text{punct}}$)**: Flags flat, monotonous comma-period pacing ($H < 1.30$); targets rich asymmetric pacing ($H \ge 1.6 - 2.2$ bits) with semicolons, em-dashes, and parentheticals.
   * Flags metronomic AI rhythm ($\sigma < 6.5$) and lack of staccato clauses ($< 8$ words).
   * **Target**: $\sigma_{\text{len}} \ge 10.0$ words, $H_{\text{punct}} \ge 1.60$ with at least one punchy staccato sentence.

2. **Causal Surprisal & Binoculars Engine (`mcp/core/engines/surprisal.py`)**:
   * Runs local SmolLM2-135M on Apple Silicon Metal GPU (MPS).
   * **Binoculars Perplexity-to-Entropy Ratio** (Hans et al., ICML 2024): $B = \frac{\log \text{PPL}}{H_M}$. In AI text, tokens closely follow model entropy ($B \le 0.95$); in authentic human text, tokens diverge asymmetrically ($B > 1.05 - 1.25$).
   * **Fast-DetectGPT Top-1 Curvature Gap** (Bao et al., ICLR 2024): $\Delta = \log P(\text{top1}) - \log P(w_t)$. Flags greedy/argmax lockstep when $\Delta < 2.1$.
   * Computes token-level causal perplexity (PPL) and burstiness.
   * **Target**: $\text{PPL} \ge 75.0$, $B \ge 1.05$, $\text{Top-1 Gap} \ge 2.5$.

3. **Syntax & Grammatical Architecture Engine (`mcp/core/engines/syntax_patterns.py`)**:
   * Utilizes **NLTK Averaged Perceptron POS Tagger** and structural syntax analysis:
     - **POS Transition Entropy ($H_{\text{POS}}$)**: Bigram POS transition diversity; flags rigid, canonical SVO pipelines ($H_{\text{POS}} < 4.2$).
     - **POS-level Triadic Parallelism**: Coordinate noun/verb/adjective chains.
     - **Passive Voice Chains**: Sequence of auxiliary + past participle (`aux + VBN`).
     - **Symmetrical Punctuation**: Semicolon balance, explanatory em-dashes, and leading adverbials (*"Furthermore,"*, *"Crucially,"*).
     - **Single-Sentence Blocks**: Isolated single-sentence paragraphs.

4. **Lexical Diversity & Zipf Long-Tail Engine (`mcp/core/engines/lexical.py`)**:
   * **WordNet Lemmatization**: Grouping words to root lemmas to eliminate morphological repetition.
   * **Hapax Legomena Ratio ($V_1 / N$)**: Words occurring once relative to token count. LLMs using nucleus sampling truncate the Zipf tail ($V_1/N < 85\%$); human text maintains $V_1/N > 90\%$.
   * **Yule's Characteristic $K$**: Length-invariant measure of vocabulary concentration.
   * **Length-invariant MTLD**: Measure of Textual Lexical Diversity (Target $\ge 80.0$).

5. **Neural Transformer Engine (`mcp/core/engines/neural.py`)**:
   * DeBERTa-v3 fine-tuned classifier on dense latent space.
   * Calibrated with RAID benchmark insights to prevent false positives on rigorous academic Computer Science terminology.

6. **External Multi-Detector Consensus Engine (`mcp/core/engines/external.py`)**:
   * Asynchronous parallel query to **Sapling.ai + CleverHumanizer.ai + ZeroGPT.com** via headless Chromium.
   * Reports live consensus alongside internal metrics to guarantee complete transparency.


---

## 2. Command Reference (`uv run`)

Always execute commands using `uv run` in `/Users/tella/Workspace/writing-suite`:

### A. Writing Assistant, Fact-Checker & Multi-LLM Prompt Maker
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite assist "<path/to/file.typ>" [paragrafo_idx] [--copy] [--all]
```
* **Cos'è**: Il ponte diretto tra la writing-suite e i tuoi modelli di scrittura (Claude, ChatGPT, Gemini).
* **Cosa fa**:
  1. Esegue il **fact-checking** completo delle citazioni incrociando il testo con `references.bib` (scova broken references e claim non supportati).
  2. Isola i paragrafi sintetici/robotici (con cadenza metronomica $\sigma_{\text{len}} < 6.0$ o pattern AI).
  3. Suggerisce fonti pertinenti dal file `.bib` per la tematica trattata.
  4. Genera un **Prompt Chirurgico pronto all'uso** contenente il testo, i vincoli IEEE S&P e il Meaning Lock.
  5. Se usi `--copy`, copia istantaneamente il prompt negli appunti di macOS (`pbcopy`) per incollarlo con `Cmd+V` in Claude, ChatGPT o Gemini!

### B. Document Evaluation & Disaggregated Heatmap
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite evaluate "<path/to/file.typ>"
```
* **Output**: Complete corpus metrics followed by the paragraph-by-paragraph matrix:
  ```text
  §    | Parole | Cadenza | Surprisal | Sintassi | DeBERTa | Status     | Snippet
  --------------------------------------------------------------------------------------
  §01  | 84     | 🔴  4.6 | 🟢 159.2  | 🔴 2     | 🟢 5.4% | 🟡 45.0%   | Modern software engineering...
       └─> CHIRURGIA DEL TESTO (Prescrizioni Operative):
           • Trovati 2 elenchi ternari: rompi la simmetria a tre (trasforma il 3° elemento in frase causale).
           • Ritmo metronomico: spezza una frase lunga e inserisci una proposizione staccata di 4-6 parole.
  ```

### B. Live External Cross-Validation
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite evaluate "<path/to/file.typ>" --cross-validate
```
* Runs the internal diagnostic engines and automatically samples the most critical paragraphs against the live network consensus:
  ```text
  CROSS-VALIDAZIONE ESTERNA LIVE (Campioni Critici su Rete)
  Paragrafo §01: "Modern software engineering..."
    • Rischio Interno Combinato : 45.0%
    • Consenso Esterno Live     : 82.0% [Sapling: 98.6% | Clever: 99.0% | ZeroGPT: 48.3%]
  ```

### C. Direct Multi-Detector Check
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite check-live "<path/to/file.typ>"
```
* Directly queries CleverHumanizer, ZeroGPT, and Sapling concurrently on any text or file.

### D. Bibliographic Integrity & Citations Audit
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite citations "<file.typ>" [references.bib]
```
* Validates that all in-text `@key` citations exist in `.bib` (zero orphan citations).
* Detects ungrounded apodictic statements (*"studies have shown"*, *"it is widely acknowledged"*).

### E. Typst PDF Compilation
```bash
uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite compile [path/to/main.typ]
```
* Compiles master document with Typst certifying 0 errors.

---

## 3. The Closed-Loop Prescriptive Writing Runbook

Whenever reviewing or writing text:

1. **Run Diagnostics**:
   `uv run --directory /Users/tella/Workspace/writing-suite bin/writing-suite evaluate <file.typ>`.
2. **Follow Actionable Prescriptions**:
   Do not guess. Read the `CHIRURGIA DEL TESTO` output for each paragraph:
   - If **Syntax** flags an elenco ternario: break the 3-item list.
   - If **Cadence** flags metronomic pacing: insert a 4-7 word punchy sentence.
   - If **Surprisal** flags low PPL: rewrite the critical sentence with concrete systems friction.
3. **Cross-Validate**:
   Run with `--cross-validate` to confirm external detector agreement.
4. **Compile**:
   Run `compile` to guarantee 0 Typst errors.
