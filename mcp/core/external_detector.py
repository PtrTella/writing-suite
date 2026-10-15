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

            # Attende che appaia il verdetto
            verdict_data = None
            for _ in range(25):
                await asyncio.sleep(1.0)
                verdict_data = await page.evaluate("""() => {
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

                    if (scoreHead || sentences.length > 0) {
                        return {
                            headText: scoreHead ? scoreHead.innerText.trim() : '',
                            reasonText: verdictReason ? verdictReason.innerText.trim() : '',
                            sentences: sentences,
                            chips: Array.from(new Set(chips))
                        };
                    }
                    return null;
                }""")
                if verdict_data:
                    break

            await browser.close()

            if not verdict_data:
                return {"error": "Timeout in attesa del referto da CleverHumanizer."}

            # Estrazione del punteggio numerico
            head_text = verdict_data.get("headText", "")
            is_human_verdict = "Human" in head_text or "✍️" in head_text
            score_matches = re.findall(r"(\d{1,3})%\s*AI", head_text, re.IGNORECASE)
            
            if score_matches:
                score = float(score_matches[0])
            elif is_human_verdict:
                score = 0.0
            else:
                score = 85.0

            return {
                "engine": "CleverHumanizer.ai (Live Chromium)",
                "overall_ai_score": score,
                "is_human": is_human_verdict,
                "verdict_summary": verdict_data.get("reasonText") or head_text.split("\n")[-1],
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CleverHumanizer.ai External Validator & Rewriter")
    parser.add_argument("--text", type=str, help="Testo da verificare o umanizzare")
    parser.add_argument("--file", type=str, help="Percorso del file da leggere")
    parser.add_argument("--action", choices=["check", "humanize"], default="check", help="Azione da compiere")
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
    elif args.action == "humanize":
        print(f"Esecuzione umanizzazione ({args.mode})...")
        res = asyncio.run(humanize_cleverhumanizer(content, mode=args.mode))
        print(json.dumps(res, indent=2, ensure_ascii=False))
