#!/bin/zsh
cd ~/intel-competitiva
echo "🔍 Coletando notícias da semana..."
python3 coletar.py --semana
echo ""
echo "🤖 Gerando relatório com Claude..."
ARQUIVO="relatorio-$(date +%Y-%m-%d).md"
python3 coletar.py --so-formatar | claude -p "gere o relatório semanal conforme CLAUDE.md" > "$ARQUIVO"
echo ""
echo "✅ Pronto! Abrindo relatório..."
open -a TextEdit "$ARQUIVO"
