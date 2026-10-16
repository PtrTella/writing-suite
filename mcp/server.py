#!/usr/bin/env python3
"""
Writing Suite - Unified MCP Server (Model Context Protocol stdio JSON-RPC 2.0)
Fornisce strumenti all'avanguardia a 4 pilastri:
1. evaluate_ai_risk (Causal Surprisal, Dynamic Stylometry, Embeddings, DeBERTa MPS)
2. audit_project (Scansione multi-file con audit a 4 pilastri e bibliografico)
3. audit_citations (Verifica deterministica chiavi BibTeX e claim non supportati)
4. check_commercial_detector (Verifica in tempo reale su CleverHumanizer.ai via Chromium)
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core.citations import audit_citations
from core.modern_evaluator import evaluate_document_modern, render_heatmap_cli
from core.external_detector import check_cleverhumanizer

SERVER_NAME = "writing-suite"
SERVER_VERSION = "2.0.0"

TOOLS = [
    {
        "name": "evaluate_ai_risk",
        "description": "Valuta il rischio e l'indice di sinteticità AI di un testo o file (.typ, .tex, .md) tramite il motore neurale e causale a 4 pilastri (SmolLM2 Surprisal MPS, Stylometria matematica Zipfiana, Embeddings densi, DeBERTa-v3). Restituisce punteggio globale, heatmap per paragrafo e frasi a bassa perplessità da riscrivere.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Il testo (o porzione di testo) da sottoporre ad audit diagnostico.",
                },
                "file_path": {
                    "type": "string",
                    "description": "Opzionale. Percorso del file originale (.typ, .tex, .md).",
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "audit_project",
        "description": "Esegue l'audit completo multi-file di un intero progetto o tesi (scansiona ricorsivamente .typ, .tex, .md), valuta ciascun file con il motore a 4 pilastri e incrocia le citazioni con references.bib. Restituisce tabella riassuntiva con hotspot e stato di ciascun capitolo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Percorso assoluto della directory del progetto o della tesi (es. /path/to/thesis_typst).",
                },
                "bib_path": {
                    "type": "string",
                    "description": "Opzionale. Percorso del file .bib. Se omesso, viene rilevato automaticamente nella directory.",
                },
            },
            "required": ["directory_path"],
        },
    },
    {
        "name": "audit_citations",
        "description": "Verifica il rigore citazionale e bibliografico: rileva asserzioni apodittiche prive di fonte ('gli studi dimostrano', 'research indicates') e convalida le chiavi citazionali (@chiave) rispetto a un file references.bib.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Il testo da analizzare (Typst, LaTeX o Markdown).",
                },
                "bib_path": {
                    "type": "string",
                    "description": "Opzionale. Percorso assoluto del file bibliografico (.bib).",
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "check_commercial_detector",
        "description": "Interroga in tempo reale il rilevatore commerciale CleverHumanizer.ai tramite Chromium locale headless, restituendo il verdetto reale esterno, il punteggio percentuale e i flag commerciali.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Il testo da sottoporre a verifica commerciale live.",
                }
            },
            "required": ["text"],
        },
    },
]


def audit_project_directory(directory_path: str, bib_path: Optional[str] = None) -> Dict[str, Any]:
    """Esegue l'audit multi-file moderno su una directory."""
    dp = Path(directory_path)
    if not dp.is_dir():
        return {"error": f"Directory non trovata: {directory_path}"}

    # Rilevamento automatico file .bib
    if not bib_path:
        bib_candidates = list(dp.glob("**/*.bib"))
        if bib_candidates:
            bib_path = str(bib_candidates[0])

    files = sorted(list(dp.glob("**/*.typ")) + list(dp.glob("**/*.tex")) + list(dp.glob("**/*.md")))
    files = [f for f in files if "node_modules" not in str(f) and ".git" not in str(f)]

    chapter_reports = []
    total_words = 0
    all_hotspots = []

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            rep = evaluate_document_modern(content, file_path=str(f))
            total_words += rep["total_words"]
            if rep["hotspots"]:
                all_hotspots.extend([{**h, "file": f.name} for h in rep["hotspots"]])
            chapter_reports.append({
                "file": f.name,
                "path": str(f),
                "words": rep["total_words"],
                "risk_score": rep["overall_ai_risk"],
                "perplexity": rep["avg_perplexity"],
                "burstiness": rep["avg_burstiness"],
                "cadence_sigma": rep["avg_cadence_sigma"],
                "hotspots_count": rep["hotspots_count"]
            })
        except Exception as e:
            chapter_reports.append({"file": f.name, "error": str(e)})

    # Audit citazionale globale se presente il bib
    cit_summary = None
    if bib_path and Path(bib_path).is_file():
        full_text = " ".join(f.read_text(encoding="utf-8", errors="ignore") for f in files if f.is_file())
        cit_summary = audit_citations(full_text, bib_path=bib_path)

    avg_project_risk = (
        sum(c["risk_score"] * c["words"] for c in chapter_reports if "risk_score" in c) / max(1, total_words)
        if total_words > 0 else 0.0
    )

    return {
        "directory": directory_path,
        "total_files": len(files),
        "total_words": total_words,
        "average_project_risk": round(avg_project_risk, 1),
        "chapters": chapter_reports,
        "total_hotspots": len(all_hotspots),
        "hotspots": all_hotspots[:10],
        "citations": cit_summary
    }


def execute_tool(name: str, arguments: dict) -> str:
    """Esegue il tool MCP e restituisce il risultato JSON."""
    text = arguments.get("text", "")
    if not text and "file_path" in arguments:
        fp = Path(arguments["file_path"])
        if fp.is_file():
            text = fp.read_text(encoding="utf-8", errors="ignore")

    if name == "evaluate_ai_risk":
        fp = arguments.get("file_path")
        res = evaluate_document_modern(text, file_path=fp)
        return json.dumps(res, indent=2, ensure_ascii=False)

    elif name == "audit_project":
        dp = arguments.get("directory_path", "")
        bib_p = arguments.get("bib_path")
        res = audit_project_directory(dp, bib_path=bib_p)
        return json.dumps(res, indent=2, ensure_ascii=False)

    elif name == "audit_citations":
        bib_p = arguments.get("bib_path")
        res = audit_citations(text, bib_path=bib_p)
        return json.dumps(res, indent=2, ensure_ascii=False)

    elif name == "check_commercial_detector":
        import asyncio
        res = asyncio.run(check_cleverhumanizer(text))
        return json.dumps(res, indent=2, ensure_ascii=False)

    return json.dumps({"error": f"Tool non supportato: {name}"}, indent=2)


def handle_json_rpc(line: str) -> None:
    """Gestione chiamate JSON-RPC 2.0 per il protocollo MCP."""
    try:
        req = json.loads(line)
    except json.JSONDecodeError:
        return

    msg_id = req.get("id")
    method = req.get("method")

    if method == "initialize":
        resp = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }
        print(json.dumps(resp), flush=True)

    elif method == "tools/list":
        resp = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS},
        }
        print(json.dumps(resp), flush=True)

    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            content_str = execute_tool(tool_name, arguments)
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": content_str}]},
            }
        except Exception as e:
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "isError": True,
                "result": {"content": [{"type": "text", "text": f"Errore interno: {str(e)}"}]},
            }
        print(json.dumps(resp), flush=True)


def main():
    """Entry point CLI / MCP stdio."""
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp":
        for line in sys.stdin:
            line = line.strip()
            if line:
                handle_json_rpc(line)
        return

    # Modalità CLI
    if len(sys.argv) < 2:
        print(f"Writing Suite v{SERVER_VERSION}")
        print("Uso: python server.py [--mcp | evaluate <file> | project <dir> | citations <file> [bib]]")
        return

    cmd = sys.argv[1]
    if cmd in ("evaluate", "audit"):
        target = sys.argv[2] if len(sys.argv) > 2 else "."
        if os.path.isfile(target):
            with open(target) as f:
                content = f.read()
            rep = evaluate_document_modern(content, file_path=target)
            print(render_heatmap_cli(rep))
        elif os.path.isdir(target):
            rep = audit_project_directory(target)
            print(json.dumps(rep, indent=2))
    elif cmd == "citations":
        target = sys.argv[2]
        bib = sys.argv[3] if len(sys.argv) > 3 else None
        with open(target) as f:
            content = f.read()
        res = audit_citations(content, bib_path=bib)
        print(json.dumps(res, indent=2))
    else:
        print(f"Comando non riconosciuto: {cmd}")


if __name__ == "__main__":
    main()
