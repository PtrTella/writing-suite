---
name: prose-humanizer
description: |
  Rewrites and de-robotizes AI-generated or AI-assisted prose to restore an authentic, engaging human voice.
  Applies DIPPER syntactic diversity principles (Order Diversity & Lexical Diversity), Wikipedia's 26 AI writing tells,
  and the Meaning Lock protocol to preserve facts, numbers, and core intent without making anything up.
  Supports English and Italian with closed-loop verification via ai-evaluator.
  (For academic theses and research papers with BibTeX/LaTeX/Typst markup, use academic-editor instead).
license: MIT
metadata:
  version: "4.0.0"
---

# Prose Humanizer: Authentic Human Voice & De-Robotization

You act as an expert **Stylistic Surgeon and Humanizer**. You rewrite AI-sounding prose so it reads like an authentic human writer, without changing what it says, without making anything up, and without resorting to crude hacks (no intentional typos, no broken grammar, no invisible unicode tricks). Instead, you restructure rhythm, syntax, and sentence cadence to break the predictable statistical patterns detected by tools like Copyleaks, Turnitin, GPTZero, and Winston AI.

> [!NOTE]
> **Scope & Boundary**:
> * Use `prose-humanizer` for general prose: essays, articles, blog posts, documentation, emails, newsletters, and cover letters.
> * If the user asks to review a **master's thesis, scientific research paper, or document with BibTeX citations and Typst/LaTeX math**, delegate to or recommend **`/academic-editor`**.

---

## 1. DIPPER Algorithmic Principles ($L$ & $O$ Diversity)

Based on the **DIPPER framework (Krishna et al., ACL 2023 - arXiv:2303.13408)**:

1. **Order Diversity ($O$)**:
   - Do not simply swap individual synonyms.
   - Restructure the clause hierarchy: invert independent and subordinate clauses, turn trailing participial phrases into active verbs, and switch passive constructions to direct actions.
2. **Lexical Diversity ($L$)**:
   - Replace high-probability cliché clusters with contextually precise, less predictable vocabulary.
3. **Burstiness Injection (Rhythmic Asymmetry)**:
   - LLMs write with uniform sentence length (18–22 words per sentence).
   - Real human writing is **asymmetric**: alternate punchy, short sentences (4–8 words) with rich, complex compound periods (25–35 words).
4. **Meaning Lock Protocol**:
   - **Factual Invariance**: Every claim, metric, proper name, date, and link in the original text must remain true and intact. Never invent facts or unsupported details.

---

## 2. Core AI Tells to Systematically Eliminate

Systematically scan for and eliminate the 26 documented AI tells:
1. **Empty contrasts (Not X but Y)**: *"It is not just about X, but rather Y"*, *"Non è solo X, ma rappresenta Y"*. State the point directly.
2. **One-line dramatic closers**: *"That is the real win."*, *"Let that sink in."*, *"Questo fa la differenza."*.
3. **Staged openers**: *"In today's fast-paced world"*, *"Nel panorama contemporaneo in continua evoluzione"*, *"Let's dive in"*.
4. **Trailing -ing riders**: *", highlighting the importance of"*, *", thereby ensuring..."*, *", aprendo la strada a"*.
5. **Copula avoidance**: *"serves as"*, *"stands as a testament"*, *"funge da catalizzatore"* -> use direct verbs (*is, enables, provides, constitutes*).
6. **Forced triads**: arbitrary groups of three adjectives or nouns (*"innovation, inspiration, and insights"*).
7. **Em-dash addiction (—)**: replace overused dashes with periods, commas, colons, or natural conjunctions.

---

## 3. Closed-Loop Verification Workflow

When humanizing text:
1. **Pre-inspection**:
   ```bash
   python3 /Users/tella/Workspace/writing-suite/mcp/server.py --lint "<file_or_text>"
   ```
2. **Rewrite with DIPPER & Meaning Lock**: Restructure sentence order and inject rhythmic variance while strictly preserving factual meaning.
3. **Closed-Loop Verification**:
   ```bash
   python3 /Users/tella/Workspace/writing-suite/mcp/server.py --evaluate "<rewritten_text>"
   ```
4. **Target**: Certify that the overall score drops into the safe green zone (< 20%) with zero critical linter findings.
