"""
Writing Suite - Language Architecture & Extensible Registry
Fornisce:
1. BaseLanguagePack: Classe base astratta per supportare qualsiasi lingua naturale
2. ItalianLanguagePack: Configurazione completa per Italiano (CoLFIS / Subtlex-IT, sillabazione, Gulpease)
3. EnglishLanguagePack: Configurazione completa per Inglese (SUBTLEX-US / Brown, Flesch-Kincaid)
4. LanguageRegistry: Rilevamento automatico lingua $O(N)$ e dispatch dinamico
"""

import math
import re
from typing import Dict, List, Optional, Set

class BaseLanguagePack:
    """Interfaccia astratta per un Language Pack estendibile."""
    lang_code: str = "base"
    name: str = "Base Language"
    
    # Insiemi gerarchici di frequenza Zipf
    top_10: Set[str] = set()
    top_100: Set[str] = set()
    top_1000: Set[str] = set()
    top_3000: Set[str] = set()
    
    # Formule stereotipate a bassa entropia
    low_entropy_collocations: List[str] = []

    def count_syllables(self, word: str) -> int:
        raise NotImplementedError

    def calculate_readability(self, text: str, words: List[str], sentences: List[str]) -> Dict:
        raise NotImplementedError

    def get_word_bucket(self, word: str) -> int:
        """Restituisce il bucket GLTR: 1 (Top 10), 2 (Top 100), 3 (Top 1000), 4 (Top 3000), 5 (Tail)."""
        w = word.lower().strip()
        if w in self.top_10:
            return 1
        if w in self.top_100:
            return 2
        if w in self.top_1000:
            return 3
        if w in self.top_3000:
            return 4
        return 5

    def get_word_zipf(self, word: str) -> float:
        """Stima continua del valore Zipf del vocabolo."""
        b = self.get_word_bucket(word)
        if b == 1:
            return 7.0
        elif b == 2:
            return 5.8
        elif b == 3:
            return 4.6
        elif b == 4:
            return 3.6
        else:
            return 2.2

class ItalianLanguagePack(BaseLanguagePack):
    lang_code = "it"
    name = "Italiano"

    top_10 = {
        "il", "di", "e", "ed", "a", "ad", "la", "in", "che", "per", "un", "una", "sono", "del", "della",
        "dei", "degli", "dello", "delle"
    }

    top_100 = {
        "lo", "i", "gli", "le", "uno", "da", "dal", "dalla", "dallo", "dai", "dagli", "dalle",
        "su", "sul", "sulla", "sullo", "sui", "sugli", "sulle", "con", "tra", "fra",
        "al", "alla", "allo", "ai", "agli", "alle", "nel", "nella", "nello", "nei", "negli", "nelle",
        "o", "ma", "se", "non", "più", "molto", "tutto", "tutti", "tutta", "tutte",
        "ci", "vi", "si", "ne", "mi", "ti", "loro", "suo", "sua", "suoi", "sue",
        "nostro", "nostra", "nostri", "nostre", "questo", "questa", "questi", "queste",
        "quello", "quella", "quelli", "quelle", "come", "anche", "solo", "prima", "dopo",
        "mentre", "ogni", "alcuni", "alcune", "qualche", "quindi", "dunque", "invece",
        "così", "allora", "già", "mai", "sempre", "ancora", "oggi", "ora", "modo", "modi",
        "parte", "parti", "tempo", "tempi", "caso", "casi", "fatto", "fatti", "punto", "punti",
        "cosa", "cose", "bene", "male", "nuovo", "nuova", "nuovi", "nuove", "altro", "altra",
        "altri", "altre", "stesso", "stessa", "stessi", "stesse", "proprio", "propria", "propri",
        "proprie", "grande", "grandi", "piccolo", "piccoli", "primo", "prima", "primi", "prime",
        "ultimo", "ultima", "ultimi", "ultime", "è", "era", "erano", "stato", "stata", "stati",
        "state", "ha", "hanno", "aveva", "avevano", "può", "possono", "deve", "devono",
        "fare", "fa", "fanno", "dare", "viene", "vengono", "dove", "quando", "durante", "verso",
        "essere", "qualsiasi", "ciascuno", "ciascuna", "oppure", "appena", "frattempo"
    }

    top_1000 = {
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
        "evitare", "consentire", "rappresentare", "costituire", "includere", "mostrare", "spiegare",
        # Termini frequenti di workflow, software e architettura
        "download", "upload", "importazione", "produzione", "rilascio", "sviluppatore", "sviluppatori",
        "utente", "utenti", "operazioni", "calcolo", "costruzione", "architettura", "architetturale",
        "scarica", "scaricano", "esegue", "eseguono", "richiede", "richiedono", "invia", "inviano",
        "risponde", "rispondono", "attende", "attendono", "aggiorna", "aggiornano", "inserisce",
        "inseriscono", "controlla", "controllano", "consuma", "consumano", "mostrando", "utilizzando",
        "sposta", "spostano", "sprecare", "blocca", "bloccano", "mantenere", "aperta", "aperto",
        "legato", "legata", "isolato", "isolata", "temporale", "temporali", "immediata", "immediato",
        "immediatamente", "doppio", "doppia", "doppie", "doppi", "passaggio", "passaggi", "collo",
        "bottiglia", "polling", "worker", "task", "background", "manager", "coda", "code", "attesa",
        "attese", "timeout", "storico", "storica", "storici", "storiche", "minare", "mining",
        "coppia", "coppie", "basata", "basato", "basati", "basate", "cli", "json", "finalizzare",
        "seguente", "seguenti", "websocket", "websockets", "ideale", "generazione", "natura",
        "simultaneamente", "previene", "locale", "locali", "secondo", "secondi", "disaccoppiato",
        "disaccoppiata", "congestione", "job", "sincrono", "sincrona", "leggero", "leggera",
        "paga", "pagano", "iniziale", "iniziali", "intrinseco", "intrinseca", "deduplicazione",
        "firma", "firme", "tramite", "lunghi", "lungo", "lunga", "lunghe", "istantaneamente",
        "metadati", "invio", "inoltra", "inoltrano", "evidenziato", "evidenziata", "diventa",
        "diventano", "totalmente", "specialmente", "archiviazione", "espone", "espondono"
    }

    top_3000 = {
        "gestore", "gestori", "decisione", "decisioni", "riguardare", "riguarda", "riguardano",
        "albero", "alberi", "direttamente", "all'interno", "portare", "porta", "portano",
        "memorizzazione", "memorizzare", "persistente", "persistenti", "costoso", "costosa",
        "contenere", "contiene", "contengono", "contenenti", "singolo", "singola", "singoli", "singole",
        "comportare", "comporta", "comportano", "comporterebbe", "consumo", "milione", "milioni",
        "pubblicare", "pubblicazione", "pubblicazioni", "possedere", "possiede", "possiedono",
        "dozzina", "dozzine", "scalare", "scalerebbe", "centinaio", "centinaia", "dollaro", "dollari",
        "rendere", "rende", "rendono", "rendendo", "antieconomico", "inusabile", "ignorare", "ignorando",
        "linguaggio", "linguaggi", "progettare", "progettato", "progettati", "conoscenza", "conoscenze",
        "computazionale", "computazionali", "poiché", "autonomo", "autonoma", "autonomi", "autonome",
        "causare", "causa", "cause", "causerebbe", "crescita", "esponenziale", "danneggiare", "danneggia",
        "danneggiano", "aumentare", "aumenta", "aumentano", "aumentando", "enorme", "enormi", "enormemente",
        "requisito", "requisiti", "adottare", "adotta", "adottano", "adottando", "minimo", "minima",
        "minimi", "minime", "combaciare", "combaciano", "fiducia", "assoluto", "assoluta", "assoluti",
        "assolute", "potenziale", "potenziali", "rischio", "rischi", "identificare", "identificato",
        "identificata", "ospitare", "ospitato", "ospitata", "perdere", "perso", "persa", "rompere",
        "romperebbe", "risiedere", "risiede", "distinzione", "scolpire", "scolpito", "scolpiti", "scolpite",
        "generare", "genera", "generano", "generato", "generata", "esclusivo", "esclusiva", "esclusivamente",
        "ottimizzazione", "ottimizzazioni", "sparire", "compromettere", "compromesso", "compromessa",
        "preservare", "preservato", "preservata", "permanente", "permanenti", "permanentemente",
        "indicizzare", "indicizzato", "indicizzata", "ricostruire", "ricostruisce", "identico", "identica",
        "identici", "identiche", "resiliente", "resilienti", "conferma", "conferme", "coda", "code",
        "attesa", "ritardo", "ritardi", "connessione", "connessioni", "canale", "canali", "barra",
        "caricamento", "terminare", "termina", "passare", "passa", "onere", "pesante", "reattiva",
        "odierno", "odierna", "odierni", "odierne", "garantendo", "delegando", "permettendo",
        "consentendo", "facilitando", "assicurando", "evitando", "riducendo", "aumentando", "eliminando"
    }

    low_entropy_collocations = [
        r"in un gestore di pacchetti",
        r"un approccio ingenuo (?:suggerirebbe|potrebbe)",
        r"pura follia architetturale",
        r"per tre ragioni fondamentali",
        r"design pattern aureo",
        r"la risposta (?:risiede|è|si trova)",
        r"funge (?:esclusivamente |meramente )?da (?:indice|cache|archivio|volano|ponte)",
        r"garantendo (?:un[a']?|il|la|i|le|l'|alla|al)",
        r"delegando al (?:client|server|sistema)",
        r"evitando di (?:sprecare|duplicare|compromettere)",
        r"non (?:solo|soltanto) [^,]+,? ma (?:anche|bensì)",
        r"è fondamentale (?:sottolineare|evidenziare|ricordare)",
        r"gioca un ruolo (?:cruciale|fondamentale|chiave)",
        r"nel (?:panorama attuale|contesto odierno)",
        r"si configura come",
        r"apre la strada a"
    ]

    def count_syllables(self, word: str) -> int:
        w = word.lower()
        vowels = re.findall(r"[aeiouàèéìòù]", w)
        return max(1, len(vowels))

    def calculate_readability(self, text: str, words: List[str], sentences: List[str]) -> Dict:
        """Indice Gulpease (standard accademico italiano, Lucisano & Piemontese 1988)."""
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        tot_chars = sum(len(w) for w in words)
        short_words = sum(1 for w in words if len(w) <= 4)

        # Formula Gulpease: 89 + (300 * n_frasi - 10 * short_words) / n_parole (variante su caratteri)
        # Standard: 89 + (300 * frasi - 10 * lettere) / parole
        gulpease = 89.0 + ((300.0 * tot_sents) - (10.0 * tot_chars)) / float(tot_words)
        gulpease_score = round(max(0.0, min(100.0, gulpease)), 1)

        if gulpease_score >= 80:
            interp = "Facile (Licenza Elementare)"
        elif gulpease_score >= 60:
            interp = "Medio-Facile (Licenza Media)"
        elif gulpease_score >= 40:
            interp = "Medio-Complesso (Diploma Superiore)"
        else:
            interp = "Difficile (Livello Accademico / Universitario)"

        return {
            "language": "it",
            "index_name": "Gulpease",
            "score": gulpease_score,
            "interpretation": interp,
            "avg_sentence_length": round(tot_words / tot_sents, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents
        }

class EnglishLanguagePack(BaseLanguagePack):
    lang_code = "en"
    name = "English"

    top_10 = {
        "the", "of", "and", "to", "a", "in", "that", "is", "was", "he", "for", "it", "with", "as"
    }

    top_100 = {
        "his", "on", "be", "at", "by", "i", "this", "had", "not", "are", "but", "from",
        "or", "have", "an", "they", "which", "one", "you", "were", "her", "all", "she",
        "there", "would", "their", "we", "him", "been", "has", "when", "who", "will",
        "more", "no", "if", "out", "so", "said", "what", "up", "its", "about", "into",
        "than", "them", "can", "only", "other", "new", "some", "could", "time", "these",
        "two", "may", "then", "do", "first", "any", "my", "now", "such", "like", "our",
        "over", "man", "me", "even", "most", "made", "after", "also", "did", "many",
        "before", "must", "through", "back", "years", "where", "much", "your", "way",
        "well", "down", "should", "because", "each", "just", "those", "people", "how"
    }

    top_1000 = {
        "work", "life", "day", "year", "part", "number", "great", "tell", "men", "say", "small",
        "every", "found", "still", "between", "name", "should", "home", "big", "give", "air",
        "line", "set", "own", "under", "read", "last", "never", "us", "left", "end", "along",
        "while", "might", "next", "sound", "below", "saw", "something", "thought", "both", "few",
        "those", "always", "show", "large", "often", "together", "asked", "house", "don't", "world",
        "going", "want", "school", "important", "until", "form", "food", "keep", "children", "feet",
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

    top_3000 = {
        "assessment", "framework", "taxonomy", "taxonomies", "mapping", "qualitative", "quantitative",
        "formal", "static", "guarantee", "absence", "vulnerability", "vulnerabilities", "projection",
        "projections", "profiling", "blockchain", "blockchains", "routing", "computational", "distribution",
        "distributions", "conducted", "locally", "utilizing", "simulation", "threat", "mitigation",
        "accuracy", "third-party", "structural", "resilience", "known", "vector", "vectors", "defense",
        "defenses", "observed", "ecosystem", "ecosystems", "tampering", "transport", "compromised",
        "malicious", "installed", "namespace", "reuse", "deletion", "re-register", "ledger", "un-linked",
        "breached", "backdoored", "artifact", "artifacts", "decoupling", "anchor", "anchors", "forge",
        "squatting", "claim", "staking", "collateral", "curation", "partition", "degradation", "intrinsic",
        "root", "trust", "paramount", "subjected", "reentrancy", "overflow", "underflow", "malleability",
        "mutability", "warning", "warnings", "informational", "enforcement", "negligible", "inviable",
        "dedicated", "thereby", "ensuring", "enabling", "allowing", "yielding", "rendering"
    }

    low_entropy_collocations = [
        r"in today\x27s (?:rapidly evolving )?(?:digital |modern )?(?:landscape|world|society|era)",
        r"plays? a (?:pivotal|crucial|vital|key) role",
        r"stands? as a testament",
        r"underscor(?:ing|es|ed) the (?:importance|significance)",
        r"not (?:merely|only) [^,]+,? but (?:rather|also)",
        r"delv(?:e|ing|es) into",
        r"seamlessly (?:integrate|embrac|navigat|blend)",
        r"(?:holistic|paradigm) shift",
        r"in conclusion",
        r"it is (?:crucial|essential|imperative|important) to",
        r"a (?:naive|tempting) approach would",
        r"the answer (?:lies in|is)",
        r"immutable root of trust",
        r"cost of trust",
        r"acts as (?:an?|the)",
        r"thereby (?:ensuring|enabling|reducing)",
        r"for three (?:fundamental|key|primary) reasons",
        r"four critical dimensions"
    ]

    def count_syllables(self, word: str) -> int:
        w = word.lower()
        if len(w) <= 3:
            return 1
        w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
        w = re.sub(r"^y", "", w)
        vowels = re.findall(r"[aeiouy]{1,2}", w)
        return max(1, len(vowels))

    def calculate_readability(self, text: str, words: List[str], sentences: List[str]) -> Dict:
        """Flesch Reading Ease & Flesch-Kincaid Grade Level (Kincaid et al. 1975)."""
        tot_words = max(1, len(words))
        tot_sents = max(1, len(sentences))
        tot_sylls = sum(self.count_syllables(w) for w in words)

        # Flesch Reading Ease = 206.835 - (1.015 * ASL) - (84.6 * ASW)
        asl = tot_words / tot_sents
        asw = tot_sylls / tot_words
        flesch = 206.835 - (1.015 * asl) - (84.6 * asw)
        flesch_score = round(max(0.0, min(100.0, flesch)), 1)

        # FK Grade Level = (0.39 * ASL) + (11.8 * ASW) - 15.59
        fk_grade = round(max(1.0, (0.39 * asl) + (11.8 * asw) - 15.59), 1)

        if flesch_score >= 70:
            interp = "Fairly Easy / Plain English"
        elif flesch_score >= 50:
            interp = "Standard / High School"
        elif flesch_score >= 30:
            interp = "Difficult / College Level"
        else:
            interp = "Very Difficult / Academic & Technical Research"

        return {
            "language": "en",
            "index_name": "Flesch Reading Ease",
            "score": flesch_score,
            "grade_level": fk_grade,
            "interpretation": interp,
            "avg_sentence_length": round(asl, 1),
            "words_count": tot_words,
            "sentences_count": tot_sents
        }

class LanguageRegistry:
    """Registry centrale per la gestione e il rilevamento automatico delle lingue."""
    _packs: Dict[str, BaseLanguagePack] = {
        "it": ItalianLanguagePack(),
        "en": EnglishLanguagePack()
    }

    @classmethod
    def register(cls, pack: BaseLanguagePack) -> None:
        cls._packs[pack.lang_code] = pack

    @classmethod
    def get(cls, lang_code: str) -> BaseLanguagePack:
        return cls._packs.get(lang_code, cls._packs["en"])

    @classmethod
    def detect_language(cls, words: List[str]) -> BaseLanguagePack:
        """Rileva automaticamente la lingua del testo basandosi sul profilo lessicale in $O(N)$."""
        if not words:
            return cls._packs["it"]
        it_matches = sum(1 for w in words if w.lower() in cls._packs["it"].top_10 or w.lower() in cls._packs["it"].top_100)
        en_matches = sum(1 for w in words if w.lower() in cls._packs["en"].top_10 or w.lower() in cls._packs["en"].top_100)
        return cls._packs["it"] if it_matches >= en_matches else cls._packs["en"]
