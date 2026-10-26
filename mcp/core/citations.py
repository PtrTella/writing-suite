"""
Writing Suite - Citations Module
Verifica lo stato di salute e il rigore citazionale di tesi, paper e report tecnici.
1. Identifica affermazioni fattuali non dimostrate ("gli studi dimostrano", "research indicates", "secondo recenti ricerche") prive di fonte immediata.
2. Estrae chiavi citazionali Typst (@chiave), LaTeX (\\cite{chiave}) e Markdown ([@chiave]).
3. Se fornito un file .bib, verifica la presenza delle chiavi bibliografiche e segnala broken references.
"""

import re
from pathlib import Path

UNSUPPORTED_PATTERNS = [
    {
        "name": "Affermazione generica su studi/ricerche",
        "regex": r"(?i)\b(?:recent studies (?:have shown|indicate|suggest)|research (?:proves|shows|indicates)|numerous studies|gli studi dimostrano(?: che)?|le ricerche indicano(?: che)?|secondo recenti (?:indagini|ricerche|studi)|diversi studi hanno evidenziato)\b(?![^.!?\n]*?(?:@|\\cite|\[\s*@|\(\s*(?:19|20)\d{2}\)))",
        "message": "Affermazione di ricerca non supportata da citazione immediata (richiede [@ref] o \\cite)."
    },
    {
        "name": "Autorità indefinita o esperti anonimi",
        "regex": r"(?i)\b(?:experts (?:agree|argue|believe)|scientists have discovered|gli esperti ritengono(?: che)?|gli scienziati concordano|la comunità scientifica afferma)\b(?![^.!?\n]*?(?:@|\\cite|\[\s*@|\(\s*(?:19|20)\d{2}\)))",
        "message": "Ricorso ad autorità anonima senza riferimento bibliografico puntuale."
    },
    {
        "name": "Statistiche o percentuali non tracciate",
        "regex": r"(?i)\b(?:oltre il \d+%\s+dei|more than \d+%\s+of the)\b(?![^.!?\n]*?(?:@|\\cite|\[\s*@|\(\s*(?:19|20)\d{2}\)))",
        "message": "Dato statistico o percentuale citato senza indicazione della fonte sperimentale."
    }
]

def extract_citation_keys(text: str) -> set[str]:
    """Estrae tutte le chiavi citazionali presenti nel documento."""
    keys = set()
    typst_raw = re.findall(r"@([a-zA-Z0-9_:.-]+)", text)
    for k in typst_raw:
        clean_k = k.rstrip(".,;:-")
        # Escludi etichette di figure, tabelle, capitoli o sezioni (<ch-...>, <fig:...>, <sec:...>, etc.) e percorsi scoped (@openzeppelin/...)
        if not re.match(r"^(?:ch|fig|sec|tbl|tab|table|eq|listing|app)[-_:]", clean_k, re.I) and not clean_k.startswith("openzeppelin"):
            keys.add(clean_k)

    latex_matches = re.findall(r"\\cite[a-z]*\{([^}]+)\}", text)
    for m in latex_matches:
        for k in m.split(","):
            clean_k = k.strip().rstrip(".,;:-")
            if clean_k:
                keys.add(clean_k)

    pandoc_keys = re.findall(r"\[@([a-zA-Z0-9_:.-]+)\]", text)
    for k in pandoc_keys:
        clean_k = k.strip().rstrip(".,;:-")
        if clean_k:
            keys.add(clean_k)
    return keys

def parse_bib_keys(bib_path: str) -> set[str]:
    """Estrae le chiavi definite in un file .bib (es. @article{key, ...})."""
    p = Path(bib_path)
    if not p.is_file():
        return set()
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
        return set(re.findall(r"@\w+\s*\{\s*([a-zA-Z0-9_:.-]+)\s*,", content))
    except Exception:
        return set()

def audit_citations(text: str, bib_path: str = None) -> dict:
    """Esegue l'audit completo delle citazioni e del rigore scientifico."""
    findings = []
    lines = text.split("\n")
    for line_idx, line in enumerate(lines, 1):
        for pat in UNSUPPORTED_PATTERNS:
            if re.search(pat["regex"], line):
                findings.append({
                    "line": line_idx,
                    "type": pat["name"],
                    "matched_text": line.strip()[:100],
                    "message": pat["message"]
                })

    used_keys = extract_citation_keys(text)
    missing_in_bib = []
    bib_defined_keys = set()

    if bib_path:
        bib_defined_keys = parse_bib_keys(bib_path)
        if bib_defined_keys:
            for k in used_keys:
                if k not in bib_defined_keys:
                    missing_in_bib.append(k)

    return {
        "unsupported_claims_count": len(findings),
        "unsupported_claims": findings,
        "total_citations_found": len(used_keys),
        "citation_keys": sorted(list(used_keys)),
        "bib_path_provided": bool(bib_path),
        "missing_in_bib": sorted(missing_in_bib),
        "bib_total_entries": len(bib_defined_keys)
    }
