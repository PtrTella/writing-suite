"""
Writing Suite - Linter Module
Database avanzato di 50+ regole e pattern statistici derivati da:
1. Catalogo dei 50 segnali diagnostici di CleverHumanizer.ai
2. Pattern di prevedibilità di Copyleaks & Turnitin (formule fisse, riders participiali, transizioni forzate)
3. Segni di scrittura AI documentati da Wikipedia (blader/humanizer)
4. Cliché accademici e retorici frequenti nei modelli generativi
"""

import re

RULES = [
    # --- A. SINTASSI E FORME STRUTTURALI TIPICHE DEI MODELLI ---
    {
        "id": "WS-SYN-001",
        "category": "Sintassi da Modello",
        "severity": "CRITICAL",
        "weight": 4.0,
        "name": "Contrasto vuoto 'Non solo X ma Y'",
        "regex": r"(?i)\b(?:non (?:è|sia|si tratta di) (?:solo|soltanto|semplicemente|un semplice) [^.!?\n]+?,? ma (?:è|sia|di|rappresenti|rappresenta|costituisca|costituisce|anche)|not (?:only|just|merely) [^.!?\n]+?,? but (?:also|rather))\b",
        "explanation": "Costrutto artificiale tipico dei modelli per conferire enfasi retorica senza aggiungere contenuto fattuale."
    },
    {
        "id": "WS-SYN-002",
        "category": "Chiusure Teatrali",
        "severity": "CRITICAL",
        "weight": 3.5,
        "name": "One-line closer isolata",
        "regex": r"(?im)^(?:\s*[-*]\s*)?(?:questo fa la differenza|lascia che questo si depositi|è qui che cambia tutto|let that sink in|that is the real win|this changes everything|read that again)\.?$",
        "explanation": "Frase ad effetto isolata a fine paragrafo per forzare una pausa emotiva senza aggiungere argomentazioni."
    },
    {
        "id": "WS-SYN-003",
        "category": "Difesa Fantasma",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Anticipazione obiezioni inesistenti",
        "regex": r"(?i)\b(?:non sto dicendo che [^.!?\n]+?,? ma|non si vuole affermare che|i'?m not saying that|this is not to say that|don'?t get me wrong)\b",
        "explanation": "Il testo risponde preventivamente a un'obiezione che nessuno ha sollevato, residuo dei prompt di istruzione."
    },
    {
        "id": "WS-SYN-004",
        "category": "Incipit Template",
        "severity": "HIGH",
        "weight": 3.0,
        "name": "Incipit stereotipato temporale/mondiale",
        "regex": r"(?i)\b(?:nel mondo frenetico di oggi|nel panorama (?:contemporaneo|attuale|moderno) in continua evoluzione|in today'?s (?:fast-paced|digital|rapidly changing|rapidly evolving|interconnected) (?:world|landscape|society)|nell'?era (?:digitale|dell'?informazione|dell'?intelligenza artificiale)|in an era (?:of|where|characterized by))\b",
        "explanation": "Apertura generica a stampino (tipica di ChatGPT) usata per contestualizzare in modo vacuo qualunque argomento."
    },
    {
        "id": "WS-SYN-005",
        "category": "Transizioni Formule",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Formule di conclusione o transizione forzata",
        "regex": r"(?i)(?:^|[.!?]\s+)(?:in conclusion|to sum up|in summary|all in all|tirando le somme|in conclusione|in definitiva|per riassumere),?\b",
        "explanation": "Riepilogo forzato e prevedibile tipico delle risposte strutturate da chatbot scolastico."
    },

    # --- B. PARTICELLE E RIDERS PARTICIPERIALI (COPYLEAKS PATTERNS) ---
    {
        "id": "WS-RID-001",
        "category": "Riders Participiali",
        "severity": "HIGH",
        "weight": 2.5,
        "name": "Clausole finali -ing posticce",
        "regex": r"(?i),\s*(?:aprendo la strada a|evidenziando l'?importanza di|sottolineando la necessità di|garantendo al contempo|highlighting the (?:importance|need|critical)|underscoring the (?:importance|significance)|thereby ensuring|fostering a sense of)\b",
        "explanation": "Clausola participiale agganciata a fine frase per conferire artificialmente profondità a un'affermazione semplice."
    },
    {
        "id": "WS-RID-002",
        "category": "Lessico di Facciata",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Verbi artificiosi per evitare 'essere' o 'avere'",
        "regex": r"(?i)\b(?:stands as a testament|serves as a (?:crucial|vital|pivotal|prime) example|funge da (?:pilastro|catalizzatore|ponte|volano)|si configura come|si pone come testimonianza|si erge a|boasts a (?:wide|rich))\b",
        "explanation": "Sostituzione forzata di predicati semplici con perifrasi ridondanti ad alta probabilità di completamento."
    },

    # --- C. METAFORE LOGORE E BUZZWORDS DEI MODELLI ---
    {
        "id": "WS-MET-001",
        "category": "Metafore Logore",
        "severity": "HIGH",
        "weight": 3.0,
        "name": "Metafore cliché dell'AI",
        "regex": r"(?i)\b(?:un faro di (?:speranza|innovazione|luce)|tessere una (?:trama|narrazione|tessitura)|un testamento duraturo|la linfa vitale di|rappresenta una pietra miliare|a testament to|beacon of (?:hope|innovation)|tapestry of|vital lifeblood|intricate tapestry)\b",
        "explanation": "Metafore stereotipate che compaiono con frequenza sproporzionata nei corpora generati da LLM."
    },
    {
        "id": "WS-LEX-001",
        "category": "Lessico Sovrarappresentato",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Formule di importanza fittizia",
        "regex": r"(?i)\b(?:è (?:fondamentale|cruciale|imprescindibile|doveroso) (?:sottolineare|notare|evidenziare|comprendere) (?:che|come)|gioca un ruolo (?:cruciale|fondamentale|chiave)|it is (?:crucial|pivotal|essential|worth noting) that|plays a (?:pivotal|crucial) role)\b",
        "explanation": "Riempitivo statistico usato dall'AI per segnalare rilevanza anziché dimostrarla con dati o argomentazioni."
    },
    {
        "id": "WS-LEX-002",
        "category": "Lessico Sovrarappresentato",
        "severity": "MEDIUM",
        "weight": 1.5,
        "name": "Parole buzzword tipiche dei modelli",
        "regex": r"(?i)\b(?:delve|pivotal|seamlessly|holistic|synergy|foster|intricacies|cornerstone|paradigm shift|panacea|a passo con i tempi|senza soluzione di continuità|approccio olistico|unravel|ever-evolving)\b",
        "explanation": "Vocaboli ad alta probabilità statistica nei token di completamento standard."
    },

    # --- D. PUNTEGGIATURA E FORMATTAZIONE ---
    {
        "id": "WS-PUN-001",
        "category": "Punteggiatura",
        "severity": "LOW",
        "weight": 1.0,
        "name": "Em-dash o En-dash come connettore universale",
        "regex": r"(?:[\w\s]—[\w\s]|[\w\s]–[\w\s]| -- )",
        "explanation": "Uso massiccio del trattino lungo al posto di subordinate, parentesi o punteggiatura standard."
    },
    {
        "id": "WS-STR-001",
        "category": "Staged Run-up",
        "severity": "HIGH",
        "weight": 3.0,
        "name": "Apertura teatrale o finta confidenza",
        "regex": r"(?i)\b(?:in questo capitolo ci immergeremo|senza ulteriori indugi|immergiamoci in|let'?s (?:dive in|explore|take a closer look)|here'?s the thing|let'?s be honest|real talk)\b",
        "explanation": "Dichiarazione teatrale dell'azione prima di esporla o finta intimità con il lettore."
    },
    {
        "id": "WS-SYN-006",
        "category": "Sintassi da Modello",
        "severity": "HIGH",
        "weight": 3.5,
        "name": "Costruzione a finto dilemma o approccio ingenuo",
        "regex": r"(?i)\b(?:un approccio ingenuo (?:suggerirebbe|potrebbe|porterebbe)|a (?:naive|tempting) approach would (?:be|suggest)|one might be tempted to|rather than (?:evaluating|relying|using|adopting) [^,]+,\s*(?:we|this approach|the system)|anziché [^,]+,\s*(?:abbiamo|il sistema|questo approccio))\b",
        "explanation": "Costruzione retorica a finto dilemma o 'approccio ingenuo' per introdurre la propria soluzione come unica via razionale (Sign of AI writing §5)."
    },
    {
        "id": "WS-SYN-007",
        "category": "Sintassi da Modello",
        "severity": "HIGH",
        "weight": 3.0,
        "name": "Domanda retorica con auto-risposta immediata",
        "regex": r"(?i)\?\s*(?:La risposta (?:risiede|è|si trova|sta)|The answer (?:lies in|is|comes down to)|Why does this matter\?|How does this work\?)\b",
        "explanation": "Domanda retorica a cui il testo risponde immediatamente da solo, tipico formato didascalico da chatbot."
    },
    {
        "id": "WS-RID-003",
        "category": "Riders Participiali",
        "severity": "HIGH",
        "weight": 2.5,
        "name": "Clausola gerundio / participio agganciata a fine frase",
        "regex": r"(?i),\s*(?:garantendo|delegando|permettendo|consentendo|facilitando|eliminando|assicurando|rendendo (?:il|la|l'|i|le)|evitando di|spostando totalmente|thereby ensuring|thereby enabling|thereby reducing|allowing for a|ensuring that)\b",
        "explanation": "Clausola gerundio o participiale posticcia agganciata con virgola per chiudere un periodo in modo enfatico o riassuntivo."
    },
    {
        "id": "WS-RID-004",
        "category": "Lessico di Facciata",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Perifrasi per evitare il verbo 'essere' in definizioni",
        "regex": r"(?i)\b(?:funge (?:esclusivamente |meramente )?da|acts (?:exclusively |merely )?as (?:an?|the)|serves (?:exclusively |merely )?as (?:an?|the))\b",
        "explanation": "Perifrasi per evitare il verbo 'essere' o 'rappresentare' in definizioni tecniche (Sign of AI writing §18)."
    },
    {
        "id": "WS-STR-002",
        "category": "Struttura Rigida",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Annuncio rigido di triadi o dimensioni prefissate",
        "regex": r"(?i)\b(?:per tre ragioni fondamentali|for three (?:fundamental|key|primary) reasons|quattro dimensioni critiche|four critical dimensions|in modo sincrono:|il flusso ideale diventa il seguente:|for the following reasons:)\b",
        "explanation": "Annuncio rigido di triadi o dimensioni prefissate tipico delle risposte strutturate da modello."
    },
    {
        "id": "WS-LEX-003",
        "category": "Lessico Sovrarappresentato",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Cliché enfatici o iperbolici per scelte architetturali software",
        "regex": r"(?i)\b(?:pura follia architetturale|design pattern aureo|immutable root of trust|cost of trust|shift(?:s)? the security paradigm|paradigmatic shift|holy grail of|passo evolutivo obbligato)\b",
        "explanation": "Iperboli o formule solenni usate dai modelli per descrivere scelte architetturali software ordinarie."
    }
]

def lint_text(text: str) -> list[dict]:
    """Scansiona il testo linea per linea e strutturalmente rilevando le occorrenze delle regole."""
    findings = []
    lines = text.split("\n")

    # 1. Scansione linea per linea per regole regolari
    for line_idx, line in enumerate(lines, 1):
        line_clean = line.strip()
        if not line_clean:
            continue
        for rule in RULES:
            matches = re.finditer(rule["regex"], line)
            for m in matches:
                findings.append({
                    "id": rule["id"],
                    "line": line_idx,
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "category": rule["category"],
                    "weight": rule["weight"],
                    "matched_text": m.group(0).strip(),
                    "explanation": rule["explanation"]
                })

    # 2. Rilevamento cluster di elenchi con etichette in grassetto (WS-FMT-001)
    bold_list_items = []
    for line_idx, line in enumerate(lines, 1):
        if re.search(r"^\s*(?:[-*+]|\d+\.)\s+\*\*[^*]+?\*\*[:\s-]", line):
            bold_list_items.append((line_idx, line.strip()))

    if len(bold_list_items) >= 3:
        first_line = bold_list_items[0][0]
        # Ponderazione proporzionale al numero di elementi seriali
        cluster_weight = min(5.0, 2.5 + (len(bold_list_items) - 3) * 0.5)
        findings.append({
            "id": "WS-FMT-001",
            "line": first_line,
            "name": "Elenco puntato a etichette in grassetto (Pattern di formattazione AI)",
            "severity": "HIGH",
            "category": "Formattazione AI",
            "weight": round(cluster_weight, 1),
            "matched_text": f"Cluster di {len(bold_list_items)} elementi puntati strutturati a '**Etichetta:** Descrizione'",
            "explanation": "Elenco seriale con ogni punto introdotto sistematicamente da un'etichetta in grassetto, layout tipico generato dai modelli linguistici."
        })

    return findings
