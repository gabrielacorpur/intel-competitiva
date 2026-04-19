#!/usr/bin/env python3
"""
Agente de Inteligência Competitiva — Vector Unitech
Coleta RSS do Google News e gera relatório classificado via Claude Code.

Uso:
    python coletar.py                  # só coleta e salva
    python coletar.py --relatorio      # coleta + imprime relatório para o Claude analisar
    python coletar.py --semana         # agrega capturas dos últimos 7 dias
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen
from xml.etree import ElementTree

# ── Configurações ────────────────────────────────────────────────────────────

PALAVRAS_CHAVE = [
    "programa de fidelidade caminhoneiro",
    "benefícios motorista caminhão",
    "app frete lançamento Brasil",
    "cashback combustível caminhoneiro",
    "Estrada de Prêmios JSL",
    "logtech Brasil",
    "ANTT resolução frete",
    "fintech caminhoneiro",
    "Truckpad lançamento",
    "Fretebras novidade",
    "CargoX Brasil",
    "cartão benefício motorista",
    "embarcador digital motorista",
]

PASTA_CAPTURAS = Path("capturas")

# ── Coleta ───────────────────────────────────────────────────────────────────

def buscar_rss(query: str) -> list[dict]:
    """Busca no Google News RSS e retorna lista de itens."""
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    try:
        with urlopen(url, timeout=10) as resp:
            tree = ElementTree.parse(resp)
    except Exception as e:
        print(f"  ⚠️  Erro ao buscar '{query}': {e}", file=sys.stderr)
        return []

    root = tree.getroot()
    channel = root.find("channel")
    if channel is None:
        return []

    itens = []
    for item in channel.findall("item"):
        titulo = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        fonte = item.findtext("source", "").strip()

        if titulo:
            itens.append({
                "titulo": titulo,
                "link": link,
                "data_publicacao": pub_date,
                "fonte": fonte,
                "query_origem": query,
            })

    return itens


def coletar_tudo() -> list[dict]:
    """Roda todas as queries e deduplica por título."""
    print(f"🔍 Coletando {len(PALAVRAS_CHAVE)} queries no Google News...\n")
    vistos = set()
    todos = []

    for query in PALAVRAS_CHAVE:
        print(f"  → {query}")
        itens = buscar_rss(query)
        for item in itens:
            chave = item["titulo"].lower()[:80]
            if chave not in vistos:
                vistos.add(chave)
                todos.append(item)

    print(f"\n✅ {len(todos)} notícias únicas coletadas.")
    return todos


# ── Persistência ─────────────────────────────────────────────────────────────

def salvar(itens: list[dict]) -> Path:
    """Salva capturas do dia em JSON."""
    PASTA_CAPTURAS.mkdir(exist_ok=True)
    hoje = datetime.now().strftime("%Y-%m-%d")
    arquivo = PASTA_CAPTURAS / f"{hoje}.json"

    # Se já existe, mescla sem duplicar
    existentes = []
    if arquivo.exists():
        with open(arquivo, encoding="utf-8") as f:
            existentes = json.load(f)

    titulos_existentes = {i["titulo"].lower()[:80] for i in existentes}
    novos = [i for i in itens if i["titulo"].lower()[:80] not in titulos_existentes]
    tudo = existentes + novos

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(tudo, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvo em: {arquivo} ({len(novos)} novos, {len(tudo)} total)")
    return arquivo


def carregar_semana() -> list[dict]:
    """Carrega capturas dos últimos 7 dias."""
    todos = []
    vistos = set()
    hoje = datetime.now()

    for i in range(7):
        data = (hoje - timedelta(days=i)).strftime("%Y-%m-%d")
        arquivo = PASTA_CAPTURAS / f"{data}.json"
        if arquivo.exists():
            with open(arquivo, encoding="utf-8") as f:
                itens = json.load(f)
            for item in itens:
                chave = item["titulo"].lower()[:80]
                if chave not in vistos:
                    vistos.add(chave)
                    todos.append(item)

    return todos


# ── Output para o Claude ──────────────────────────────────────────────────────

def formatar_para_claude(itens: list[dict], periodo: str = "hoje") -> str:
    """Formata as notícias para o Claude analisar via Claude Code."""
    linhas = [
        f"# Capturas de Inteligência Competitiva — {periodo}",
        f"Total: {len(itens)} notícias\n",
        "Analise cada notícia conforme as instruções do CLAUDE.md.\n",
        "---\n",
    ]

    for i, item in enumerate(itens, 1):
        linhas.append(f"## [{i}] {item['titulo']}")
        linhas.append(f"- **Fonte:** {item.get('fonte', 'N/A')}")
        linhas.append(f"- **Publicado:** {item.get('data_publicacao', 'N/A')}")
        linhas.append(f"- **Query:** {item.get('query_origem', 'N/A')}")
        linhas.append(f"- **Link:** {item.get('link', 'N/A')}")
        linhas.append("")

    return "\n".join(linhas)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Coleta inteligência competitiva para a Vector Unitech")
    parser.add_argument("--relatorio", action="store_true", help="Gera relatório do dia para análise")
    parser.add_argument("--semana", action="store_true", help="Agrega capturas dos últimos 7 dias")
    parser.add_argument("--so-formatar", action="store_true", help="Só formata o que já foi salvo, sem coletar")
    args = parser.parse_args()

    if args.so_formatar:
        # Apenas formata o arquivo de hoje sem fazer requests
        hoje = datetime.now().strftime("%Y-%m-%d")
        arquivo = PASTA_CAPTURAS / f"{hoje}.json"
        if not arquivo.exists():
            print("❌ Nenhuma captura encontrada para hoje. Rode sem --so-formatar primeiro.")
            sys.exit(1)
        with open(arquivo, encoding="utf-8") as f:
            itens = json.load(f)
        print(formatar_para_claude(itens, hoje))
        return

    if args.semana:
        # Coleta + agrega semana
        itens = coletar_tudo()
        salvar(itens)
        todos_semana = carregar_semana()
        periodo = f"semana até {datetime.now().strftime('%d/%m/%Y')}"
        print("\n" + "=" * 60)
        print(formatar_para_claude(todos_semana, periodo))
        return

    # Fluxo padrão: coleta do dia
    itens = coletar_tudo()
    salvar(itens)

    if args.relatorio:
        hoje = datetime.now().strftime("%d/%m/%Y")
        print("\n" + "=" * 60)
        print(formatar_para_claude(itens, hoje))


if __name__ == "__main__":
    main()
