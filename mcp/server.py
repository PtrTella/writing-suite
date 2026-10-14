#!/usr/bin/env python3
"""
Writing Suite - Unified MCP Server & CLI Engine
Fornisce servizi deterministici per l'analisi stilometrica, la diagnosi AI e il rigore accademico.
Compatibile con lo standard Model Context Protocol (MCP stdio JSON-RPC 2.0).
Zero dipendenze esterne: funziona nativamente con Python 3.9+ su macOS, Linux e Windows.
"""

import argparse
import json
import sys
from pathlib import Path

# Aggiunge la directory corrente al path di importazione
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from core.citations import audit_citations
from core.evaluator_engine import evaluate_document
from core.linter import lint_text
from core.metrics import calculate_readability
from core.project_auditor import audit_directory

SERVER_NAME = "writing-suite"
SERVER_VERSION = "1.0.0"

# ==============================================================================
# TOOL SCHEMAS & DEFINITIONS
# ==============================================================================

TOOLS = [
    {
        "name": "evaluate_ai_risk",
        "description": "Valuta il rischio e l'indice di sinteticità AI di un testo combinando 4 lenti autonome: GPTZero emulato (PPL & Burstiness), Linter euristico (50+ pattern Clever/Copyleaks), Stilometria accademica (Yule K, Hapax) e Anti-Bypass check. Restituisce referto completo con heatmap frase-per-frase.",
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
                "domain": {
                    "type": "string",
                    "description": "Opzionale. Dominio del testo (es. 'cryptography', 'biomedical', 'legal', 'general').",
                },
                "domain_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Opzionale. Lista oggettiva di 5-15 termini tecnici o acronimi del dominio estratti dall'agente (es. ['Sepolia', 'zk-SNARKs', 'rollup']). Vengono esclusi dal tail statistico come terminologia attesa.",
                },
                "target_style": {
                    "type": "string",
                    "enum": [
                        "academic_thesis",
                        "technical_documentation",
                        "essay",
                        "conversational",
                    ],
                    "description": "Opzionale. Profilo di stile atteso: 'academic_thesis' (default, σ0=10.5), 'technical_documentation' (σ0=8.0), 'essay' (σ0=11.5), 'conversational' (σ0=9.0).",
                },
                "language": {
                    "type": "string",
                    "description": "Opzionale. Lingua del testo ('it', 'en'). Se omesso, viene rilevata automaticamente in O(N).",
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "audit_project",
        "description": "Esegue l'audit completo multi-file di un intero progetto o tesi (scansiona ricorsivamente .typ, .tex, .md), calcola PPL, burstiness, linter, leggibilità Flesch/Gulpease e incrocia le citazioni con il file references.bib. Restituisce tabella riassuntiva e quadro complessivo.",
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
                "language": {
                    "type": "string",
                    "description": "Lingua di analisi per la leggibilità: 'en' o 'it'. Default: 'en'.",
                    "enum": ["en", "it"],
                },
            },
            "required": ["directory_path"],
        },
    },
    {
        "name": "calculate_readability",
        "description": "Calcola gli indici di leggibilità e cadenza ritmica: Indice Gulpease (Italiano), Flesch-Kincaid (Inglese), Varianza lunghezza frasi (Burstiness) e Dispersione sillabica (stile Copyleaks).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Il testo da analizzare."},
                "language": {
                    "type": "string",
                    "description": "Lingua di analisi: 'it' (Italiano) o 'en' (Inglese). Default: 'it'.",
                    "enum": ["it", "en"],
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "lint_writing",
        "description": "Scansiona il testo identificando i 50+ tic, formule e cliché statistici tipici dei modelli generativi (CleverHumanizer signals, Wikipedia AI tells, transizioni artificiali, riders participiali).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Il testo da scansionare."}
            },
            "required": ["text"],
        },
    },
    {
        "name": "audit_citations",
        "description": "Verifica il rigore citazionale e bibliografico: rileva asserzioni fattuali non dimostrate privi di fonte ('gli studi dimostrano', 'research indicates') e convalida le chiavi citazionali rispetto a un file .bib.",
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
]

# ==============================================================================
# TOOL DISPATCHER
# ==============================================================================


def execute_tool(name: str, arguments: dict) -> str:
    """Esegue il tool specificato e restituisce il risultato formattato in formato testuale/JSON."""
    text = arguments.get("text", "")
    if not text and "file_path" in arguments:
        fp = Path(arguments["file_path"])
        if fp.is_file():
            text = fp.read_text(encoding="utf-8", errors="ignore")

    if name == "evaluate_ai_risk":
        fp = arguments.get("file_path")
        domain = arguments.get("domain")
        domain_terms = arguments.get("domain_terms")
        target_style = arguments.get("target_style", "academic_thesis")
        lang = arguments.get("language")
        res = evaluate_document(
            text,
            file_path=fp,
            domain=domain,
            domain_terms=domain_terms,
            target_style=target_style,
            language=lang,
        )
        return json.dumps(res, indent=2, ensure_ascii=False)

    elif name == "audit_project":
        dp = arguments.get("directory_path", "")
        bib_p = arguments.get("bib_path")
        lang = arguments.get("language", "en")
        res = audit_directory(dp, bib_path=bib_p, lang=lang)
        return json.dumps(res, indent=2, ensure_ascii=False)

    elif name == "calculate_readability":
        lang = arguments.get("language", "it")
        res = calculate_readability(text, lang=lang)
        return json.dumps(res, indent=2, ensure_ascii=False)

    elif name == "lint_writing":
        findings = lint_text(text)
        return json.dumps(
            {"total_findings": len(findings), "findings": findings},
            indent=2,
            ensure_ascii=False,
        )

    elif name == "audit_citations":
        bib_p = arguments.get("bib_path")
        res = audit_citations(text, bib_path=bib_p)
        return json.dumps(res, indent=2, ensure_ascii=False)

    else:
        raise ValueError(f"Tool sconosciuto: {name}")


# ==============================================================================
# MCP STDIO JSON-RPC 2.0 PROTOCOL LOOP
# ==============================================================================


def run_mcp_server():
    """Ascolta ed evade richieste JSON-RPC 2.0 su stdin/stdout secondo lo standard MCP."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    },
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                # Notifica client di avvenuta inizializzazione, nessuna risposta richiesta
                pass

            elif method == "tools/list":
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                try:
                    result_text = execute_tool(tool_name, tool_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"content": [{"type": "text", "text": result_text}]},
                    }
                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Errore durante l'esecuzione del tool {tool_name}: {str(e)}",
                                }
                            ],
                            "isError": True,
                        },
                    }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "ping":
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            else:
                if req_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Metodo non supportato: {method}",
                        },
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

        except Exception as err:
            err_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Errore interno del server: {str(err)}",
                },
            }
            sys.stdout.write(json.dumps(err_response) + "\n")
            sys.stdout.flush()


# ==============================================================================
# CLI ENTRYPOINT
# ==============================================================================


def main():
    parser = argparse.ArgumentParser(description="Writing Suite Engine & MCP Server")
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Avvia il server in modalità MCP stdio JSON-RPC",
    )
    parser.add_argument(
        "--audit",
        type=str,
        help="Esegue l'audit completo di un progetto o directory (.typ, .tex, .md)",
    )
    parser.add_argument(
        "--evaluate", type=str, help="Valuta rischio AI di un file, directory o stringa"
    )
    parser.add_argument(
        "--readability", type=str, help="Calcola leggibilità (Gulpease/Flesch)"
    )
    parser.add_argument("--lint", type=str, help="Scansiona cliché e pattern bot")
    parser.add_argument("--citations", type=str, help="Verifica salute citazioni")
    parser.add_argument(
        "--bib", type=str, default=None, help="File .bib associato per verifica chiavi"
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Dominio del testo (es. cryptography, biomedical, legal)",
    )
    parser.add_argument(
        "--terms",
        type=str,
        default=None,
        help="Termini di dominio separati da virgola (es. 'Sepolia,zk-SNARKs,rollup')",
    )
    parser.add_argument(
        "--style",
        type=str,
        default="academic_thesis",
        help="Profilo stilistico: academic_thesis, technical_documentation, essay, conversational",
    )
    parser.add_argument("--lang", type=str, default="en", help="Lingua ('it' o 'en')")
    parser.add_argument(
        "--json", action="store_true", help="Restituisce output in formato JSON grezzo"
    )

    args = parser.parse_args()

    if args.mcp or (len(sys.argv) == 1 and not sys.stdin.isatty()):
        run_mcp_server()
        return

    # Modalità CLI
    target_audit = args.audit or (
        args.evaluate and Path(args.evaluate).is_dir() and args.evaluate
    )
    if target_audit:
        res = audit_directory(target_audit, bib_path=args.bib, lang=args.lang)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 88)
            print("  📊 WRITING SUITE: PROJECT & CORPUS AUDIT REPORT")
            print("=" * 88)
            print(res["summary_table"])
            print("-" * 88)
            print(
                f"TOTAL WORDS: {res['total_words']} | TOTAL SENTENCES: {res['total_sentences']}"
            )
            print(
                f"CORPUS AI RISK: {res['corpus_badge']} {res['corpus_ai_score']}% ({res['corpus_verdict']})"
            )
            print(f"CORPUS MEAN PPL: {res['corpus_mean_ppl']} / 100")
            print("=" * 88)

            lints = res["detailed_findings"]["lints"]
            missing_bib = res["detailed_findings"]["missing_bib"]
            unsupported = res["detailed_findings"]["unsupported_claims"]

            if lints:
                print("\n🔍 DETAILED LINT FINDINGS:")
                for rel_p, findings in lints.items():
                    print(f"\n  [{rel_p}] ({len(findings)} findings):")
                    for find in findings:
                        print(
                            f"    Line {find.get('line', '?')}: [{find.get('category')}] {find.get('name')}: '{find.get('matched_text')}'"
                        )

            if missing_bib:
                print("\n⚠️ CITATIONS MISSING IN BIB:")
                for rel_p, keys in missing_bib.items():
                    print(f"  [{rel_p}]: {', '.join(keys)}")

            if unsupported:
                print("\n⚠️ UNSUPPORTED CLAIMS ([citation needed]):")
                for rel_p, claims in unsupported.items():
                    print(f"\n  [{rel_p}] ({len(claims)} claims):")
                    for cl in claims:
                        print(
                            f"    Line {cl.get('line', '?')}: '{cl.get('matched_text')}'"
                        )

    elif args.evaluate:
        p = Path(args.evaluate)
        text = (
            p.read_text(encoding="utf-8", errors="ignore")
            if p.is_file()
            else args.evaluate
        )
        domain_terms_list = (
            [t.strip() for t in args.terms.split(",")] if args.terms else None
        )
        res = evaluate_document(
            text,
            file_path=str(p) if p.is_file() else None,
            domain=args.domain,
            domain_terms=domain_terms_list,
            target_style=args.style,
            language=args.lang,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.readability:
        p = Path(args.readability)
        text = (
            p.read_text(encoding="utf-8", errors="ignore")
            if p.is_file()
            else args.readability
        )
        res = calculate_readability(text, lang=args.lang)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.lint:
        p = Path(args.lint)
        text = (
            p.read_text(encoding="utf-8", errors="ignore") if p.is_file() else args.lint
        )
        res = lint_text(text)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.citations:
        p = Path(args.citations)
        text = (
            p.read_text(encoding="utf-8", errors="ignore")
            if p.is_file()
            else args.citations
        )
        res = audit_citations(text, bib_path=args.bib)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
