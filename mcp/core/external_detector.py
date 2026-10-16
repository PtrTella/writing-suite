"""
Writing Suite - External Detector & Humanizer Bridge
Interfaccia headless asincrona ad altissima affidabilità per CleverHumanizer.ai.
Consente la validazione e l'umanizzazione su motori commerciali reali (CleverHumanizer/Copyleaks)
sfruttando l'installazione locale di Google Chrome.
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


async def check_cleverhumanizer(text: str) -> Dict[str, Any]:
    """
    Invia un blocco di testo (minimo 80 parole) a CleverHumanizer.ai Detector
    ed estrae la diagnosi completa frase per frase.
    """
    words = text.strip().split()
    if len(words) < 80:
        return {
            "error": f"Il testo contiene solo {len(words)} parole. CleverHumanizer richiede almeno 80 parole.",
            "overall_ai_score": None,
            "verdict": "TOO_SHORT"
        }

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        try:
            await page.goto("https://cleverhumanizer.ai/ai-detector", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_selector("textarea", timeout=10000)

            # Iniezione sicura del testo tramite il prototipo nativo React/Vue
            await page.evaluate("""(textToInsert) => {
                const textarea = document.querySelector('textarea');
                const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                nativeSetter.call(textarea, textToInsert);
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.dispatchEvent(new Event('change', { bubbles: true }));
            }""", text)

            await asyncio.sleep(0.6)

            # Clicca sul pulsante 'Check for AI'
            btn_clicked = await page.evaluate("""() => {
                const btn = document.querySelector('button.greenBtn') || 
                            Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Check for AI'));
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            }""")

            if not btn_clicked:
                await browser.close()
                return {"error": "Pulsante 'Check for AI' non trovato o non cliccabile."}

            # Attende che appaia il verdetto e che l'animazione percentuale si stabilizzi
            verdict_data = None
            last_raw_score = None
            stable_count = 0

            for _ in range(35):
                await asyncio.sleep(0.8)
                data = await page.evaluate("""() => {
                    const scoreHead = document.querySelector('.score-head');
                    const verdictReason = document.querySelector('.detector-verdict-reason');
                    const bodyText = document.body.innerText;
                    
                    if (bodyText.includes('AI score will appear here.')) {
                        return null;
                    }
                    
                    const sentences = Array.from(document.querySelectorAll('.detector-sentence')).map(el => {
                        const isAi = el.className.includes('sentence-ai');
                        const isMixed = el.className.includes('sentence-mixed');
                        const isHuman = el.className.includes('sentence-human');
                        return {
                            text: el.innerText.trim(),
                            className: el.className,
                            type: isAi ? 'AI' : (isMixed ? 'MIXED' : (isHuman ? 'HUMAN' : 'UNKNOWN')),
                            badge: isAi ? '🔴' : (isMixed ? '🟡' : (isHuman ? '🟢' : '⚪'))
                        };
                    });
                    
                    const chips = Array.from(document.querySelectorAll('.sig-chip')).map(el => el.innerText.replace('↗', '').trim());

                    if (scoreHead && verdictReason && sentences.length > 0) {
                        return {
                            headText: scoreHead.innerText.trim(),
                            reasonText: verdictReason.innerText.trim(),
                            sentences: sentences,
                            chips: Array.from(new Set(chips))
                        };
                    }
                    return null;
                }""")

                if data:
                    raw_head = data.get("headText", "")
                    # Controlla se la percentuale si è stabilizzata (non più in fase di animazione)
                    if raw_head == last_raw_score and ("%" in raw_head):
                        stable_count += 1
                        if stable_count >= 2:
                            verdict_data = data
                            break
                    else:
                        last_raw_score = raw_head
                        stable_count = 0

            await browser.close()

            if not verdict_data:
                return {"error": "Timeout in attesa del referto da CleverHumanizer."}

            # Estrazione del punteggio numerico stabilizzato
            head_text = verdict_data.get("headText", "")
            reason_text = verdict_data.get("reasonText", "")
            
            # Distinzione tra verdetto Human vs AI
            is_human_verdict = head_text.startswith("✍️") or "Human" in head_text.split("\n")[0]
            
            # Match della percentuale visualizzata
            pct_matches = re.findall(r"(\d{1,3})%", head_text)
            if pct_matches:
                displayed_pct = float(pct_matches[0])
                if is_human_verdict:
                    # In CleverHumanizer, se il badge è 'Human', il numero indica la % umana (es. 99% Human -> 1% AI)
                    score = round(max(0.0, 100.0 - displayed_pct), 1)
                else:
                    # Se il badge è 'AI', il numero indica la % AI (es. 94% AI)
                    score = displayed_pct
            elif is_human_verdict:
                score = 0.0
            else:
                score = 85.0

            return {
                "engine": "CleverHumanizer.ai (Live Chromium)",
                "overall_ai_score": score,
                "is_human": is_human_verdict,
                "verdict_summary": reason_text or head_text.split("\n")[-1],
                "badge": "🟢" if score < 25.0 else ("🟡" if score < 60.0 else "🔴"),
                "total_sentences": len(verdict_data.get("sentences", [])),
                "sentence_signals": verdict_data.get("sentences", []),
                "flagged_ai_patterns": verdict_data.get("chips", [])
            }

        except Exception as e:
            await browser.close()
            return {"error": f"Errore durante l'esecuzione del browser: {str(e)}"}


async def humanize_cleverhumanizer(text: str, mode: str = "clear_structured") -> Dict[str, Any]:
    """
    Riscrive il testo con il motore neurale di CleverHumanizer.ai.
    mode: 'clear_structured' (per tesi/paper accademici) oppure 'normal'.
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        try:
            await page.goto("https://cleverhumanizer.ai/", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_selector(".ql-editor", timeout=10000)

            # Seleziona la modalità desiderata
            mode_label = "Clear & Structured" if mode == "clear_structured" else "Normal"
            await page.evaluate("""(targetMode) => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes(targetMode));
                if (btn) btn.click();
            }""", mode_label)

            await asyncio.sleep(0.4)

            # Inserisce il testo nell'editor Quill
            await page.evaluate("""(textToInsert) => {
                const editor = document.querySelector('.ql-editor');
                editor.innerHTML = `<p>${textToInsert}</p>`;
                editor.dispatchEvent(new Event('input', { bubbles: true }));
            }""", text)

            await asyncio.sleep(0.5)

            # Clicca sul pulsante 'Humanize AI'
            await page.evaluate("""() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Humanize AI'));
                if (btn) btn.click();
            }""")

            # Attende che appaia la versione riscritta (max 25s)
            rewritten_text = None
            for _ in range(25):
                await asyncio.sleep(1.0)
                rewritten_text = await page.evaluate("""() => {
                    const editors = Array.from(document.querySelectorAll('.ql-editor'));
                    if (editors.length >= 2 && editors[1].innerText.trim().length > 20) {
                        return editors[1].innerText.trim();
                    }
                    return null;
                }""")
                if rewritten_text:
                    break

            await browser.close()

            if not rewritten_text:
                return {"error": "Timeout in attesa dell'output da CleverHumanizer."}

            return {
                "engine": f"CleverHumanizer.ai Humanizer ({mode_label})",
                "original_words": len(text.split()),
                "humanized_words": len(rewritten_text.split()),
                "humanized_text": rewritten_text
            }

        except Exception as e:
            await browser.close()
            return {"error": f"Errore durante l'umanizzazione: {str(e)}"}


async def check_zerogpt(text: str) -> Dict[str, Any]:
    """
    Invia un blocco di testo al detector ZeroGPT.com tramite Chromium headless.
    Restituisce percentuale AI, verdetto e badge.
    """
    words = text.strip().split()
    if len(words) < 25:
        return {
            "error": "Testo troppo breve per ZeroGPT (minimo 25 parole).",
            "overall_ai_score": None,
            "verdict": "TOO_SHORT"
        }

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        try:
            await page.goto("https://www.zerogpt.com", wait_until="domcontentloaded", timeout=15000)
            await page.evaluate("""text => {
                const ta = document.querySelector("textarea");
                const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                setter.call(ta, text);
                ta.dispatchEvent(new Event("input", { bubbles: true }));
                ta.dispatchEvent(new Event("change", { bubbles: true }));
            }""", text)
            await asyncio.sleep(0.4)
            await page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll("button"));
                const b = btns.find(btn => btn.innerText.includes("Detect Text"));
                if (b) b.click();
            }""")
            await asyncio.sleep(3.5)

            data = await page.evaluate("""() => {
                const textMatch = document.body.innerText.match(/Your Text is [^\\n]+/);
                const pctMatch = document.body.innerText.match(/(\\d+(\\.\\d+)?)%\\s+AI GPT/i);
                return {
                    verdict: textMatch ? textMatch[0].replace("Your Text is ", "").trim() : "Unknown",
                    ai_percentage: pctMatch ? parseFloat(pctMatch[1]) : 0.0
                };
            }""")
            await browser.close()
            pct = data.get("ai_percentage", 0.0)
            return {
                "engine": "ZeroGPT.com (Live)",
                "overall_ai_score": pct,
                "is_human": pct < 35.0,
                "verdict_summary": data.get("verdict", "Unknown"),
                "badge": "🟢" if pct < 30.0 else ("🟡" if pct < 65.0 else "🔴")
            }
        except Exception as e:
            await browser.close()
            return {"error": f"Errore durante l'interrogazione di ZeroGPT: {str(e)}"}


async def check_sapling(text: str) -> Dict[str, Any]:
    """
    Invia un blocco di testo al detector neurale Sapling.ai (sviluppato da ricercatori Stanford/Berkeley).
    Restituisce percentuale complessiva AI, verdetto, badge e breakdown frase per frase.
    """
    words = text.strip().split()
    if len(words) < 20:
        return {
            "error": "Testo troppo breve per Sapling (minimo 20 parole).",
            "overall_ai_score": None,
            "verdict": "TOO_SHORT"
        }

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        try:
            await page.goto("https://sapling.ai/ai-content-detector", wait_until="networkidle", timeout=15000)
            data = await page.evaluate("""async (txt) => {
                const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText);
                let jwtMatch = null;
                for (let s of scripts) {
                    const m = s.match(/eyJhbGciOi[A-Za-z0-9._-]+/);
                    if (m) {
                        jwtMatch = m[0];
                        break;
                    }
                }
                const response = await fetch('https://api.sapling.ai/api/v1/aidetect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: txt, key: jwtMatch || '' })
                });
                return await response.json();
            }""", text)
            await browser.close()

            score_pct = round(float(data.get("score", 0.0)) * 100.0, 1)
            sentences = []
            for s in data.get("sentence_scores", []):
                s_pct = round(float(s.get("score", 0.0)) * 100.0, 1)
                sentences.append({
                    "sentence": s.get("sentence", ""),
                    "ai_pct": s_pct,
                    "badge": "🔴" if s_pct >= 60.0 else ("🟡" if s_pct >= 30.0 else "🟢")
                })

            return {
                "engine": "Sapling.ai (Stanford/Berkeley NLP)",
                "overall_ai_score": score_pct,
                "is_human": score_pct < 35.0,
                "verdict_summary": "Human written" if score_pct < 30.0 else ("Mixed / Uncertain" if score_pct < 65.0 else "AI Generated"),
                "badge": "🟢" if score_pct < 30.0 else ("🟡" if score_pct < 65.0 else "🔴"),
                "total_sentences": len(sentences),
                "sentence_signals": sentences
            }
        except Exception as e:
            await browser.close()
            return {"error": f"Errore durante l'interrogazione di Sapling: {str(e)}"}


async def check_multi_detector(text: str) -> Dict[str, Any]:
    """
    Esegue in parallelo l'audit sui tre principali motori commerciali esterni:
    1. CleverHumanizer.ai (pattern diagnostici e chip)
    2. ZeroGPT.com (perplessità e burstiness)
    3. Sapling.ai (Stanford/Berkeley deep token NLP)
    Restituisce un verdetto di consenso esterno.
    """
    clever_task = check_cleverhumanizer(text)
    zero_task = check_zerogpt(text)
    sapling_task = check_sapling(text)
    
    clever_res, zero_res, sapling_res = await asyncio.gather(
        clever_task, zero_task, sapling_task, return_exceptions=True
    )
    
    clever_out = clever_res if isinstance(clever_res, dict) else {"error": str(clever_res)}
    zero_out = zero_res if isinstance(zero_res, dict) else {"error": str(zero_res)}
    sapling_out = sapling_res if isinstance(sapling_res, dict) else {"error": str(sapling_res)}
    
    scores = []
    for out in [clever_out, zero_out, sapling_out]:
        val = out.get("overall_ai_score")
        if isinstance(val, (int, float)):
            scores.append(val)
        
    avg_score = round(sum(scores) / len(scores), 1) if scores else None
    
    return {
        "consensus_score": avg_score,
        "consensus_badge": "🟢" if avg_score is not None and avg_score < 30.0 else ("🟡" if avg_score is not None and avg_score < 65.0 else "🔴"),
        "consensus_verdict": "Likely Human" if avg_score is not None and avg_score < 35.0 else ("Mixed / Review" if avg_score is not None and avg_score < 65.0 else "Likely AI"),
        "detectors": {
            "cleverhumanizer": clever_out,
            "zerogpt": zero_out,
            "sapling": sapling_out
        }
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Detector External Validator & Rewriter")
    parser.add_argument("--text", type=str, help="Testo da verificare o umanizzare")
    parser.add_argument("--file", type=str, help="Percorso del file da leggere")
    parser.add_argument("--action", choices=["check", "zerogpt", "sapling", "multi", "humanize"], default="multi", help="Azione da compiere")
    parser.add_argument("--mode", choices=["clear_structured", "normal"], default="clear_structured", help="Modalità di riscrittura")

    args = parser.parse_args()

    content = args.text
    if not content and args.file:
        content = Path(args.file).read_text(encoding="utf-8")

    if not content:
        print("Specificare --text o --file.")
        sys.exit(1)

    if args.action == "check":
        print("Esecuzione audit su CleverHumanizer.ai Detector...")
        res = asyncio.run(check_cleverhumanizer(content))
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "zerogpt":
        print("Esecuzione audit su ZeroGPT.com Detector...")
        res = asyncio.run(check_zerogpt(content))
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "sapling":
        print("Esecuzione audit su Sapling.ai Detector...")
        res = asyncio.run(check_sapling(content))
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "multi":
        print("Esecuzione audit multi-detector (CleverHumanizer + ZeroGPT + Sapling)...")
        res = asyncio.run(check_multi_detector(content))
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "humanize":
        print(f"Esecuzione umanizzazione ({args.mode})...")
        res = asyncio.run(humanize_cleverhumanizer(content, mode=args.mode))
        print(json.dumps(res, indent=2, ensure_ascii=False))
