"""
Writing Suite - Cleaner Module
Fornisce parsing e sanitizzazione avanzata di testi tecnici, accademici e formattati (Typst, LaTeX, Markdown, HTML).
Isola la sola prosa naturale per garantire analisi stilometriche e probabilistiche accurate senza falsi positivi.
"""

import re

def clean_markup(text: str) -> str:
    """Rimuove elementi tecnici, tabelle, LaTeX, Typst markup e blocchi codice per isolare la sola prosa."""
    # 1. Blocchi di codice raw
    text = re.sub(r"````[\s\S]*?````", "", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`\n]+`", "", text)

    # 2. Commenti di codice (Typst // e /* */, LaTeX %)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    text = re.sub(r"(?m)^%.*$", "", text)

    # 3. Costrutti Typst (figure, table, image, macro di layout e comandi)
    text = re.sub(r"#figure\([\s\S]*?\)(?:\s*<[^>]+>)?", "", text)
    text = re.sub(r"#table\([\s\S]*?\)", "", text)
    text = re.sub(r"#image\([\s\S]*?\)", "", text)
    text = re.sub(r"#(?:set|show|let|align|v|h|line|page|rect|block|grid|include|import)\b[^\n;]*", "", text)
    text = re.sub(r"#text\([^)]*\)\[([^\]]*)\]", r"\1", text)

    # 4. Equazioni LaTeX e Typst math ($...$ e $$...$$)
    text = re.sub(r"\$\$[\s\S]*?\$\$", "", text)
    text = re.sub(r"\\begin\{[a-zA-Z*]+\}[\s\S]*?\\end\{[a-zA-Z*]+\}", "", text)
    text = re.sub(r"\$[^$\n]+\$", "", text)

    # 5. Tabelle Markdown
    text = re.sub(r"\|[^\n]+\|", "", text)

    # 6. Citazioni ed etichette (Typst @citazione, <label>, LaTeX \cite, Pandoc [@])
    text = re.sub(r"@[a-zA-Z0-9_:.-]+", "", text)
    text = re.sub(r"<[a-zA-Z0-9_:.-]+>", "", text)
    text = re.sub(r"\\cite[a-z]*\{[^}]+\}", "", text)
    text = re.sub(r"\[@[^\]]+\]", "", text)

    # 7. Intestazioni e frontmatter
    text = re.sub(r"^---[\s\S]*?---", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[=#]+\s+[^\n]+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    
    # 8. Normalizzazione spaziature
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_sentences(text: str) -> list[str]:
    """Segmentazione avanzata delle frasi con protezione abbreviazioni comuni (IT/EN/Academic)."""
    clean_text = clean_markup(text)
    protected = re.sub(
        r"(?i)\b(et al|es|ad es|dott|prof|ing|avv|fig|tab|vol|pag|cap|art|vs|i\.e|e\.g|etc|ecc|approx|cf)\.",
        r"\1<PROTECTED_DOT>",
        clean_text
    )
    raw_splits = re.split(r"(?<=[.!?])\s+", protected)
    sentences = []
    for s in raw_splits:
        clean_s = s.replace("<PROTECTED_DOT>", ".").strip()
        # Considera frasi con almeno 2 parole e non meri residui di codice o elenchi
        if clean_s and not clean_s.startswith("#") and len(clean_s.split()) >= 2:
            sentences.append(clean_s)
    return sentences

def extract_words(text: str) -> list[str]:
    """Estrae parole normalizzate per il calcolo lessicale e frequenziale."""
    clean_text = clean_markup(text)
    # Normalizza elisioni clitiche italiane (l'utente -> lo utente / l' utente)
    normalized = re.sub(r"\b([ldnsmtc]|dell|all|dall|sull|nell|un)'", r"\1 ", clean_text, flags=re.IGNORECASE)
    raw_words = re.findall(r"\b[a-zA-ZàèéìòùÀÈÉÌÒÙ-]+\b", normalized.lower())
    return [w for w in raw_words if any(c.isalpha() for c in w) and len(w) >= 2]
