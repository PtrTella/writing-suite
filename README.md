# 🖋️ Writing Suite

> **Toolkit unificato, universale e portabile per la scrittura, la diagnosi AI e la revisione accademica.**  
> Funziona offline e a zero dipendenze su **macOS, Linux e Windows**, compatibile con **Antigravity**, **Claude Desktop**, **Cursor**, **VS Code** e lo standard aperto **Vercel Agent Skills** (`npx skills`).

---

## 🏛️ Architettura: Server MCP (Sensore) + Agent Skills (Cervello)

`Writing Suite` risolve il trade-off fondamentale tra determinismo matematico e intelligenza procedurale:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AGENT SKILLS (Frontend Cognitivo)               │
│                                                                        │
│   • /ai-evaluator     • /academic-editor        • /prose-humanizer     │
│    (Il Diagnosta)       (Il Relatore di Tesi)     (Il Chirurgo Stile)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Chiamate JSON-RPC veloci
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      SERVER MCP (Backend Deterministico)               │
│                                                                        │
│  1. evaluate_ai_risk       -> PPL, Burstiness, Yule K, 50+ Pattern     │
│  2. calculate_readability  -> Gulpease (IT), Flesch (EN), Ritmo frasi  │
│  3. lint_writing           -> Scansione 50+ cliché Clever & Copyleaks  │
│  4. audit_citations        -> Unsupported claims & BibTeX / Typst check│
└────────────────────────────────────────────────────────────────────────┘
```

1. **Il Server MCP (`mcp/server.py`)**:
   * Esegue calcoli matematici rigorosi e costanti nel tempo (PPL continua, deviazione standard del ritmo, indice Gulpease, Yule's K, matching di 50+ regole sintattiche).
   * **Zero dipendenze esterne**: sfrutta solo la standard library di Python 3.9+, funzionando istantaneamente su qualsiasi computer senza virtualenv o `pip install`.
2. **Le Agent Skills (`skills/`)**:
   * Istruiscono qualunque LLM (Gemini, Claude 3.5, GPT-4, Llama locale) su come comportarsi, garantendo che anche cambiando modello i criteri di revisione restino rigorosi e identici.

---

## 🔬 Fondamenti Scientifici & Reverse-Engineering

La suite incorpora le scoperte dei principali benchmark e motori di rilevamento internazionali:

* **Da Copyleaks & Turnitin**:
  * Rilevamento della *densità di token ad alta probabilità* e della *perplessità piatta*.
  * Monitoraggio della **burstiness** (la scrittura umana alterna frasi da 4 parole a periodi da 35 parole; l'AI è monotona attorno a 18–22 parole).
  * Calcolo della **dispersione sillabica** e intercettazione dei *riders participiali* (`", underscoring the need for"`).
* **Da CleverHumanizer.ai**:
  * Integrazione del catalogo dei **50 segnali diagnostici** (prevedibilità, simmetria artificiale, chiusure teatrali, aperture template).
  * Adozione del **Doppio Stile**: modalità *Normal* (conversazionale fluida) vs *Clear & Structured* (accademica sobria, zero slang).
* **Dal Modello DIPPER (Krishna et al., 2023 - arXiv:2303.13408)**:
  * Ristrutturazione basata su **Order Diversity ($O$)** con Kendall's $\tau$ (inversione principale/subordinata) e **Lexical Diversity ($L$)**.
  * **Meaning Lock Protocol**: vincolo rigido di invarianza semantica sui fatti, dati numerici, formule matematiche `$ ... $` e citazioni bibliografiche.

---

## 🛠️ Le 3 Skill della Suite

### 1. `/ai-evaluator` (Il Termometro / Diagnosta)
* **Cosa fa**: Esegue un audit senza toccare né riscrivere una singola parola.
* **Cosa restituisce**:
  * Indice sintetico ponderato (0–100%) con verdetto a semaforo (🟢 Umano, 🟡 Misto, 🔴 AI).
  * Quadro a 4 lenti: GPTZero emulato, Linter a 50+ regole, Stilometria Yule/Hapax, Anti-Bypass.
  * Heatmap frase-per-frase (🟢🟡🔴) e isolamento della frase più robotica e più umana.

### 2. `/academic-editor` (Il Relatore di Tesi)
* **Cosa fa**: Revisiona tesi (Typst/LaTeX), articoli scientifici e report tecnici.
* **Cosa restituisce**:
  * Valutazione dell'**Indice Gulpease** (target 38–52 per livello accademico/laurea).
  * Segnalazione automatica di affermazioni prive di riscontro con `[citazione richiesta]`.
  * Verifica incrociata con il file `.bib` (chiavi mancanti o orfane).
  * Protezione assoluta al 100% di formule `$ ... $`, macro Typst `#figure(...)` e codice.

### 3. `/prose-humanizer` (Il Chirurgo dello Stile)
* **Cosa fa**: Riscrive testi robotici trasformandoli in prosa autentica e naturale.
* **Caratteristiche**:
  * Scelta tra stile **Normal** (per blog/email/post) e **Clear & Structured** (per saggi/report).
  * Applicazione dei principi DIPPER ($L$ & $O$ diversity) e iniezione di burstiness ritmica.
  * Verifica a ciclo chiuso: convalida automatica con `ai-evaluator` per garantire uno score finale < 15%.

---

## 📦 Installazione Rapida

### Metodo 1: Script Automatico (Consigliato)
Clona o scarica il repository ed esegui:
```bash
git clone https://github.com/tuo-user/writing-suite.git ~/writing-suite
cd ~/writing-suite
bash install.sh
```
Lo script testa i moduli e collega le skill sia in Antigravity (`~/.gemini/config/skills/`) che nello standard globale (`~/.agents/skills/`).

### Metodo 2: Tramite standard Agent Skills CLI (`npx skills`)
```bash
npx skills add tuo-user/writing-suite
```

---

## 🔌 Configurazione Server MCP

Per usare i tool deterministici direttamente nei tuoi editor:

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "writing-suite": {
      "command": "python3",
      "args": ["/Users/tella/Workspace/writing-suite/mcp/server.py"]
    }
  }
}
```

### Cursor (`.cursor/mcp.json`) o VS Code
```json
{
  "mcpServers": {
    "writing-suite": {
      "command": "python3",
      "args": ["/Users/tella/Workspace/writing-suite/mcp/server.py"]
    }
  }
}
```

---

## 💻 Uso Diretto da Riga di Comando (CLI)

Il server MCP può essere usato direttamente anche come potente CLI locale senza client MCP:

```bash
# Valutare un capitolo di tesi Typst o Markdown:
python3 mcp/server.py --evaluate /path/to/capitolo1.typ

# Calcolare indice Gulpease e cadenza ritmica:
python3 mcp/server.py --readability /path/to/testo.txt --lang it

# Scansionare i 50+ cliché dell'AI:
python3 mcp/server.py --lint /path/to/bozza.md

# Verificare le citazioni e coerenza con file .bib:
python3 mcp/server.py --citations /path/to/capitolo.tex --bib /path/to/refs.bib
```

---

## 🧪 Test Suite

Tutti i componenti sono coperti da unit test automatizzati:
```bash
python3 tests/test_suite.py
```
Output atteso:
```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.005s

OK
```

---

## 📄 Licenza
Rilasciato sotto licenza MIT. Libero per uso accademico, personale e professionale.
