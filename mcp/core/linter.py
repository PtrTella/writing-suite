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
        "regex": r"(?i)\b(?:non\s+(?:(?:è|sia|si\s+tratta\s+di)\s+)?(?:solo|soltanto|semplicemente)\s+[^.!?\n]+?,?\s+ma\s+(?:anche\s+|invece\s+|una?\s+|il\s+|la\s+|lo\s+|i\s+|le\s+|piuttosto\s+|soprattutto\s+|sopratutto\s+|al\s+contrario\s+|[a-zàèéìòù]+)\b|not\s+(?:only|just|merely)\s+[^.!?\n]+?,?\s+but\s+(?:also\s+|rather\s+|instead\s+|a\s+|an\s+|the\s+|[a-z]+)\b)",
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
        "severity": "MEDIUM",
        "weight": 1.5,
        "name": "Em-dash o doppio trattino come connettore universale",
        "regex": r"(?:[a-zA-ZàèéìòùÀÈÉÌÒÙ]+[—–][a-zA-ZàèéìòùÀÈÉÌÒÙ]+|\s[—–]\s|\s--\s|[a-zA-ZàèéìòùÀÈÉÌÒÙ]+--[a-zA-ZàèéìòùÀÈÉÌÒÙ]+|[—–]\s)",
        "explanation": "Uso massiccio del trattino lungo (—, –) o doppio trattino (--) isolato o attaccato alle parole al posto di subordinate, parentesi o punteggiatura standard."
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
        "regex": r"(?i)\?\s*(?:La risposta (?:risiede|è|si trova|sta|consiste)|The answer (?:lies in|is|comes down to|consists of|can be found in)|Why does this matter\?|How does this work\?)\b",
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
        "regex": r"(?i)\b(?:funge (?:esclusivamente |meramente )?da (?:pilastro|catalizzatore|ponte|volano|guida|faro|ancora|collante|indice|tramite)|serves as a (?:testament|crucial|vital|pivotal|compelling|prime|lasting|powerful|strong) example|acts as a (?:testament|vital pillar|prime catalyst))\b",
        "explanation": "Perifrasi enfatica per evitare il verbo 'essere' o 'rappresentare' in definizioni tecniche (Sign of AI writing §18)."
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
    },
    {
        "id": "WS-SYN-008",
        "category": "Sintassi da Modello",
        "severity": "HIGH",
        "weight": 3.5,
        "name": "Incipit teatrale di contrasto e finta analisi oggettiva",
        "regex": r"(?i)(?:^|[.!?]\s+)(?:tuttavia|nondimeno|ciò\s+nonostante),\s*(?:un\'?\s*(?:analisi\s+(?:attenta|approfondita|accurata|oggettiva|critica)|(?:attenta|approfondita)\s*analisi)|un\s*esame\s*più\s*approfondito|a\s*(?:closer|deeper|more\s*careful|thorough)\s*(?:look|examination|analysis))[^.!?\n]*?\b(?:dimostra|rivela|mostra|ha\s*dimostrato|evidenzia|reveals|shows|demonstrates)\b",
        "explanation": "Formula stereotipata di svolta teatrale in cui il modello simula un'analisi critica oggettiva per rovesciare la premessa precedente."
    },
    {
        "id": "WS-SYN-009",
        "category": "Incipit Template",
        "severity": "HIGH",
        "weight": 3.0,
        "name": "Incipit temporale stereotipato",
        "regex": r"(?i)(?:^|[.!?]\s+)(?:negli\s+ultimi\s+anni|nel\s+corso\s+degli\s+ultimi\s+anni|in\s+recent\s+years|over\s+the\s+past\s+few\s+years),\s*(?:gli\s+|i\s+|le\s+|la\s+|il\s+|we\s+|the\s+|researchers|developers|hacker|aziende)",
        "explanation": "Apertura cronologica convenzionale usata dai modelli per contestualizzare genericamente una problematica tecnica o storica."
    },
    {
        "id": "WS-FMT-002",
        "category": "Formattazione AI",
        "severity": "MEDIUM",
        "weight": 2.5,
        "name": "Etichetta di sezione in grassetto isolata",
        "regex": r"(?im)^\s*(?:#{2,4}\s+)?\*\*(?:Il Problema|La Soluzione|Vantaggio|Vantaggi|Limite|Limiti|Obiettivo|Conclusione|Risposta fondamentale per la tesi|The Problem|The Solution|Key Insight|Core Trade-off|Architectural Pivot)[^*:\n]*:\*\*\s*",
        "explanation": "Marker visivo isolato a etichetta in grassetto per simulare categorizzazione strutturata da chatbot."
    },
    {
        "id": "WS-LEX-004",
        "category": "Lessico Sovrarappresentato",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Cliché enfatici o iperbolici di profondità concettuale",
        "regex": r"(?i)\b(?:cattura l'?essenza pura|radicalmente diverso e molto più profondo|in modo inequivocabile|in un mondo sempre più|risposta architetturale a due dei problemi più pressanti)\b",
        "explanation": "Formule enfatiche ricorrenti generate dai modelli per attribuire profondità filosofica o concettuale ad argomenti tecnici."
    },
    {
        "id": "WS-SYN-006",
        "category": "Incipit Template",
        "severity": "CRITICAL",
        "weight": 4.5,
        "name": "Preamble & Smoothness Trap (Cornice saggistica astratta)",
        "regex": r"(?i)\b(?:is fundamentally (?:an exercise in|a matter of|shifted toward)|has fundamentally shifted toward|rather than authoring [^,]+, contemporary|rather than relying on [^,]+, developers distributed)\b",
        "explanation": "Apertura saggistica astratta ad altissima probabilità nei completamenti di LLM ('Modern software engineering is fundamentally an exercise in composition')."
    },
    {
        "id": "WS-SYN-007",
        "category": "Sintassi da Modello",
        "severity": "HIGH",
        "weight": 3.5,
        "name": "Pivot antitetico artificiale 'While X accelerates A, it introduces B'",
        "regex": r"(?i)\bwhile this [a-z\s]+ accelerates [^,]+, it introduces an? asymmetric\b",
        "explanation": "Clausola concessiva simmetrica altamente predicibile usata dai modelli per bilanciare artificialmente vantaggi e rischi."
    },
    {
        "id": "WS-SYN-008",
        "category": "Lessico di Facciata",
        "severity": "MEDIUM",
        "weight": 2.5,
        "name": "Qualificazione e avverbiazione iperbolica 'fundamentally X'",
        "regex": r"(?i)\b(?:remains fundamentally (?:centralized|opaque|unresolved|vulnerable)|fundamentally localized|fundamentally reflects?)\b",
        "explanation": "Avverbi enfatici vuoti inseriti dai modelli per enfatizzare lo stato di una tecnologia anziché descriverne il meccanismo."
    },
    {
        "id": "WS-SYN-009",
        "category": "Sintassi da Modello",
        "severity": "HIGH",
        "weight": 3.0,
        "name": "Frase di autorità astratta con avversativa a contrasto",
        "regex": r"(?i)\b(?:recent empirical audits confirm that [^,]+, yet the foundational infrastructure remains|empirical investigations into package registry security[^,]+demonstrate that)\b",
        "explanation": "Formula stereotipata di citazione di studi empirici senza ancoraggio a metriche specifiche, seguita da contrasto moraleggiante."
    },
    {
        "id": "WS-LEX-005",
        "category": "Lessico Sovrarappresentato",
        "severity": "MEDIUM",
        "weight": 2.0,
        "name": "Metafore concettuali astratte ('has long mirrored')",
        "regex": r"(?i)\b(?:has long mirrored the architectural assumptions|serves to facilitate|constitutes the bedrock of)\b",
        "explanation": "Copula astratta stereotipata per introdurre panoramiche storiche o concettuali senza dinamismo ingegneristico."
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

    if len(bold_list_items) >= 2:
        first_line = bold_list_items[0][0]
        # Ponderazione progressiva continua (min 2.0 per 2 elementi, max 6.0 per cluster ampi)
        cluster_weight = min(6.0, 2.0 + (len(bold_list_items) - 2) * 0.75)
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

    # 3. Rilevamento chiusure participiali posticce sistematiche (WS-RID-005)
    # Cattura ", <gerundio> ..." a fine frase prima del punto (stile Copyleaks 'Predictable sentence endings')
    ADJECTIVAL_EXCLUSIONS = {
        'operating', 'engineering', 'training', 'underlying', 'computing', 'routing',
        'existing', 'leading', 'remaining', 'missing', 'upcoming', 'incoming', 'manufacturing',
        'surrounding', 'preceding', 'following', 'building', 'binding', 'parsing'
    }
    coda_matches = list(re.finditer(r",\s+(?!(?:according|including|during|concerning|regarding|involving)\b)([a-z]+ing)\b([^.!?\n]{12,}[.!?])", text, re.IGNORECASE))
    if coda_matches:
        for cm in coda_matches:
            verb = cm.group(1).lower()
            rest = cm.group(2).strip()
            
            # Escludi participi con funzione aggettivale seguiti da sostantivo
            if verb in ADJECTIVAL_EXCLUSIONS:
                continue
                
            # Escludi clausole racchiuse all'interno di parentesi
            start_pos = cm.start()
            pre_text = text[:start_pos]
            if pre_text.count('(') > pre_text.count(')'):
                continue
            if rest.count(')') > rest.count('('):
                continue
                
            # Escludi soggetti al gerundio introdotti da virgola dopo proposizioni preposizionali
            sent_start = max(pre_text.rfind('.'), pre_text.rfind('!'), pre_text.rfind('?'), pre_text.rfind('\n'))
            curr_sent_pre = pre_text[sent_start+1:].strip() if sent_start != -1 else pre_text.strip()
            if re.match(r'^(?:In|During|For|Under|With|After|Before|By|Upon|Without|When|While)\b[^.!?]*$', curr_sent_pre, re.IGNORECASE):
                if re.search(r'\b(?:unpacks|executes|provides|enables|requires|creates|demands|yields|allows|triggers|relies|stores|records|verifies|inspects)\b', rest, re.IGNORECASE):
                    continue

            findings.append({
                "id": "WS-RID-005",
                "line": 1,
                "name": "Chiusura participiale posticcia a fine frase (-ing coda)",
                "severity": "HIGH",
                "category": "Riders Participiali",
                "weight": 2.5,
                "matched_text": cm.group(0).strip(),
                "explanation": "Clausola participiale '-ing' agganciata con virgola in chiusura di periodo, pattern di conclusione altamente predicibile dei modelli linguistici."
            })

    # 4. Rilevamento densità patologica di due punti (WS-SYN-010: Elaboration Addiction)
    # Nei testi umani accademici la frequenza dei due punti è rara (< 0.15 per frase).
    # Nei modelli AI, i due punti vengono usati compulsivamente come connettore di elaborazione (ratio >= 0.30 con >= 3 colons).
    raw_sents_count = len(re.split(r"(?<=[.!?])\s+", text.strip()))
    colon_count = text.count(":")
    if raw_sents_count >= 5 and colon_count >= 3:
        colon_ratio = colon_count / raw_sents_count
        if colon_ratio >= 0.30:
            colon_weight = min(5.0, 2.0 + (colon_ratio - 0.30) * 10.0)
            findings.append({
                "id": "WS-SYN-010",
                "line": 1,
                "name": "Eccessiva densità di due punti (Elaboration Addiction da modello)",
                "severity": "HIGH",
                "category": "Sintassi da Modello",
                "weight": round(colon_weight, 1),
                "matched_text": f"{colon_count} due punti in {raw_sents_count} frasi (densità: {colon_ratio:.2f} per frase)",
                "explanation": "Uso compulsivo dei due punti come connettore di elaborazione binaria [affermazione]: [spiegazione], tipico tic dei generatori neurali."
            })

    return findings
