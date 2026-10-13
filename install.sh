#!/usr/bin/env bash
# ==============================================================================
# Writing Suite - Universal Installer & Linking Script
# Collega la suite di scrittura e MCP Server su Antigravity, Claude Desktop, Cursor e VS Code.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER_PATH="$SCRIPT_DIR/mcp/server.py"

echo "======================================================================"
echo "  🚀 Installazione e Configurazione di Writing Suite"
echo "======================================================================"

# 1. Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Errore: Python 3 non è installato o non si trova nel PATH."
    exit 1
fi

echo "✔ Rilevato Python: $(python3 --version)"

# 2. Rendi eseguibile il server MCP (se i permessi lo consentono)
chmod +x "$MCP_SERVER_PATH" 2>/dev/null || true
echo "✔ Server MCP configurato: $MCP_SERVER_PATH"

# 3. Esegui i test di integrità
echo "⏳ Esecuzione test suite..."
python3 "$SCRIPT_DIR/tests/test_suite.py"
echo "✔ Tutti i test completati con successo!"

# 4. Creazione directory di destinazione
mkdir -p "$HOME/.gemini/config/skills"
mkdir -p "$HOME/.agents/skills"

# 5. Collegamento delle Skill in Antigravity (~/.gemini/config/skills/)
echo "🔗 Collegamento delle Skill in Antigravity (~/.gemini/config/skills/)..."
for skill_dir in "$SCRIPT_DIR/skills/"*; do
    if [ -d "$skill_dir" ]; then
        skill_name="$(basename "$skill_dir")"
        target="$HOME/.gemini/config/skills/$skill_name"
        rm -rf "$target"
        ln -sf "$skill_dir" "$target"
        echo "   -> $skill_name collegato in Antigravity"
    fi
done

# 6. Collegamento delle Skill nello standard Agent Skills (~/.agents/skills/)
echo "🔗 Collegamento delle Skill nello standard Agent Skills (~/.agents/skills/)..."
for skill_dir in "$SCRIPT_DIR/skills/"*; do
    if [ -d "$skill_dir" ]; then
        skill_name="$(basename "$skill_dir")"
        target="$HOME/.agents/skills/$skill_name"
        rm -rf "$target"
        ln -sf "$skill_dir" "$target"
        echo "   -> $skill_name collegato in ~/.agents/skills/"
    fi
done

echo ""
echo "======================================================================"
echo "  🎉 Installazione completata con successo!"
echo "======================================================================"
echo ""
echo "Per configurare il server MCP sui tuoi editor/client preferiti, aggiungi"
echo "il seguente blocco di configurazione:"
echo ""
echo "--- [1] CLAUDE DESKTOP (~/Library/Application Support/Claude/claude_desktop_config.json) ---"
cat << EOF
{
  "mcpServers": {
    "writing-suite": {
      "command": "python3",
      "args": ["$MCP_SERVER_PATH"]
    }
  }
}
EOF
echo ""
echo "--- [2] CURSOR (.cursor/mcp.json) o VS CODE ---"
cat << EOF
{
  "mcpServers": {
    "writing-suite": {
      "command": "python3",
      "args": ["$MCP_SERVER_PATH"]
    }
  }
}
EOF
echo ""
echo "Comandi disponibili da chat:"
echo "  • /ai-evaluator      -> Audit diagnostico PPL, Burstiness, Yule K e 50 pattern"
echo "  • /academic-editor   -> Revisione rigore tesi, Typst/LaTeX, Gulpease, citazioni"
echo "  • /prose-humanizer   -> Riscrittura naturale bilingue (Normal vs Structured, DIPPER)"
echo "======================================================================"
