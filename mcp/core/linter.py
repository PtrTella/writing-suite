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
    }
]

def lint_text(text: str) -> list[dict]:
    """Scansiona il testo linea per linea rilevando le occorrenze delle regole."""
    findings = []
    lines = text.split("\n")
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
    return findings
