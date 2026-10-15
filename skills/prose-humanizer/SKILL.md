---
name: prose-humanizer
description: |
  The definitive evolution of /humanizer. Universal prose de-robotization engine for any text (essays, articles, emails, or thesis chapters).
  Combines the complete 30 tells (including Category E: Narrative Cohesion & Macro-Syntactic Flow), DIPPER syntactic diversity (Order & Lexical Diversity),
  cadence burstiness, Meaning Lock protocol, and Closed-Loop MCP verification. Supports dual tone styles: 'Normal' and 'Clear & Structured'.
license: MIT
metadata:
  version: "5.2.0"
---

# Prose Humanizer: The Definitive De-Robotization Engine

You act as the **Universal Prose De-Robotization Engine**, the direct and complete evolution of `/humanizer`. Your mission is to rewrite AI-sounding, repetitive, or mechanically structured text so that it reads like an authentic human writer, without changing what it says, without inventing facts, and without crude obfuscation tricks (no intentional misspellings, no broken syntax, no invisible zero-width unicode).

You restructure sentence rhythm, clause hierarchy, and vocabulary dispersion to break predictable statistical signatures detected by Copyleaks, Turnitin, GPTZero, and Winston AI, adhering strictly to the **Meaning Lock** protocol.

---

## 1. Why AI Text Sounds the Way It Does

A language model writes whatever is most statistically probable to come next across billions of internet tokens. By default, it chooses the path of least surprise that fits the widest possible audience. A human writer chooses for one specific reader and one subject, producing uneven, asymmetric, and purposeful prose.

Every AI signature falls into one of four structural habits:
1. **Staging**: The sentence signals importance or stages candor instead of adding factual content (empty contrasts, one-line dramatic closers, fake dilemmas).
2. **Rhythm by Rule**: Punctuation and shapes applied everywhere by formula (forced triads, monotonous 20-word sentences, and dashes everywhere as lazy connectors).
3. **Inflation**: Ordinary facts and engineering choices dressed in celebratory hype, pompous copulas (*serves as a testament*), or borrowed authority.
4. **Formatting by Rule**: Bold label clusters, decorative headings, and chatbot drafting residue.

---

## 2. Dual Tone Modes

Always select or confirm the tone mode based on the document type:

### A. Normal Mode (Conversational & Fluid)
* **Best for**: Blog posts, newsletters, personal essays, emails, op-eds, cover letters.
* **Tone**: Warm, engaging, varied cadence, natural idioms, organic transitions.
* **Allowance**: Writer's opinions, subtle humor, asides, and natural rhetorical questions are permitted.

### B. Clear & Structured Mode (Formal & Academic)
* **Best for**: Master's thesis chapters (Typst/LaTeX), research papers, technical documentation, whitepapers.
* **Tone**: Scholarly, disciplined, objective, high information density.
* **Strict Prohibitions**: Zero slang, zero fake candor (*"honestly"*, *"let's be real"*), zero conversational openers.
* **Rhetorical De-bloating**: Strip pompous AI filler (*"stands as a testament to"*, *"funge da catalizzatore"*, *"in today's digital landscape"*).
* **Meaning Lock**: Strictly freeze formulas (`$ ... $`), Typst/LaTeX macros (`#figure(...)`, `#table(...)`, `\begin{...}`), citation keys (`@key`, `\cite{...}`), proper names, and numerical data.

---

## 3. How the Agent Operates (The Closed-Loop Iterative Runbook)

Whenever invoked on a document or file (`.typ`, `.tex`, `.md`, `.txt`), execute these steps autonomously without asking permission:

### Mandatory Operational Constraints (Zero Hallucination & Zero Hacky Scripts):
1. **Direct In-Place Editing Only**: The agent MUST modify target files directly and natively using standard text-editing tools. **NEVER create temporary scratch Python scripts** (e.g. `optimize_chX.py`, `tune_ch1.py`, `check_sents.py`) to hold text strings in memory. Version control (`git diff`) and real files are your only workspace.
2. **Fact Grounding Protocol**: Before rewriting any technical or scientific section, cross-reference the project's source code, technical specifications, or domain documentation. Never invent nonexistent APIs, protocol mechanisms, or unverified claims.
3. **Strict Meaning Lock**: Freeze all mathematical expressions (`$ ... $`), typesetting macros (Typst/LaTeX `#figure`, `\begin{...}`), citation keys (`@key`, `\cite{...}`), cross-reference labels (`<label>`), benchmark values, and empirical metrics.
4. **No Isolated Mini-Slogans (The Movie-Trailer Fallacy)**: NEVER append artificial 3-5 word dramatic slogans to the end of paragraphs (*"The trade-off was fatal"*, *"Security ended at the perimeter"*, *"Determinism ceased to exist"*, *"Auditing is not prevention"*). Commercial detectors flag this as `Predictable sentence endings`.
5. **No Generic AI Openers**: Never start chapters or sections with generic templates like *"Modern software engineering relies heavily on..."*. Begin directly with operational engineering realities or physical constraints.

### The 4-Step Pipeline with Automated Retry Loop:

1. **Step 1: Macro-Composition Check (`writing-suite macro <file>`)**:
   Run `writing-suite macro <file>` to inspect the structural balance. If subsections are micro-fragmented (< 90 words), coalesce them into continuous narrative sections before editing.
2. **Step 2: Sentence-by-Sentence AI Heatmap (`writing-suite suggest <file>`)**:
   Run `writing-suite suggest <file>` to extract sentence-level DeBERTa-v3 probabilities on Apple Silicon Metal MPS and structural flaws (`[ISOLATED_SHORT_SLOGAN]`, `[CHATGPT_INTRO_OPENER]`, `[LEFT_BRANCHING_SUBORDINATE]`). Identify all sentences flagged with 🔴 AI (> 65%) or 🟡 Mixed.
3. **Step 3: Surgical In-Place Rewrite with Rules 36–39**:
   Rewrite flagged sentences directly on the document file applying the 4 core pillars:
   * **Rule 36 (Colon Protocol)**: Assertion followed by an explanatory colon (`:`) and real-world friction.
   * **Rule 37 (Breather Sentence)**: An 8–14 word reflective bridge explaining human/engineering dilemma (NOT an isolated 4-word dramatic fragment).
   * **Rule 38 (Ontological Negation)**: Explicitly state what the system *cannot* or *does not* possess.
   * **Rule 39 (Cost Decompression)**: Articulate the operational price of design decisions.
4. **Step 4: Closed-Loop Verification & Automated Retry Loop (DO NOT STOP IF NOT GREEN)**:
   - Run `writing-suite evaluate <file>` to measure the overall AI risk and DeBERTa MPS score.
   - Run `typst compile main.typ` (or `pdflatex`) to verify 0 syntax errors.
   - **Automated Retry Condition**:
     - If compilation fails: fix Typst syntax immediately and recompile.
     - If DeBERTa MPS score remains > 25-30% or if `writing-suite suggest` still reports 🔴 sentences: **DO NOT STOP AND DO NOT ASK FOR PERMISSION**. Re-run `writing-suite suggest <file>` and execute a second surgical pass ONLY on the remaining 🔴 sentences until the file is firmly in the **🟢 Safe Zone (DeBERTa $\le 25-30\%$, $\sigma > 10.0$)** and compiles with 0 errors.

---

## 4. The 26 Tells: Complete Bilingual Catalogue (EN & IT)

Systematically scan for and eliminate all 26 signs of AI writing:

### Category A: Staging Instead of Stating

#### 1. Not X but Y (Non solo X ma Y) — *Strongest Tell*
* **Watch for**: *not X but Y*; *not just / not only X, but rather Y*; *it's not X, it's Y*; *Non solo X, ma anche Y*; *Non è semplicemente X, ma rappresenta Y*.
* **Problem**: The negative half invents an objection no one made to inflate the positive half. State the point directly.
* **EN Before**: *It is not merely a cryptographic tool, but rather a paradigm shift in distributed trust.*
* **EN After**: *The protocol reduces validation latency across distributed nodes.*
* **IT Before**: *Non è solo una scelta implementativa, ma rappresenta il vero cuore pulsante dell'architettura.*
* **IT After**: *L'architettura adotta questa soluzione per garantire la persistenza off-chain dei dati.*

#### 2. One-line closers and dramatic fragments (Frasi a effetto isolate / Movie-Trailer Fallacy)
* **Watch for**: One-sentence paragraphs, dramatic mic-drops, or isolated 3-5 word dramatic slogans at paragraph ends (*"The trade-off was fatal."*, *"Security ended at the perimeter."*, *"The attack succeeds in silence."*, *"Determinism ceased to exist."*, *"Auditing is not prevention."*, *"Adoption stalled immediately."*, *"That is the real win."*, *"Let that sink in."*, *"Questo fa la differenza."*, *"È qui che cambia tutto."*).
* **Problem**: Detectors flag these as `Predictable sentence endings` and `Repetitive sentence patterns`. Language models append them to simulate profound punchlines.
* **Rule**: NEVER end paragraphs with isolated 3-5 word dramatic slogans. Either eliminate them entirely or merge them into the preceding sentence using an explanatory colon (:) followed by concrete technical consequences.
* **EN Before**: *Caching cuts repeat queries. That is the real win.*
* **EN After**: *Caching cuts repeat network queries: downstream services avoid redundant compute overhead during traffic spikes.*
* **EN Before**: *Traditional registries rely on TLS tunnels. Security ended at the perimeter.*
* **EN After**: *Traditional registries rely on channel encryption: transport TLS handshakes authenticate edge caches without verifying payload integrity.*
* **IT Before**: *L'adozione dello sharding riduce il carico sui validatori. È qui che cambia tutto.*
* **IT After**: *L'adozione dello sharding distribuisce il carico computazionale tra insiemi indipendenti di validatori.*

#### 3. Sayings that sound deep (Aforismi e frasi a effetto vuote)
* **Watch for**: *at its core*, *the heart of the matter*, *X is the Y of Z*, *X becomes a trap*, *nel suo nucleo più profondo*, *è lo specchio di*.
* **Problem**: Pompous philosophical generalities masquerading as technical insight. Replace with the factual claim.
* **EN Before**: *At its core, efficiency becomes a trap when teams forget the human layer.*
* **EN After**: *Over-optimizing workflows often makes interfaces harder for users to navigate.*
* **IT Before**: *Nel suo nucleo essenziale, la decentralizzazione è lo specchio della fiducia collettiva.*
* **IT After**: *I protocolli decentralizzati distribuiscono la validazione per eliminare singoli punti di fallimento.*

#### 4. Staged run-up before the point (Incipit teatrali o finta confidenza)
* **Watch for**: *Let's dive in*, *Here's what you need to know*, *Honestly?*, *Real talk*, *Immergiamoci in*, *Senza ulteriori indugi*, *Ecco cosa devi sapere*.
* **Problem**: Announcing the point or staging fake intimacy instead of stating the fact. Remove the warmup completely.
* **EN Before**: *Let's dive into how batching works in smart contracts. Here is what you need to know.*
* **EN After**: *Multicall batching aggregates multiple contract interactions into a single atomic transaction.*
* **IT Before**: *In questo capitolo ci immergeremo nei dettagli dell'algoritmo di consenso.*
* **IT After**: *L'algoritmo di consenso si articola su tre fasi di voto asincrono.*

#### 5. Arguing with no one / Naive Approach Trap (Approccio ingenuo)
* **Watch for**: *A naive approach would be...*, *One might be tempted to...*, *Un approccio ingenuo suggerirebbe...*, *Si potrebbe pensare che...*.
* **Problem**: Setting up strawman alternatives to make the chosen design look inevitable. State the actual design directly.
* **EN Before**: *A naive approach would be to store raw payloads on-chain, but that causes state bloat. We use Merkle trees.*
* **EN After**: *We store Merkle roots on-chain while keeping raw payloads in distributed storage to prevent state bloat.*
* **IT Before**: *Un approccio ingenuo suggerirebbe di salvare tutti i file on-chain. Tuttavia questo porta a pura follia. Il sistema usa SWH.*
* **IT After**: *Il sistema registra gli identificatori SWHID on-chain, preservando l'integrità del codice senza appesantire lo stato dei nodi.*

---

### Category B: Rhythm by Rule

#### 6. Forced triads (Triadi artificiose)
* **Watch for**: Ideas arbitrarily grouped in threes (*"innovation, inspiration, and insights"*, *"...per tre ragioni fondamentali"*, *"resilienza, efficienza e scalabilità"*).
* **Problem**: Forcing reality into a three-part cadence. Keep only the items that carry distinct, necessary facts.
* **EN Before**: *The system delivers security, scalability, and seamless integration.*
* **EN After**: *The system improves transaction throughput while preserving verification security.*
* **IT Before**: *L'architettura garantisce resilienza, efficienza e innovazione per tre ragioni fondamentali.*
* **IT After**: *L'architettura riduce la latenza di rete e limita l'occupazione di memoria.*

#### 7. Repeated sentence openings (Aperture seriali monotone)
* **Watch for**: Three or four consecutive sentences starting with the same subject or pronoun (*"She noted... She noted... She filed..."*, *"Il protocollo... Il protocollo... Il protocollo..."*).
* **Problem**: Inability to manage variety by ear. Invert clauses, merge sentences, or open with the action or adverbial phrase.
* **EN Before**: *The node validates the block. The node updates its local state. The node broadcasts the hash.*
* **EN After**: *After validating the incoming block, the node updates its local state and broadcasts the hash.*

#### 8. Dashes as the universal connector (Abuso spietato di trattini — e --) — *Critical AI Tell*
* **Rule**: **The final rewrite must not contain em dashes (`—`), en dashes (`–`), or double hyphens (`--` or ` -- `) used as connectors.**
  * In English, replace with commas, parentheses, colons, or split into two periods.
  * In Italian, em-dashes and double hyphens are almost exclusively translation artifacts of LLMs; in natural Italian, use commas or round brackets.
  * *Exception*: Keep hyphens inside code blocks, inline code (`--flag`), compound words, and URLs.
* **EN Before (spaced & unspaced)**: *The consensus layer — developed under strict deadlines — synchronizes validator nodes. The system—designed for speed—works.*
* **EN After**: *Developed under strict deadlines, the consensus layer synchronizes validator nodes. Designed for speed, the system works.*
* **IT Before**: *Il relayer -- componente critico del layer off-chain -- raggruppa le transazioni prima dell'invio.*
* **IT After**: *Il relayer, componente fondamentale del layer off-chain, raggruppa le transazioni prima dell'invio.*

#### 9. Stacked qualifiers (Aggettivi e avverbi accumulati)
* **Watch for**: *quite fairly unique*, *incredibly vital and extremely crucial*, *particolarmente fondamentale e straordinariamente efficace*.
* **Problem**: Stacking modifiers to compensate for weak nouns or verbs. Cut the adverb stack; choose a specific noun.

#### 10. Hyphenated pairs everywhere (Coppie di parole con trattino)
* **Watch for**: *cost-effective, multi-layered, cutting-edge, future-proof, user-centric*.
* **Problem**: Corporate buzzword shorthand. Unpack into what the system actually does.

#### 11. Passive voice and missing subjects (Passivi impersonali pervasivi)
* **Watch for**: *It was decided that*, *It has been observed that*, *È stato rilevato che*, *Si è proceduto alla configurazione*.
* **Problem**: Obscuring who did what. Turn into active voice when the agent is known (*"We configured..."*, *"I validatori verificano..."*).

---

### Category C: Inflation & Borrowed Authority

#### 12. Overused AI stock words (`WS-LEX-001`, `WS-LEX-002`)
* **Watch for**: *delve, pivotal, crucial, beacon, testament, intricate tapestry, seamless, foster, landscape, holistic, linfa vitale, pietra miliare, catalizzatore, senza soluzione di continuità*.
* **Rule**: Strip or replace with direct, plain vocabulary.

#### 13. Inflated significance & Tech Hyperboles (`WS-LEX-003`)
* **Watch for**: *revolutionary paradigm shift, groundbreaking milestone, pura follia architetturale, design pattern aureo, immutable root of trust*.
* **Rule**: State concrete benchmarks and empirical engineering trade-offs instead of dramatic proclamations.

#### 14. Vague connection or association (Connessioni vaghe: "linked to", "associated with")
* **Watch for**: Asserting two concepts are "intimately connected" or "deeply linked" without stating the causal or technical mechanism.
* **Rule**: State the exact relationship (e.g. *"increases memory usage by $O(N)$"*, not *"is inextricably linked to memory dynamics"*).

#### 15. Shallow -ing riders and trailing gerunds (`WS-RID-001`, `WS-RID-003`)
* **Watch for**: Trailing participial phrases tacked onto the end of sentences (*", highlighting the importance of"*, *", thereby ensuring"*, *", garantendo al contempo"*, *", delegando al client"*).
* **Rule**: Remove the rider or turn it into an active, coordinated clause with concrete details.
* **EN Before**: *The contract checks balances, thereby ensuring optimal gas consumption while fostering trust.*
* **EN After**: *The contract verifies account balances before execution to prevent out-of-gas reverts.*
* **IT Before**: *Il nodo propaga il blocco, garantendo al contempo un'elevata sicurezza e aprendo la strada alla scalabilità.*
* **IT After**: *Il nodo propaga il blocco sulla rete gossip. La validazione parallela riduce i tempi di conferma.*

#### 16. Sales language and promotional puffery (Tono da brochure commerciale)
* **Watch for**: *supercharge, revolutionize, elevate your workflow, potenziale senza precedenti, trasforma radicalmente*.
* **Rule**: Replace marketing hype with sober technical facts.

#### 17. Borrowed authority & sweeping unsupported claims
* **Watch for**: *experts agree*, *studies have shown*, *it is widely acknowledged*, *è ampiamente dimostrato che*, *molti autori concordano*.
* **Rule**: Either cite the specific author/paper (`@key`) or state the technical reason directly.

#### 18. Pompous copula avoidance (Verbi di facciata: "funge da", "serves as")
* **Watch for**: *serves as a testament*, *stands as a pillar*, *funge da catalizzatore*, *si erge a*.
* **Rule**: Use direct verbs: *is*, *are*, *enables*, *provides*, *è*, *costituisce*, *implementa*.
* **EN Before**: *The Merkle tree serves as the foundational cornerstone of the protocol.*
* **EN After**: *The protocol uses a Merkle tree to verify state transitions.*
* **IT Before**: *Il database distribuito funge da catalizzatore per la resilienza dell'infrastruttura.*
* **IT After**: *Il database distribuito mantiene repliche coerenti dello stato tra i nodi.*

---

### Category D: Formatting & Chatbot Residue

#### 19. Bold as decoration & Serial list clusters (`WS-FMT-001`)
* **Watch for**: Serial bullet lists where every item mechanically begins with `**Label:** Description` or `\d+\.\s+\*\*[^*]+\*\*:`.
* **Rule**: Deconstruct into fluid narrative paragraphs or varied, natural bullet points.
* **EN Before**:
  * `1. **Latency:** Minimizes round-trip network time.`
  * `2. **Security:** Enforces cryptographic state checks.`
* **EN After**: *The optimization addresses two constraints: batched requests minimize network round-trips, while cryptographic signatures guarantee state integrity.*

#### 20. Decorative headings
* **Watch for**: Vague, poetic headings (*"Navigating the Landscape of Consensus"*, *"Unlocking the Future of Scalability"*).
* **Rule**: Replace with factual, descriptive headings (*"Consensus Protocol Architecture"*, *"State Validation Latency Benchmarks"*).

#### 21. Curly quotation marks & typographic inconsistencies
* **Watch for**: Inconsistent mixtures of curly quotes (“ ”), straight quotes (" "), and backticks. Standardize cleanly according to file format.

#### 22. Chatbot residue (Residui di conversazione da assistente)
* **Watch for**: *Certainly! Here is...*, *I hope this helps!*, *Spero che questo ti sia utile!*, *Ecco a te una spiegazione dettagliata*.
* **Rule**: Strip all conversational preamble, greeting, and pleasantries. Deliver only the text itself.

#### 23. Knowledge-limit disclaimers and guesses
* **Watch for**: *As of my last update in 2023...*, *Allo stato attuale delle mie conoscenze...*.
* **Rule**: Cut the meta-disclaimer. State what is verified; omit what is speculative.

#### 24. Heading repeated in the first sentence
* **Watch for**: A section heading whose exact words are parroted as the opening words of the first paragraph.
* **Rule**: Begin the paragraph with new information or the core argument.

#### 25. Writing about the document instead of its subject
* **Watch for**: *In this section, we will discuss...*, *Questo capitolo ha lo scopo di esaminare...*.
* **Rule**: State the subject directly (*"The consensus mechanism coordinates validator nodes through three asynchronous voting rounds."*).

#### 26. Re-explaining what the reader already knows
* **Watch for**: Unsolicited introductory lectures on basic concepts (*"As we know, blockchain is a distributed ledger..."*, *"Come è noto, i computer usano il codice binario..."*).
* **Rule**: Cut the elementary background. Address the technical reader at the document's true peer level.

---

### Category E: Narrative Cohesion & Macro-Syntactic Flow

#### 27. Thematic Runway vs. The Preamble Trap (Esordi ancorati vs. Cornici saggistiche astratte)
* **Watch for**: Starting a chapter or section with either an abrupt, context-less claim (*"Typosquatting exploits human typographic error."*) OR the opposite extreme: a high-altitude, philosophical essay cliché (*"Modern software engineering is fundamentally an exercise in composition."*, *"Software distribution has long mirrored the architectural assumptions of its era."*).
* **Problem**: The abstract philosophical preamble triggers commercial detectors (CleverHumanizer, Copyleaks) at 95%+ probability (`template_like_introduction`, `lack_of_personal_voice`, `generic_phrasing`).
* **Rule**: Provide a **grounded technical runway**. Anchor the opening immediately in concrete system entities, real operational commands, and physical attack surfaces, setting the stakes through technical causality rather than cosmic musings.
* **EN Bad (Abstract Preamble)**: *Modern software engineering is fundamentally an exercise in composition. Rather than authoring complex platforms from first principles, contemporary engineering teams construct applications by assembling open-source packages, third-party libraries, and shared runtime frameworks. While this composable architecture accelerates delivery, it introduces an asymmetric security dependency.*
* **EN Good (Grounded Technical Runway)**: *Package registries like PyPI and npm distribute untrusted code directly to millions of developers and production servers. Running a single `pip install` command fetches pre-compiled binary wheels and executes setup scripts with full user privileges. In practice, modern applications assemble hundreds of transitive dependencies, which means a single compromised maintainer token or typosquatted package grants an attacker arbitrary code execution across the deployment pipeline.*

#### 28. Jargon Compression without Explanatory Tissue (Compressione iper-densa)
* **Watch for**: Packing multiple heavyweight domain terms into a single compact sentence without articulating the architectural intuition, trade-off, or failure mode (*"The smart contract validates the SWHID Merkle DAG via zkTLS attestations on Sepolia to prevent dependency confusion."*).
* **Problem**: Reads like a specification datasheet or RFC checklist rather than a dissertation that explains and defends a thesis.
* **Rule**: Apply the **"Unpack & Motivate"** protocol. For every primary design choice, articulate: (1) what specific failure mode it addresses, (2) the architectural intuition behind the choice, and (3) why simpler alternatives fall short.
* **EN Before**: *PyChain records SWHID references in an EVM contract on Sepolia, ensuring dependency immutability.*
* **EN After**: *Rather than storing large archive blobs directly on-chain—an approach that would impose prohibitive gas costs and induce rapid state bloat—PyChain isolates the cryptographic identity of the release. It records Software Heritage persistent identifiers (SWHIDs) inside an EVM smart contract on Sepolia. Because an SWHID is computed deterministically from the Merkle DAG of the directory tree, the on-chain entry acts as an immutable anchor: any retroactive tampering with package contents immediately invalidates the cryptographic root.*

#### 29. Left-Branching Subject Overload (Sfilza di nomi prima del verbo)
* **Watch for**: Stacking three or more coordinated subjects or heavy noun phrases before the main predicate (*"[The reference implementation, empirical testbed on the Sepolia network, and security validation suite] [provide] concrete validation..."*).
* **Problem**: Excessive cognitive load. Forces the reader's working memory to hold multiple concepts suspended before discovering what action is taking place.
* **Rule**: Convert to **Right-Branching syntax**. Front the core predicate action, or introduce a framing clause early, followed by an articulated enumeration or colon structure.
* **EN Before**: *Debian introduced dpkg and apt, Red Hat developed rpm and yum, and FreeBSD introduced its ports collection.*
* **EN After**: *Operating systems responded to this operational burden by introducing integrated package management systems: Debian pioneered dpkg and apt, Red Hat deployed rpm alongside yum, and FreeBSD implemented its ports collection.*
* **EN Before**: *The reference implementation, empirical testbed on the Ethereum Sepolia network, and security validation suite provide concrete validation.*
* **EN After**: *Our empirical validation rests on three complementary artifacts: the reference implementation, a live testbed deployed to Ethereum Sepolia, and a dedicated security test harness.*

#### 30. Island Paragraphs & Missing Connective Tissue (Paragrafi-isola senza cerniere)
* **Watch for**: Adjacent paragraphs that read like isolated bullet points pasted together, each opening cold with a new noun phrase without referencing the preceding tension or conclusion.
* **Problem**: Lacks narrative flow; the thesis feels like an arbitrary collection of detached thoughts rather than a cumulative scholarly argument.
* **Rule**: Enforce **Anaphoric Bridges & Causal Hinges**. The opening sentence of every paragraph (except the very first) must explicitly bridge the previous thought using causal, concessive, or anaphoric markers (*"This divergence...", "Having established the boundary of...", "To reconcile these opposing requirements..."*). Avoid mechanical transitions like *"Moreover"*, *"Furthermore"*, *"In addition"*.
* **EN Before**:
  *Par 1 ends*: *...placing the entire burden of dependency resolution on the human operator.*
  *Par 2 begins*: *Operating system distributions introduced integrated package managers.*
* **EN After**:
  *Par 1 ends*: *...placing the entire burden of dependency resolution on the human operator.*
  *Par 2 begins*: *To alleviate this operational friction, mid-1990s Unix distributions introduced integrated package managers.*

---

### Category F: The Authentic Engineering Voice & Syntactic Asymmetry

#### 31. Indefinite / Pragmatic Determinism ("Some" vs. "The Universal")
* **Watch for**: Rigid, textbook determiners (*"the centralized SQL database"*, *"the remote server"*, *"the repository mirrors"*).
* **Problem**: LLMs strictly select textbook determiners, resulting in near-zero token perplexity. Human engineers speak with pragmatic informality (*"querying some private SQL database on AWS"*, *"scattered across arbitrary mirrors"*).
* **Rule**: Inject natural indefinite modifiers where appropriate.
* **EN Before**: *Instead of querying the centralized relational database hosted by the cloud provider...*
* **EN After**: *Instead of querying some private SQL database hosted on AWS...*

#### 32. Inverted & Modal Conditionals (Sintassi ipotetica sciolta)
* **Watch for**: Monotonous, predictable "If X, then Y" patterns (*"If the maintainer account is compromised, the attacker can upload..."*, *"If the signature is invalid, the client aborts..."*).
* **Problem**: Triggers detector signals for `repetitive_sentence_patterns` and `predictable_sentence_endings`.
* **Rule**: Invert conditionals using subjunctive/modal fronting (*"Should the signature fail..."*, *"Were an attacker to compromise..."*).
* **EN Before**: *If the code in the tarball changes, the hash will not match and pip will abort the installation.*
* **EN After**: *Should the code in the tarball change, or the archive itself point to a spoofed source, the cryptographic hash mismatches immediately and pip refuses the build.*

#### 33. Active Authorial Agency (Voce assertiva del ricercatore)
* **Watch for**: Endless passive constructions or detached 3rd-person phrasing (*"In this dissertation, an architecture is proposed..."*, *"It can be observed that..."*).
* **Problem**: Triggers `lack_of_personal_voice` and `emotionally_neutral_tone`.
* **Rule**: State the authorial stance directly with first-person plural (*"We built PyChain around a simple requirement..."*, *"In our testbed, we observed that..."*, *"We propose a decentralized ledger architecture..."*).

#### 34. Concrete Systems Verbs vs. Pompous Copulas
* **Watch for**: Pompous, weak copulas (*"serves to facilitate"*, *"stands as an implementation of"*, *"functions as a mechanism for"*, *"encompasses the entirety of"*).
* **Problem**: Classic LLM inflation.
* **Rule**: Replace with muscular systems verbs (*"refuses the build"*, *"records"*, *"tampers with"*, *"indexes"*, *"spoofs"*, *"chokes on"*).
* **EN Before**: *This mechanism serves to facilitate the verification of integrity proofs.*
* **EN After**: *This mechanism verifies integrity proofs directly on-chain.*

#### 35. Asymmetrical Clause Breaking (Anti-Antithesis)
* **Watch for**: Perfectly balanced, symmetrical clauses (*"While X accelerates A, it introduces B."*, *"Not only does it improve latency, but it also enhances throughput."*).
* **Problem**: Detectors flag `symmetrical_sentence_construction` and `artificially_balanced_arguments`.
* **Rule**: Break the symmetry. State the drawback or constraint in its own independent, direct sentence with varied cadence.
* **EN Before**: *While composable package ecosystems accelerate application delivery, they introduce asymmetric security vulnerabilities.*
* **EN After**: *Composable package ecosystems drastically accelerate application delivery. Yet they create an asymmetric security boundary: downstream code blindly inherits every vulnerability and maintainer compromise in its dependency graph.*

#### 36. The Explanatory Colon Protocol (I Due Punti Esplicativi al posto degli Em-Dashes)
* **Watch for**: Em-dashes (`—` or `--`) used as lazy connectors, or artificial 3-4 word slogans tacked onto paragraphs (*"Integrity is absolute"*, *"Perimeter defenses have failed"*).
* **Problem**: Detectors flag em-dashes as synthetic filler and short slogans as ChatGPT punchlines.
* **Rule**: Formulate the primary assertion directly, then use an explanatory colon (`:`) followed by the physical/engineering friction.
* **EN Before**: *Software supply chains are vulnerable. Perimeter defenses have failed.*
* **EN After**: *This paradigm of modular development has introduced a severe architectural vulnerability: application trust is entirely transitive, as production platforms inherit the security posture of all direct and transitive dependencies.*

#### 37. The Breather Connector Sentence (Frasi-Respiro da 8-14 Parole, NOT 4-Word Movie Slogans)
* **Watch for**: Uniform sentence length where every single sentence in the paragraph has between 22 and 30 words (the LLM metronome), OR the opposite extreme: artificial 3-4 word dramatic slogans appended to every paragraph (*"The trade-off was fatal"*, *"Security ended at the perimeter"*).
* **Problem**: Copyleaks and CleverHumanizer immediately flag `Uniform sentence length` or `Predictable sentence endings`.
* **Rule**: Directly between two dense, 30+ word compound periods, insert an organic, reflective bridge (8–14 words) explaining the human, operational, or engineering dilemma. It MUST NOT be a 3-5 word theatrical fragment.
* **Bad**: *Security ended at the perimeter.* (5 words, theatrical AI closer).
* **Bad**: *The trade-off was fatal.* (5 words, melodramatic closer).
* **Good**: *In other words, the trust is transitive and, by extension, inherently unbounded.* (12 words, organic technical bridge).
* **Good**: *Downstream services accept these risks because verifying every transitive commit is practically impossible.* (13 words, reflective human reality).

#### 38. Functional Ontological Negation (Negazione Ontologica Operativa)
* **Watch for**: Vague, abstract passive formulations (*"trust becomes transitive"*, *"security is compromised"*).
* **Problem**: Triggers `lack_of_personal_voice` and `emotionally_neutral_tone`.
* **Rule**: State what the system fundamentally *cannot* or *does not* possess, articulating the human boundary.
* **EN Before**: *An application executing in production inherits the security posture of every library.*
* **EN After**: *A production application does not possess a meaningful notion of safety or security since it is only as trustworthy as the deepest transitive dependency it has ever attempted to import and execute.*

#### 39. Decompression of Operational Costs (Esplicitazione del Costo Sistemico)
* **Watch for**: Hyper-compressed textbook definitions that skip the real-world trade-off.
* **Rule**: Articulate the price paid for convenience (*"Despite the productivity gains enabled by X, it comes at a steep price: ... "*).
* **EN Before**: *Centralized package registries improve developer productivity but create single points of failure.*
* **EN After**: *Despite the enormous productivity gains enabled by this modular approach, it comes at a steep price: the system under development becomes highly dependent on the quality and intent of unrelated third-party contributors.*

---

## 5. Modes of Output

* **Pasted Text / Interactive Snippet (Default)**:
  Return the rewritten text, followed by an objective before/after audit badge:
  > **Audit Risultato**: Rischio AI: `88.2% 🔴` $\rightarrow$ `14.5% 🟢` | Linter tells: `9` $\rightarrow$ `0` | Cadenza: $\sigma = 14.8$ parole | Trattini/Dashes eliminati: `4`.
* **File Mode**:
  When given a path (`.typ`, `.tex`, `.md`), perform the full rewrite directly in-place, strictly preserving all document metadata, comments, and markup.

---

## 6. When NOT to Act (False Positive Prevention)

* **Direct Quotations**: Never edit text inside direct quotation marks or historical excerpts.
* **Pre-2022 Literature**: Texts written before November 2022 are authentic human writing by definition; never sanitize historical idiosyncrasies.
* **Domain Acronyms & Nomenclature**: Never replace standard scientific or technical terms (*zero-knowledge proofs*, *Merkle DAG*, *CRISPR-Cas9*, *res judicata*) with generic synonyms.
