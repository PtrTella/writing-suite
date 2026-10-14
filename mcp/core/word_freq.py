"""
Writing Suite - Word Frequency & Forensic GLTR Engine
Implementa:
1. Lexicon di frequenza Zipf normalizzato e multi-lingua (Italiano & Inglese)
2. Profilazione Forense GLTR (Giant Language Model Test Room - Harvard/MIT) a 4 bucket:
   - Green: Top 10 (Funzioni grammaticali, connettori essenziali)
   - Yellow: Top 100 (Pronomi, verbi ausiliari, preposizioni ad altissima frequenza)
   - Red: Top 1000 (Lessico comune, sostantivi e verbi base)
   - Tail/Purple: Fuori dai Top 1000 (Lessico ricercato, specialistico, idiosincratico umano)
3. MTLD (Measure of Textual Lexical Diversity - McCarthy & Jarvis 2010), invariante rispetto alla lunghezza del testo
4. Entropia di Shannon basata su sorpresa Zipf per frase
"""

import math
import re
from typing import Dict, List, Tuple

# --- TOP 10 (BUCKET 1 - GREEN / ULTRA-PREDICTABLE) ---
TOP_10_IT = {
    "il", "di", "e", "ed", "a", "ad", "la", "in", "che", "per", "un", "una", "sono", "del", "della"
}
TOP_10_EN = {
    "the", "of", "and", "to", "a", "in", "that", "is", "was", "he", "for", "it", "with", "as"
}

# --- TOP 100 (BUCKET 2 - YELLOW / HIGHLY PREDICTABLE) ---
TOP_100_IT = {
    # Articoli, preposizioni articolate, congiunzioni, ausiliari, pronomi
    "lo", "i", "gli", "le", "uno", "da", "dal", "dalla", "dallo", "dai", "dagli", "dalle",
    "su", "sul", "sulla", "sullo", "sui", "sugli", "sulle", "con", "tra", "fra",
    "al", "alla", "allo", "ai", "agli", "alle", "nel", "nella", "nello", "nei", "negli", "nelle",
    "o", "ma", "se", "non", "più", "molto", "tutto", "tutti", "tutta", "tutte",
    "ci", "vi", "si", "ne", "mi", "ti", "ci", "vi", "loro", "suo", "sua", "suoi", "sue",
    "nostro", "nostra", "nostri", "nostre", "questo", "questa", "questi", "queste",
    "quello", "quella", "quelli", "quelle", "come", "anche", "solo", "prima", "dopo",
    "mentre", "ogni", "alcuni", "alcune", "qualche", "quindi", "dunque", "invece",
    "così", "allora", "già", "mai", "sempre", "ancora", "oggi", "ora", "modo", "parte",
    "tempo", "caso", "fatto", "punto", "cosa", "bene", "male", "nuovo", "altro",
    "stesso", "proprio", "grande", "piccolo", "primo", "ultimo", "è", "era", "erano",
    "stato", "stata", "stati", "state", "ha", "hanno", "aveva", "avevano", "può", "possono",
    "deve", "devono", "fare", "fa", "fanno", "fatto", "dare", "da", "danno", "va", "viene"
}

TOP_100_EN = {
    "his", "on", "be", "at", "by", "i", "this", "had", "not", "are", "but", "from",
    "or", "have", "an", "they", "which", "one", "you", "were", "her", "all", "she",
    "there", "would", "their", "we", "him", "been", "has", "when", "who", "will",
    "more", "no", "if", "out", "so", "said", "what", "up", "its", "about", "into",
    "than", "them", "can", "only", "other", "new", "some", "could", "time", "these",
    "two", "may", "then", "do", "first", "any", "my", "now", "such", "like", "our",
    "over", "man", "me", "even", "most", "made", "after", "also", "did", "many",
    "before", "must", "through", "back", "years", "where", "much", "your", "way",
    "well", "down", "should", "because", "each", "just", "those", "people", "how",
    "too", "little", "state", "good", "very", "make", "world", "still", "own", "see"
}

# --- TOP 1000 (BUCKET 3 - RED / STANDARD VOCABULARY & DOMAIN DISCOURSE) ---
TOP_1000_IT = {
    # Sostantivi, verbi e aggettivi di frequenza primaria
    "uomo", "donna", "persona", "persone", "giorno", "giorni", "anno", "anni", "mese", "mesi",
    "vita", "mondo", "paese", "paesi", "città", "casa", "lavoro", "lavori", "scuola", "mano",
    "mani", "occhio", "occhi", "voce", "parola", "parole", "aria", "luce", "notte", "sera",
    "acqua", "terra", "fine", "inizio", "faccia", "storia", "storie", "senso", "forza", "valore",
    "valori", "forma", "forme", "idea", "idee", "momento", "momenti", "ragione", "ragioni",
    "diritto", "diritti", "legge", "leggi", "ordine", "livello", "livelli", "grado", "gradi",
    "numero", "numeri", "linea", "linee", "gruppo", "gruppi", "campo", "campi", "spazio", "spazi",
    "sistema", "sistemi", "processo", "processi", "sviluppo", "funzione", "funzioni", "tipo", "tipi",
    "misura", "misure", "effetto", "effetti", "azione", "azioni", "condizione", "condizioni",
    "rapporto", "rapporti", "società", "cultura", "politica", "economia", "mercato", "prezzo",
    "costo", "costi", "opera", "opere", "progetto", "progetti", "problema", "problemi",
    "soluzione", "soluzioni", "risultato", "risultati", "studio", "studi", "ricerca", "ricerche",
    "dati", "dato", "rete", "reti", "codice", "file", "memoria", "test", "servizio", "servizi",
    "client", "server", "modulo", "moduli", "accesso", "chiave", "chiavi", "fase", "fasi",
    "flusso", "flussi", "tabella", "tabelle", "nodo", "nodi", "protocollo", "protocolli",
    "algoritmo", "algoritmi", "richiesta", "richieste", "risposta", "risposte", "elaborazione",
    "prestazioni", "analisi", "standard", "supporto", "versione", "versioni", "componente",
    "componenti", "database", "pacchetto", "pacchetti", "transazione", "transazioni", "blocco",
    "blocchi", "smart", "contract", "blockchain", "storage", "token", "hash", "indice", "cache",
    "registro", "registri", "dipendenza", "dipendenze", "libreria", "librerie", "relayer",
    "framework", "infrastruttura", "piattaforma", "strumento", "strumenti", "risoluzione",
    "verifica", "integrità", "validazione", "on-chain", "off-chain", "crittografia", "decentralizzato",
    "immutabile", "pubblico", "privato", "principale", "fondamentale", "critico", "complesso",
    "semplice", "diretto", "completo", "totale", "reale", "possibile", "necessario", "presente",
    "chiaro", "diverso", "comune", "attuale", "moderno", "tradizionale", "importante", "noto",
    "sapere", "volere", "potere", "dovere", "dire", "andare", "venire", "vedere", "sentire",
    "trovare", "lasciare", "prendere", "parlare", "mettere", "pensare", "passare", "portare",
    "guardare", "chiamare", "credere", "vivere", "morire", "usare", "utilizzare", "eseguire",
    "creare", "offrire", "permettere", "garantire", "richiedere", "fornire", "gestire",
    "salvare", "scaricare", "calcolare", "elaborare", "definire", "dimostrare", "presentare",
    "verificare", "risolvere", "analizzare", "valutare", "ridurre", "ottimizzare", "eliminare",
    "evitare", "consentire", "rappresentare", "costituire", "includere", "mostrare", "spiegare"
}

TOP_1000_EN = {
    "work", "life", "day", "year", "part", "number", "great", "tell", "men", "say", "small",
    "every", "found", "still", "between", "name", "should", "home", "big", "give", "air",
    "line", "set", "own", "under", "read", "last", "never", "us", "left", "end", "along",
    "while", "might", "next", "sound", "below", "saw", "something", "thought", "both", "few",
    "those", "always", "show", "large", "often", "together", "asked", "house", "don't", "world",
    "going", "want", "school", "important", "until", "form", "food", "keep", "children", "feet",
    "land", "side", "without", "boy", "once", "animal", "life", "enough", "took", "four", "head",
    "above", "kind", "began", "almost", "live", "page", "got", "earth", "need", "far", "hand",
    "high", "year", "mother", "light", "country", "father", "let", "night", "picture", "being",
    "study", "second", "soon", "story", "since", "white", "ever", "paper", "hard", "near", "sentence",
    "better", "best", "across", "during", "today", "however", "sure", "knew", "it's", "try",
    "told", "young", "sun", "thing", "whole", "hear", "example", "heard", "several", "change",
    "answer", "room", "sea", "against", "top", "turned", "learn", "point", "city", "play",
    "toward", "five", "himself", "usually", "money", "seen", "didn't", "car", "morning", "i'm",
    # Academic & Technical core tokens
    "system", "systems", "data", "network", "networks", "code", "model", "models", "process",
    "processes", "architecture", "security", "application", "applications", "user", "users",
    "file", "files", "cost", "costs", "operation", "operations", "result", "results", "memory",
    "test", "tests", "service", "services", "client", "clients", "server", "servers", "module",
    "modules", "value", "values", "state", "states", "access", "project", "projects", "key",
    "keys", "phase", "phases", "flow", "table", "tables", "node", "nodes", "protocol",
    "protocols", "algorithm", "algorithms", "request", "requests", "response", "responses",
    "processing", "performance", "analysis", "problem", "problems", "solution", "solutions",
    "standard", "standards", "support", "version", "versions", "component", "components",
    "database", "databases", "package", "packages", "transaction", "transactions", "block",
    "blocks", "smart", "contract", "contracts", "blockchain", "storage", "token", "tokens",
    "hash", "hashes", "index", "cache", "framework", "function", "functions", "method", "methods",
    "approach", "layer", "layers", "step", "steps", "dimension", "dimensions", "parameter",
    "parameters", "environment", "resource", "resources", "overhead", "latency", "hardware",
    "software", "infrastructure", "registry", "release", "dependency", "dependencies", "tool",
    "tools", "library", "pattern", "design", "structure", "implementation", "level", "evaluation",
    "metric", "benchmark", "validation", "verification", "experiment", "research", "section",
    "provide", "ensure", "allow", "enable", "require", "perform", "demonstrate", "evaluate",
    "present", "implement", "reduce", "increase", "optimize", "maintain", "include", "execute",
    "store", "verify", "validate", "measure", "compare", "indicate", "suggest"
}

def get_word_bucket(word: str, lang: str = "it") -> int:
    """
    Restituisce il bucket forense GLTR del vocabolo:
    1 = Top 10 (Green: Ultra-Prevedibile)
    2 = Top 100 (Yellow: Altamente Prevedibile)
    3 = Top 1000 (Red: Lessico Standard)
    4 = Tail / Rare (Purple: Lessico specialistico, creativo o idiosincratico umano)
    """
    w = word.lower().strip()
    if lang == "it":
        if w in TOP_10_IT:
            return 1
        if w in TOP_100_IT:
            return 2
        if w in TOP_1000_IT:
            return 3
        return 4
    else:
        if w in TOP_10_EN:
            return 1
        if w in TOP_100_EN:
            return 2
        if w in TOP_1000_EN:
            return 3
        return 4

def get_word_zipf(word: str, lang: str = "it") -> float:
    """Stima il valore Zipf della parola (log10 frequenza per miliardo)."""
    bucket = get_word_bucket(word, lang)
    if bucket == 1:
        return 7.0
    elif bucket == 2:
        return 5.8
    elif bucket == 3:
        return 4.6
    else:
        # Coda specialistica / rara
        return 2.5

def calculate_gltr_profile(words: List[str], lang: str = "it") -> Dict:
    """
    Calcola la distribuzione forense GLTR del testo su 4 bucket di probabilità:
    - Green (Top 10)
    - Yellow (Top 100)
    - Red (Top 1000)
    - Purple (Tail / >1000)
    Nei modelli generativi, la saturazione (Green + Yellow + Red) supera spesso il 90-95%,
    mentre il testo umano presenta una coda (Purple) tra il 18% e il 35%+.
    """
    if not words:
        return {
            "top_10_pct": 0.0,
            "top_100_pct": 0.0,
            "top_1000_pct": 0.0,
            "tail_pct": 0.0,
            "saturation_pct": 0.0,
            "gltr_risk_score": 50.0
        }

    total = len(words)
    b1_count = 0
    b2_count = 0
    b3_count = 0
    b4_count = 0

    for w in words:
        b = get_word_bucket(w, lang)
        if b == 1:
            b1_count += 1
        elif b == 2:
            b2_count += 1
        elif b == 3:
            b3_count += 1
        else:
            b4_count += 1

    p1 = round((b1_count / total) * 100.0, 1)
    p2 = round((b2_count / total) * 100.0, 1)
    p3 = round((b3_count / total) * 100.0, 1)
    p4 = round((b4_count / total) * 100.0, 1)
    saturation = round(p1 + p2 + p3, 1)

    # Rischio GLTR calibrato:
    # Se la coda Purple (p4) < 10% e saturation > 90% -> Altissima probabilità AI
    # Se p4 >= 22% -> Zona Umana Tipica
    if p4 >= 24.0:
        gltr_risk = max(5.0, (28.0 - p4) * 2.5)
    elif p4 >= 15.0:
        gltr_risk = 20.0 + (24.0 - p4) * 3.0
    else:
        gltr_risk = min(100.0, 50.0 + (15.0 - p4) * 4.0)

    return {
        "top_10_pct": p1,
        "top_100_pct": p2,
        "top_1000_pct": p3,
        "tail_pct": p4,
        "saturation_pct": saturation,
        "gltr_risk_score": round(gltr_risk, 1)
    }

def calculate_sentence_zipf_surprisal(sentence: str, lang: str = "it") -> float:
    """
    Calcola l'entropia media della frase basata sul valore Zipf reale delle parole.
    Frasi composte solo da parole ad altissima frequenza ottengono sorpresa bassa (0-30).
    Frasi con lessico specialistico o combinazioni inattese ottengono sorpresa alta (50-85+).
    """
    words = re.findall(r"\b[a-zA-ZàèéìòùÀÈÉÌÒÙ0-9'-]+\b", sentence.lower())
    if not words:
        return 50.0

    surprisals = [(7.5 - get_word_zipf(w, lang)) for w in words]
    mean_surprisal = sum(surprisals) / len(words)
    
    # Normalizzazione in scala 0-100
    score = (mean_surprisal / 5.0) * 85.0
    return round(max(5.0, min(100.0, score)), 1)

def calculate_mtld(words: List[str], threshold: float = 0.72) -> float:
    """
    Calcola il Measure of Textual Lexical Diversity (MTLD, McCarthy & Jarvis 2010).
    A differenza del Type-Token Ratio (TTR) classico, MTLD è matematicamente
    robusto e non decade artificialmente all'aumentare della lunghezza del testo.
    Un MTLD > 80 indica ricchezza lessicale umana; un MTLD < 45 indica ripetitività robotica.
    """
    if len(words) < 15:
        return 50.0

    def _factor_count(seq: List[str]) -> float:
        factors = 0.0
        current_types = set()
        tokens = 0
        ttr = 1.0
        for w in seq:
            tokens += 1
            current_types.add(w)
            ttr = len(current_types) / tokens
            if ttr <= threshold:
                factors += 1.0
                current_types = set()
                tokens = 0
        if tokens > 0:
            partial_factor = (1.0 - ttr) / (1.0 - threshold) if ttr < 1.0 else 0.0
            factors += max(0.0, min(1.0, partial_factor))
        return len(seq) / max(0.001, factors)

    forward = _factor_count(words)
    backward = _factor_count(list(reversed(words)))
    return round((forward + backward) / 2.0, 1)
