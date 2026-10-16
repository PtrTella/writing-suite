#!/usr/bin/env python3
"""
Writing Suite - Full Thesis Audit & Live Cross-Validation
Audita tutti i capitoli della tesi PyChain (ch1 - ch8) con le 7 lenti locali
ed esegue cross-validazione live su CleverHumanizer.ai per sezioni chiave.
"""

import sys
import json
import asyncio
from pathlib import Path

# Setup path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "mcp"))

from core.evaluator_engine import evaluate_document
from core.external_detector import check_cleverhumanizer
from core.cleaner import clean_markup, extract_sentences

def run_local_audit():
    chapters_dir = Path("/Users/tella/Workspace/PyChain/thesis_typst/chapters")
    chapter_files = sorted([f for f in chapters_dir.glob("ch*.typ")])

    print("=" * 110)
    print("AUDIT FORENSE COMPLETO TESI PYCHAIN (CAPITOLI CH1 - CH8)")
    print("Motore Locale: DeBERTa Hierarchical + 7 Lenti Calibrate (Copyleaks/CleverHumanizer Standard)")
    print("=" * 110)
    print(f"{'Capitolo':<24} | {'Parole':<6} | {'Overall AI':<11} | {'Neural':<8} | {'Linter':<8} | {'Cadence':<8} | {'GLTR':<6} | {'Findings'}")
    print("-" * 110)

    results = []
    for f in chapter_files:
        text = f.read_text(encoding="utf-8")
        res = evaluate_document(text, target_style="academic_thesis")
        
        words_count = res["stats"]["total_words"]
        overall = res["overall_ai_score"]
        badge = res["verdict_badge"]
        neural = res["lenses"]["neural_transformer"]["risk_score"]
        linter = res["lenses"]["heuristic_linter"]["risk_score"]
        cadence = res["lenses"]["cadence"]["risk_score"]
        gltr = res["lenses"]["gltr_forensics"]["risk_score"]
        findings = res["lenses"]["heuristic_linter"]["findings"]

        results.append({
            "file": f.name,
            "path": str(f),
            "words": words_count,
            "overall": overall,
            "badge": badge,
            "verdict": res["verdict"],
            "neural": neural,
            "linter": linter,
            "cadence": cadence,
            "gltr": gltr,
            "findings_count": len(findings),
            "findings": findings,
            "raw_text": text
        })

        print(f"{f.name:<24} | {words_count:>6} | {overall:>5.1f}% {badge} | {neural:>6.1f}% | {linter:>6.1f}% | {cadence:>6.1f}% | {gltr:>4.1f}% | {len(findings):>8}")

    print("=" * 110)
    return results

async def run_live_samples(local_results):
    print("\n" + "=" * 110)
    print("CROSS-VALIDAZIONE LIVE SU CLEVERHUMANIZER.AI (SEZIONI CHIAVE)")
    print("=" * 110)

    # Campioniamo una sezione rappresentativa di ~100-200 parole per capitoli chiave (>80 parole per CleverHumanizer)
    live_targets = [
        ("ch1_intro.typ", "Ch1 Sec 1.0 (Motivation & Zero-Trust)", 
         "Public package repositories, including the Python Package Index (PyPI) and npm, stream untrusted third-party code straight onto developer workstations, cloud clusters, and continuous integration pipelines. Because Python serves as the foundational substrate for modern Artificial Intelligence and Machine Learning engineering (powering frameworks such as PyTorch, TensorFlow, Hugging Face Transformers, and distributed inference engines), the software supply chain has become a primary target for sophisticated adversaries. In traditional workflows, running a single pip install command unpacks pre-compiled binary wheels or executes arbitrary build scripts from source distributions with ambient user privileges. This operational design creates a structural vulnerability: application trust is entirely transitive, forcing production systems to inherit the operational habits, vulnerability lifecycles, and maintainer security postures of every direct and transitive library across their software bill of materials. In high-consequence deployments, an uninspected upstream library compromise can silently facilitate training data exfiltration, latent model weight tampering, or adversarial backdoor injection into downstream neural models without triggering network perimeter alarms."),
        
        ("ch2_background.typ", "Ch2 Sec 2.0 (Decentralized Trade-offs)",
         "No individual decentralized network satisfies the throughput, consensus, and archival requirements of software distribution simultaneously. Three distinct technical properties must hold at once for secure software distribution: registries must enforce global consensus on namespace ownership, swarms must transfer large file archives without centralized bandwidth choking, and archives must preserve source trees permanently across decades. Forcing all three duties onto a single protocol produces fatal engineering compromises. Blockchains that attempt to host multi-megabyte package archives suffer immediate state bloat and prohibitive gas costs, whereas pure peer-to-peer storage networks lack the deterministic consensus needed to sequence package versions or prevent namespace squatting. PyChain reconciles these competing requirements by federating three complementary technologies: the Ethereum Virtual Machine provides immutable state transitions and maintainer governance, the InterPlanetary File System (IPFS) delivers content-addressed peer-to-peer storage, and Software Heritage provides packaging-invariant source preservation."),
        
        ("ch4_threat_model.typ", "Ch4 Sec 4.0 (Perimeter Model Collapse)",
         "Traditional software security architectures rely on perimeter defense models where authenticated access to a central server establishes an implicit umbrella of trust across all downstream participants. In centralized package registries like PyPI or npm, developers and automated compilation pipelines treat the central repository as an unquestioned trust root. When administrative credentials leak, repository domain registrations lapse, or internal cloud infrastructure suffers compromise, this implicit trust model collapses, exposing millions of downstream systems to unvetted malicious payloads. Transitioning software metadata and artifact distribution to decentralized consensus substrates fundamentally inverts this attack surface. Without a central corporate authority to arbitrate operational disputes or purge compromised artifacts, system security cannot rely on administrative discretion."),
        
        ("ch5_architecture.typ", "Ch5 Sec 5.0 (Architectural Tension)",
         "Modern software engineering rests upon a delicate compromise between cryptographic verification and runtime developer ergonomics. When package managers attempt to eliminate centralized authority by writing complete software archives directly to distributed ledgers, they immediately succumb to prohibitive gas costs and unsustainable storage bloat; conversely, delegating storage entirely to uncoordinated peer-to-peer swarms leaves developers vulnerable to peer churn and mutable pointer poisoning. Resolving this fundamental architectural tension demands an infrastructure that strictly decouples consensus over metadata commitments from the horizontal distribution of physical bytes across decentralized content networks. By structuring the runtime perimeter so that consensus validators record only fixed-size, immutable cryptographic commitments while uncoordinated storage swarms and institutional archival repositories handle multi-megabyte physical distribution payloads, PyChain ensures that local client installations execute with the deterministic rigor of mathematical verification without imposing prohibitive financial or latency penalties on package consumers."),
        
        ("ch8_conclusions.typ", "Ch8 Sec 8.0 (Legacy Registry Limits)",
         "Centralized registries rely on an outdated perimeter security model where trust is implicitly delegated to remote servers, commercial Content Delivery Networks, and mutable storage backends. By relying on centralized metadata indices and unvetted network transport channels where single compromised credentials or malicious package unpublishing cascades catastrophically across global development pipelines, legacy package registries have demonstrated vulnerabilities that cannot be resolved through edge-caching or administrative curation policies alone. High-profile security crises, including the sophisticated multi-year infiltration of the XZ Utils backdoor, the transitive collapse triggered by the unpublishing of left-pad, and massive automated Revival Hijack campaigns on abandoned namespaces, confirm that central repositories represent structural single points of failure.")
    ]

    live_results = []
    for f_name, sec_name, sample_text in live_targets:
        print(f"\n[Interrogando CleverHumanizer Live] {sec_name} ({len(sample_text.split())} parole)...")
        live_res = await check_cleverhumanizer(sample_text)
        live_score = live_res.get("overall_ai_score", "ERR")
        live_badge = live_res.get("badge", "⚪")
        patterns = live_res.get("flagged_ai_patterns", [])

        # Local evaluation on exact same excerpt
        loc_res = evaluate_document(sample_text, target_style="academic_thesis")
        loc_score = loc_res["overall_ai_score"]
        loc_badge = loc_res["verdict_badge"]

        live_results.append({
            "chapter": f_name,
            "section": sec_name,
            "local_score": loc_score,
            "local_badge": loc_badge,
            "live_score": live_score,
            "live_badge": live_badge,
            "patterns": patterns,
            "verdict": live_res.get("verdict_summary", "N/A")
        })

    print("\n" + "=" * 110)
    print(f"{'Capitolo / Sezione':<35} | {'Locale':<10} | {'Live Clever':<13} | {'Pattern AI Segnalati Live'}")
    print("-" * 110)
    for r in live_results:
        live_str = f"{r['live_score']}% {r['live_badge']}" if isinstance(r['live_score'], (int, float)) else str(r['live_score'])
        patt_str = ", ".join(r['patterns'][:3]) if r['patterns'] else "Nessuno (Umano autentico)"
        print(f"{r['section']:<35} | {r['local_score']:>5.1f}% {r['local_badge']} | {live_str:>11} | {patt_str}")
    print("=" * 110)

    # Salvataggio referto completo in JSON
    out_file = root_dir / "tests" / "thesis_audit_report.json"
    audit_data = {
        "local_chapters": [
            {k: v for k, v in cr.items() if k != "raw_text"}
            for cr in local_results
        ],
        "live_cross_validation": live_results
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False)
    print(f"\nReport completo esportato con successo in: {out_file}")

async def main():
    local_res = run_local_audit()
    await run_live_samples(local_res)

if __name__ == "__main__":
    asyncio.run(main())
