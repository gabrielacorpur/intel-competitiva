#!/usr/bin/env python3
"""
Gera o one-pager HTML para GitHub Pages a partir do relatório markdown.
Uso: python3 publicar.py relatorio-2026-04-19.md
"""

import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime

def ler_relatorio(arquivo: str) -> str:
    with open(arquivo, encoding="utf-8") as f:
        return f.read()

def extrair_secoes(md: str) -> dict:
    secoes = {}
    secoes["titulo"] = re.search(r"^# (.+)$", md, re.MULTILINE)
    secoes["titulo"] = secoes["titulo"].group(1) if secoes["titulo"] else "Inteligência Competitiva"

    alta = re.findall(r"### \d+\. (.+?)\n[\s\S]+?(?=### \d+\.|## 📦|$)", md)
    secoes["alta_relevancia"] = alta[:5]

    oportunidades = re.findall(r"\d+\. \*\*(.+?)\*\*[— -]+(.+?)(?=\n\d+\.|\n---|\Z)", md)
    secoes["oportunidades"] = oportunidades[:5]

    rodape = re.search(r"\*Relatório gerado em (.+?)\*", md)
    secoes["rodape"] = rodape.group(1) if rodape else f"Gerado em {datetime.now().strftime('%d/%m/%Y')}"

    return secoes

def gerar_html(md: str, data_relatorio: str) -> str:
    secoes = extrair_secoes(md)

    alertas_html = ""
    cores = ["#E24B4A", "#BA7517", "#185FA5", "#0F6E56", "#993556"]
    for i, item in enumerate(secoes["alta_relevancia"]):
        cor = cores[i % len(cores)]
        alertas_html += f"""
        <div class="alert-card" style="border-left-color: {cor}">
            <p class="alert-title">{item}</p>
        </div>"""

    opps_html = ""
    for i, (titulo, desc) in enumerate(secoes["oportunidades"], 1):
        opps_html += f"""
        <div class="opp-item">
            <span class="opp-num">{i}</span>
            <div>
                <p class="opp-title">{titulo}</p>
                <p class="opp-desc">{desc.strip()}</p>
            </div>
        </div>"""

    semana_anterior = ""
    arquivos = sorted(Path(".").glob("relatorio-*.md"), reverse=True)
    historico_html = ""
    for arq in arquivos[:10]:
        data = arq.stem.replace("relatorio-", "")
        ativo = "active" if data == data_relatorio else ""
        historico_html += f'<a href="relatorio-{data}.html" class="hist-link {ativo}">{data}</a>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Intel Competitiva — Vector Unitech</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f0; color: #1a1a1a; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }}
  .header {{ background: #1a1a1a; color: white; padding: 2rem 1.5rem; margin-bottom: 1.5rem; border-radius: 12px; }}
  .header h1 {{ font-size: 20px; font-weight: 500; margin-bottom: 6px; }}
  .header p {{ font-size: 13px; opacity: 0.6; }}
  .badges {{ display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }}
  .badge {{ font-size: 11px; padding: 4px 10px; border-radius: 20px; font-weight: 500; }}
  .badge-red {{ background: #fce8e8; color: #a32d2d; }}
  .badge-amber {{ background: #fef3e2; color: #854f0b; }}
  .badge-teal {{ background: #e0f5ee; color: #0f6e56; }}
  .section {{ background: white; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; border: 0.5px solid #e5e5e5; }}
  .section-title {{ font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #888; margin-bottom: 12px; }}
  .alert-card {{ border-left: 3px solid #e24b4a; padding: 10px 12px; margin-bottom: 8px; background: #fafafa; border-radius: 0 8px 8px 0; }}
  .alert-card:last-child {{ margin-bottom: 0; }}
  .alert-title {{ font-size: 13px; color: #1a1a1a; line-height: 1.4; }}
  .opp-item {{ display: flex; gap: 12px; padding: 10px 0; border-bottom: 0.5px solid #f0f0f0; }}
  .opp-item:last-child {{ border-bottom: none; }}
  .opp-num {{ font-size: 13px; font-weight: 600; color: #888; min-width: 20px; }}
  .opp-title {{ font-size: 13px; font-weight: 500; color: #1a1a1a; margin-bottom: 2px; }}
  .opp-desc {{ font-size: 12px; color: #666; line-height: 1.5; }}
  .hist-link {{ display: inline-block; font-size: 12px; padding: 4px 10px; border-radius: 6px; background: #f0f0f0; color: #444; text-decoration: none; margin: 3px; }}
  .hist-link.active {{ background: #1a1a1a; color: white; }}
  .hist-link:hover {{ background: #ddd; }}
  .footer {{ text-align: center; font-size: 11px; color: #aaa; margin-top: 1.5rem; }}
  .full-report {{ margin-top: 8px; }}
  .full-report summary {{ font-size: 13px; color: #185FA5; cursor: pointer; padding: 8px 0; }}
  .full-report pre {{ font-size: 12px; line-height: 1.6; color: #444; white-space: pre-wrap; padding: 12px; background: #fafafa; border-radius: 8px; margin-top: 8px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Inteligência Competitiva — Vector Unitech</h1>
    <p>{secoes["titulo"]}</p>
    <div class="badges">
      <span class="badge badge-red">Alta relevância</span>
      <span class="badge badge-amber">Mercado logístico</span>
      <span class="badge badge-teal">Oportunidades</span>
    </div>
  </div>

  <div class="section">
    <p class="section-title">🚨 Movimentos de alta relevância</p>
    {alertas_html}
  </div>

  <div class="section">
    <p class="section-title">💡 Oportunidades para a Vector</p>
    {opps_html}
  </div>

  <div class="section">
    <p class="section-title">📁 Edições anteriores</p>
    {historico_html if historico_html else '<p style="font-size:13px;color:#888;">Nenhuma edição anterior ainda.</p>'}
  </div>

  <div class="section">
    <p class="section-title">📄 Relatório completo</p>
    <details class="full-report">
      <summary>Ver relatório completo desta semana</summary>
      <pre>{md}</pre>
    </details>
  </div>

  <p class="footer">{secoes["rodape"]} · gabrielacorpur.github.io/intel-competitiva</p>
</div>
</body>
</html>"""

def publicar(arquivo_md: str):
    md = ler_relatorio(arquivo_md)
    data = Path(arquivo_md).stem.replace("relatorio-", "")

    html = gerar_html(md, data)

    arquivo_html = f"relatorio-{data}.html"
    with open(arquivo_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML gerado: {arquivo_html}")

    index_html = gerar_html(md, data)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("✅ index.html atualizado")

    print("📤 Publicando no GitHub Pages...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"relatorio {data}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"🌐 Publicado em: https://gabrielacorpur.github.io/intel-competitiva")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        relatorios = sorted(Path(".").glob("relatorio-*.md"), reverse=True)
        if relatorios:
            arquivo = str(relatorios[0])
            print(f"Usando relatório mais recente: {arquivo}")
        else:
            print("❌ Nenhum relatório encontrado. Passe o arquivo como argumento.")
            sys.exit(1)
    else:
        arquivo = sys.argv[1]

    publicar(arquivo)
