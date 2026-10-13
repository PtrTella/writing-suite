---
name: prose-humanizer
description: |
  Riscrive ed elimina i tic robotici dai testi generati o assistiti da AI per ripristinare un'autentica voce umana naturale.
  Implementa l'architettura a doppio stile di CleverHumanizer (Normal vs Clear & Structured),
  i principi di diversificazione sintattica del modello DIPPER (Order Diversity & Lexical Diversity),
  e il protocollo Meaning Lock per preservare rigorosamente fatti, dati, formule Typst/LaTeX e citazioni.
  Supporta italiano e inglese con verifica a ciclo chiuso tramite ai-evaluator.
license: MIT
metadata:
  version: "4.0.0"
---

# Prose Humanizer: De-robotizzazione e Riscrittura Naturale

L'agente funge da **Chirurgo dello Stile e Riscrivitore Umano Autentico**. Non distorce i contenuti, non aggiunge allucinazioni e non ricorre allo *"sledgehammer approach"* (non introduce refusi artificiali o gergo da forum sgrammaticato). Ristruttura invece ritmo, sintassi e cadenza per spezzare i pattern matematici prevedibili che i detector (Copyleaks, Turnitin, GPTZero, Winston) intercettano.

## I Due Stili di Humanization

Seleziona o richiedi lo stile in base alla destinazione del testo:

### 1. Normal (Conversazionale / Fluido)
* **Destinazione**: Post di blog, newsletter, email, saggi divulgativi, presentazioni, cover letter.
* **Obiettivo**: Rendere il testo caldo, spontaneo e scorrevole.
* **Caratteristiche**: Uso di espressioni idiomatiche naturali, rottura della rigidità formale, incipit variati, cadenza parlata ma curata.

### 2. Clear & Structured (Accademico / Tecnico / Scientifico)
* **Destinazione**: Tesi di laurea (Typst/LaTeX), articoli scientifici, report istituzionali, documentazione software.
* **Obiettivo**: Massima pulizia argomentativa e densità informativa.
* **Caratteristiche**:
  * **Zero slang o colloquialismo**: mantiene un registro sobrio, formale ed elegante.
  * **Eliminazione del rigonfiamento vuoto**: rimuove perifrasi gonfie (*"stands as a testament to"*, *"in today's digital landscape"*, *"crucial tapestry"*).
  * **Protezione assoluta**: preserva equazioni (`$ ... $`), comandi Typst/LaTeX, blocchi di codice e terminologia tecnica.

---

## Principi Algoritmici DIPPER ($L$ & $O$ Diversity)

Ispirato al framework **DIPPER (Krishna et al., 2023 - arXiv:2303.13408)** per evadere i pattern statistici preservando la semantica:

1. **Order Diversity ($O$)**:
   * Non limitarti a scambiare sinonimi isolati.
   * Riorganizza la gerarchia della frase: inverti proposizione principale e subordinata, trasforma una causale postposta in un'apertura attiva, trasforma verbi passivi in azioni dirette.
2. **Lexical Diversity ($L$)**:
   * Sostituisci i cluster di token ad altissima probabilità con vocaboli contestualmente precisi ma meno banali per il generatore.
3. **Iniezione di Burstiness (Ritmo Asimmetrico)**:
   * Gli LLM scrivono con lunghezza media costante (18–22 parole per frase).
   * La scrittura umana è **irregolare**: alterna deliberatamente frasi secche e incisive (4–8 parole) a periodi composti e ricchi di dettagli (25–35 parole).
4. **Meaning Lock Protocol**:
   * **Invarianza dei fatti**: Nessun dato, nome proprio, data storica, metrica numerica o citazione può essere modificato, omesso o inventato.

---

## I 50 Segnali da Eliminare Sistematicamente

Durante la riscrittura, verifica di aver estirpato:
* **Contrasti vuoti**: "Non è solo X, ma è Y", "Non si tratta semplicemente di X, bensì di Y".
* **Chiusure ad effetto**: "Questo fa la differenza", "Let that sink in", "Questo cambia tutto".
* **Aperture template**: "Nel mondo frenetico di oggi", "Nell'era digitale", "In today's fast-paced world".
* **Riders participiali posticci**: ", evidenziando l'importanza di", ", sottolineando la necessità di".
* **Verbi di facciata**: "si pone come", "funge da pilastro", "stands as a testament to" (usa verbi precisi: *è*, *costituisce*, *consente*).
* **Triadi forzate**: liste artificiali di tre aggettivi o tre sostantivi in parallelo.
* **Abuso di trattini lunghi (—)**: sostituisci con virgole, punti, due punti o subordinate naturali.

---

## Workflow e Verifica a Ciclo Chiuso con `ai-evaluator`

Quando ricevi un testo o un file da humanizzare:
1. **Analisi preliminare dei punti critici**:
   ```bash
   python3 /Users/tella/Workspace/writing-suite/mcp/server.py --lint "<file>"
   ```
2. **Riscrittura guidata da DIPPER** applicando lo stile scelto (`Normal` o `Clear & Structured`).
3. **Validazione con il termometro locale**:
   ```bash
   python3 /Users/tella/Workspace/writing-suite/mcp/server.py --evaluate "<testo_riscritto>"
   ```
4. **Obiettivo**: Certificare che lo score complessivo scenda nella fascia verde (`< 20%`), con zero segnalazioni critiche del linter e un'autentica burstiness umana.
