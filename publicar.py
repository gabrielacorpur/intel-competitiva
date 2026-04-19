#!/usr/bin/env python3
"""
Converte relatório markdown em HTML e publica no GitHub Pages.
Uso: python3 publicar.py                    (usa o mais recente)
     python3 publicar.py relatorio-XXX.md
"""
import sys, re, subprocess
from pathlib import Path
from datetime import datetime

def ler(arquivo):
    with open(arquivo, encoding="utf-8") as f:
        return f.read()

def md_para_html(md):
    html = md

    # Escapa HTML
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Título h1
    html = re.sub(r"^# (.+)$", r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # h2
    html = re.sub(r"^## (.+)$", r'<h2>\1</h2>', html, flags=re.MULTILINE)

    # h3 com badge de relevância
    def h3_badge(m):
        texto = m.group(1)
        cor = "#e24b4a"
        if "Regulatório" in texto: cor = "#ba7517"
        if "Parceria" in texto: cor = "#0f6e56"
        badge = f'<span style="font-size:11px;padding:2px 8px;border-radius:20px;background:{cor}22;color:{cor};margin-left:8px;font-weight:600;vertical-align:middle;">Alta</span>'
        return f'<h3>{texto}{badge}</h3>'
    html = re.sub(r"^### (.+)$", h3_badge, html, flags=re.MULTILINE)

    # Negrito
    html = re.sub(r"\*\*(.+?)\*\*", r'<strong>\1</strong>', html)

    # Itálico
    html = re.sub(r"\*(.+?)\*", r'<em>\1</em>', html)

    # Código inline
    html = re.sub(r"`(.+?)`", r'<code>\1</code>', html)

    # Listas com bullet
    html = re.sub(r"^- (.+)$", r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*?</li>\n?)+", lambda m: f'<ul>{m.group()}</ul>', html, flags=re.DOTALL)

    # Tabelas markdown
    def converter_tabela(m):
        linhas = m.group().strip().split("\n")
        resultado = '<div class="table-wrap"><table>'
        for i, linha in enumerate(linhas):
            if re.match(r"\|[-| ]+\|", linha):
                continue
            celulas = [c.strip() for c in linha.strip("|").split("|")]
            tag = "th" if i == 0 else "td"
            resultado += "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in celulas) + "</tr>"
        return resultado + "</table></div>"
    html = re.sub(r"(\|.+\|\n)+", converter_tabela, html)

    # Separadores
    html = re.sub(r"^---$", "<hr>", html, flags=re.MULTILINE)

    # Parágrafos
    linhas = html.split("\n")
    resultado = []
    for linha in linhas:
        stripped = linha.strip()
        if stripped and not stripped.startswith("<"):
            resultado.append(f"<p>{stripped}</p>")
        else:
            resultado.append(linha)
    html = "\n".join(resultado)

    return html

def gerar_historico(data_atual):
    arquivos = sorted(Path(".").glob("relatorio-2*.html"), reverse=True)
    links = []
    for arq in arquivos[:10]:
        data = arq.stem.replace("relatorio-", "")
        ativo = "background:#1a1a1a;color:white;" if data == data_atual else "background:#f0f0f0;color:#444;"
        links.append(f'<a href="relatorio-{data}.html" style="{ativo}display:inline-block;font-size:12px;padding:4px 10px;border-radius:6px;text-decoration:none;margin:3px;">{data}</a>')
    return "\n".join(links) if links else '<p style="font-size:13px;color:#888;">Primeira edição.</p>'

def gerar_pagina(md, data):
    conteudo = md_para_html(md)
    historico = gerar_historico(data)
    periodo = ""
    m = re.search(r"Semana de (.+?)$", md, re.MULTILINE)
    if m:
        periodo = m.group(1).strip()

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Intel Competitiva — Vector Unitech</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f0; color: #1a1a1a; line-height: 1.6; }}
  .container {{ max-width: 860px; margin: 0 auto; padding: 2rem 1.5rem; }}
  .topbar {{ background: #1a1a1a; color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; }}
  .topbar h1 {{ font-size: 20px; font-weight: 500; margin-bottom: 4px; }}
  .topbar p {{ font-size: 13px; opacity: 0.55; }}
  .content {{ background: white; border-radius: 12px; padding: 1.5rem 2rem; border: 0.5px solid #e5e5e5; margin-bottom: 1rem; }}
  .hist {{ background: white; border-radius: 12px; padding: 1.25rem 1.5rem; border: 0.5px solid #e5e5e5; margin-bottom: 1rem; }}
  .hist-title {{ font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #888; margin-bottom: 10px; }}
  h1 {{ font-size: 22px; font-weight: 500; margin: 1.5rem 0 0.75rem; color: #1a1a1a; }}
  h2 {{ font-size: 16px; font-weight: 600; margin: 2rem 0 1rem; padding-bottom: 8px; border-bottom: 0.5px solid #e5e5e5; color: #1a1a1a; }}
  h3 {{ font-size: 14px; font-weight: 500; margin: 1.25rem 0 0.5rem; color: #1a1a1a; padding: 10px 12px; background: #fafafa; border-left: 3px solid #e24b4a; border-radius: 0 8px 8px 0; }}
  p {{ font-size: 13px; color: #444; margin: 0.5rem 0; }}
  strong {{ color: #1a1a1a; }}
  ul {{ margin: 0.5rem 0 0.5rem 1.25rem; }}
  li {{ font-size: 13px; color: #444; margin: 4px 0; }}
  code {{ font-size: 12px; background: #f0f0f0; padding: 2px 6px; border-radius: 4px; color: #333; }}
  hr {{ border: none; border-top: 0.5px solid #e5e5e5; margin: 1.5rem 0; }}
  .table-wrap {{ overflow-x: auto; margin: 1rem 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ background: #f5f5f0; font-weight: 600; text-align: left; padding: 8px 10px; border-bottom: 1px solid #e5e5e5; }}
  td {{ padding: 8px 10px; border-bottom: 0.5px solid #f0f0f0; color: #444; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  .footer {{ text-align: center; font-size: 11px; color: #aaa; margin-top: 1rem; padding-bottom: 2rem; }}
</style>
</head>
<body>
<div class="container">
  <div class="topbar">
    <p style="font-size:11px;opacity:0.4;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Vector Unitech</p>
    <h1>Inteligência Competitiva</h1>
    <p>Semana de {periodo}</p>
  </div>

  <div class="content">
    {conteudo}
  </div>

  <div class="hist">
    <p class="hist-title">📁 Edições anteriores</p>
    {historico}
  </div>

  <p class="footer">gabrielacorpur.github.io/intel-competitiva</p>
</div>
</body>
</html>"""

def publicar(arquivo_md):
    md = ler(arquivo_md)
    data = Path(arquivo_md).stem.replace("relatorio-", "")
    html = gerar_pagina(md, data)

    arq_html = f"relatorio-{data}.html"
    with open(arq_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML gerado: {arq_html}")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html atualizado")

    print("📤 Publicando no GitHub Pages...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"relatorio {data}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"🌐 Publicado: https://gabrielacorpur.github.io/intel-competitiva")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        relatorios = sorted(Path(".").glob("relatorio-*.md"), reverse=True)
        if relatorios:
            arquivo = str(relatorios[0])
            print(f"Usando: {arquivo}")
        else:
            print("❌ Nenhum relatório encontrado.")
            sys.exit(1)
    else:
        arquivo = sys.argv[1]
    publicar(arquivo)
