---
name: writing-suite
description: |
  Official operational and forensic evaluation CLI for academic theses and technical documents.
  Executes the disaggregated multi-engine diagnostic suite (Cadence, MPS Causal Surprisal, Syntax Patterns,
  Lexical Diversity, DeBERTa-v3, and Live External Tri-Consensus: Sapling + CleverHumanizer + ZeroGPT).
  Generates paragraph-by-paragraph Visual Heatmaps with actionable text surgery prescriptions,
  runs BibTeX citation audits, and compiles Typst documents into PDF with 0 errors.
license: MIT
metadata:
  version: "3.0.0"
---

# Writing Suite 3.0: Disaggregated Multi-Engine Diagnostic Architecture

Located in `/Users/tella/Workspace/writing-suite`. This suite abandons simplistic, single-scalar abstractions in favor of an **objective, disaggregated Multi-Engine Diagnostic Matrix** with **Chirurgia del Testo (Actionable Prescriptions)** and integrated **External Live Cross-Validation** (Sapling.ai, CleverHumanizer.ai, ZeroGPT.com).

---

## 1. The Disaggregated Diagnostic Engines

Writing Suite evaluates every paragraph through independent, specialized diagnostic engines:

1. **Cadence & Rhythm Engine (`mcp/core/engines/cadence.py`)**:
   * Measures sentence length standard deviation ($\sigma_{\text{len}}$) and min/max length span.
   * Flags metronomic AI rhythm ($\sigma < 6.5$) and lack of staccato clauses ($< 8$ words).
   * **Target**: $\sigma_{\text{len}} \ge 10.0$ words with at least one punchy staccato sentence.

2. **Causal Surprisal Engine (`mcp/core/engines/surprisal.py`)**:
   * Computes token-level causal perplexity (PPL) and burstiness on Apple Silicon Metal GPU (SmolLM2 MPS).
   * Pinpoints the exact lowest-surprisal sentence in the paragraph (the statistical AI cliché).
   * **Target**: $\text{PPL} \ge 75.0$.

3. **Syntax & AI Patterns Engine (`mcp/core/engines/syntax_patterns.py`)**:
   * Scans for the structural hallmarks that trigger commercial detectors:
     - **Triadic Parallelism**: elenchi a 3 bilanciati (*"A, B, and C"*).
     - **Symmetrical Antithesis**: contrapposizioni binarie (*"cannot X; rather Y"*).
     - **Explanatory Em-dashes**: incisi appositivi (*"--- as demonstrated by"*).
     - **Passive Hedges & Clichés**: *"plays a crucial role"*, *"serves as a testament"*.
     - **Single-Sentence Blocks**: paragrafi monoriga a varianza ritmica zero.

4. **Lexical Diversity Engine (`mcp/core/engines/lexical.py`)**:
   * Calculates length-invariant MTLD (Measure of Textual Lexical Diversity).
   * Flags over-repeated abstract verbs (*"ensure"*, *"guarantee"*, *"facilitate"*, *"leverage"*, *"mitigate"*).
   * **Target**: $\text{MTLD} \ge 80.0$.

5. **Neural Transformer Engine (`mcp/core/engines/neural.py`)**:
   * DeBERTa-v3 fine-tuned classifier on dense latent space.
   * Detects macro-scale semantic smoothness.

6. **External Multi-Detector Consensus Engine (`mcp/core/engines/external.py`)**:
   * Asynchronous parallel query to **Sapling.ai + CleverHumanizer.ai + ZeroGPT.com** via headless Chromium.
   * Reports live consensus alongside internal metrics to guarantee complete transparency.

---

## 2. Command Reference (`uv run`)

Always execute commands using `uv run` in `/Users/tella/Workspace/writing-suite`:

### A. Document Evaluation & Disaggregated Heatmap
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
