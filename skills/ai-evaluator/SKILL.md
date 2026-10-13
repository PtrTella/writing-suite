---
name: ai-evaluator
description: |
  Esegue un audit diagnostico multi-prospettiva accurato su testi in italiano o inglese per valutare quanto un testo sia o meno generato da AI.
  Combina 4 lenti autonome: Emulatore GPTZero locale (Perplessità e Burstiness frase-per-frase), Linter euristico (50+ segnali Clever/Copyleaks),
  Stilometria accademica (Hapax Legomena e Caratteristica K di Yule), e modulo Anti-Bypass (stile Text2Go).
  100% autonomo, locale, offline e deterministico. Non modifica il testo dell'utente, genera un referto oggettivo e una heatmap visiva.
license: MIT
metadata:
  version: "4.0.0"
---

# AI Evaluator: Diagnostica e Audit di Sinteticità del Testo

L'agente funge da **Diagnosta / Termometro** oggettivo. Non modifica né riscrive il testo esaminato. Restituisce una diagnosi matematica basata sul motore locale deterministico di `writing-suite`.

## Come Operare

1. **Esecuzione dell'Audit**:
   Quando l'utente richiede la valutazione di un testo o di un file (`.typ`, `.tex`, `.md`), invoca il tool MCP `evaluate_ai_risk(text=..., file_path=...)` oppure esegui:
   ```bash
   python3 /Users/tella/Workspace/writing-suite/mcp/server.py --evaluate "<percorso_file_o_testo>"
   ```
2. **Generazione del Referto Visivo**:
   Formatta l'output in modo chiaro e leggibile:
   - **Score Globale Ponderato** (0–100%) con barra visuale e badge (`🟢` Autentico Umano < 20%, `🟡` Misto/Editato 20-65%, `🔴` Alto Rischio AI > 65%).
   - **Quadro Comparativo delle 4 Lenti**:
     - *1. Emulatore GPTZero* (Perplessità media e Burstiness di sorpresa).
     - *2. Linter Euristico* (Occorrenze dei 50+ tic statistici).
     - *3. Stilometria Accademica* (Hapax Legomena Ratio e Caratteristica K di Yule).
     - *4. Anti-Bypass Check* (Rilevamento frammentazione anomala o loose openers).
   - **Heatmap Frase-per-Frase**:
     - 🟢 PPL alta (sorpresa autentica umana)
     - 🟡 PPL media (struttura mista)
     - 🔴 PPL bassa (completamento lineare standard AI)
   - **Estremi del Testo**:
     - Frase più prevedibile/robotica
     - Frase più umana/sorprendente
   - **Elenco Dettagliato delle Segnalazioni**: riga, categoria, frammento rilevato e motivazione.
