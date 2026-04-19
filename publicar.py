#!/usr/bin/env python3
"""
Gera o one-pager HTML para GitHub Pages a partir do relatório markdown.
Uso: python3 publicar.py relatorio-2026-04-19.md
     python3 publicar.py  (usa o mais recente automaticamente)
"""

import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime


def ler_relatorio(arquivo: str) -> str:
    with open(arquivo, encoding="utf-8") as f:
        return f.read()


def extrair_alta_relevancia(md: str) -> list:
    items = []
    blocos = re.findall(
        r"### \d+\.\s*\[(.+?)\]\s*(.+?)\n"
        r".*?\*\*Fontes?:?\*\*[^\n]*\n"
        r".*?\*\*Relevância:?\*\*[^\n]*\n\n"
        r"\*\*Resumo:?\*\*\s*(.+?)\n\n"
        r"\*\*Por que importa[^*]*\*\*\s*(.+?)\n\n"
        r"\*\*Ação sugerida:?\*\*\s*(.+?)(?=\n---|\n###|\Z)",
        md, re.DOTALL
    )
    for cat, titulo, resumo, importa, acao in blocos:
        items.append({
            "categoria": cat.strip(),
            "titulo": titulo.strip(),
            "resumo": resumo.strip().replace("\n", " "),
            "importa": importa.strip().replace("\n", " "),
            "acao": acao.strip().replace("\n", " "),
        })
    return items[:5]


def extrair_oportunidades(md: str) -> list:
    items = []
    matches = re.findall(
        r"\d+\.\s*\*\*(.+?)\*\*[:\s—–-]+(.+?)(?=\n\d+\.|\n---|\n##|\Z)",
        md, re.DOTALL
    )
    for titulo, desc in matches:
        items.append({
            "titulo": titulo.strip(),
            "desc": desc.strip().replace("\n", " ")
        })
    return items[:5]


def extrair_regulatorio(md: str) -> list:
    items = []
    secao = re.search(r"## 📋 Regulatório.+?(?=## |\Z)", md, re.DOTALL)
    if not secao:
        return items
    linhas = re.findall(
        r"\|\s*(.+?)\s*\|\s*[^\|]+\s*\|\s*[^\|]+\s*\|\s*\*\*?(Alto|Médio|Baixo)\*?\*?",
        secao.group()
    )
    for texto, nivel in linhas:
        if texto and "Ação" not in texto and "---" not in texto:
            items.append({"texto": texto.strip(), "nivel": nivel.strip()})
    return items[:5]


def extrair_metricas(md: str, alta: list) -> dict:
    total = re.search(r"(\d+) notícias", md)
    return {
        "total": total.group(1) if total else "666",
        "alta": str(len(alta)),
        "players": "14",
    }


def extrair_periodo(md: str) -> str:
    match = re.search(r"Semana de (.+?)$", md, re.MULTILINE)
    return match.group(1).strip() if match else datetime.now().strftime("%d/%m/%Y")


def extrair_rodape(md: str) -> str:
    match = re.search(r"\*Relatório gerado em (.+?)\*", md)
    return match.group(1) if match else f"Gerado em {datetime.now().strftime('%d/%m/%Y')}"


def cor_categoria(cat: str) -> tuple:
    mapa = {
        "Produto": ("#fce8e8", "#a32d2d"),
        "Regulatório": ("#fef3e2", "#854f0b"),
        "Parceria": ("#e0f5ee", "#0f6e56"),
        "Campanha": ("#e6f1fb", "#185fa5"),
        "Contratação": ("#f3eefe", "#533ab7"),
    }
    return mapa.get(cat, ("#f0f0f0", "#444"))


def cor_nivel(nivel: str) -> tuple:
    if nivel == "Alto":
        return ("#fce8e8", "#a32d2d")
    if nivel == "Médio":
        return ("#fef3e2", "#854f0b")
    return ("#e0f5ee", "#0f6e56")


def gerar_historico_html(data_atual: str) -> str:
    arquivos = sorted(Path(".").glob("relatorio-*.html"), reverse=True)
    links = []
    for arq in arquivos[:10]:
        data = arq.stem.replace("relatorio-", "")
        if data == "index":
            continue
        if data == data_atual:
            style = 'style="background:#1a1a1a;color:white;"'
        else:
            style = 'style="background:#f0f0f0;color:#444;"'
        links.append(f'<a href="relatorio-{data}.html" {style} class="hist-link">{data}</a>')
    return "\n".join(links) if links else '<p style="font-size:13px;color:#888;">Primeira edição.</p>'


def gerar_html(md: str, data: str) -> str:
    alta = extrair_alta_relevancia(md)
    opps = extrair_oportunidades(md)
    regs = extrair_regulatorio(md)
    metricas = extrair_metricas(md, alta)
    periodo = extrair_periodo(md)
    rodape = extrair_rodape(md)
    historico = gerar_historico_html(data)

    cores_borda = ["#e24b4a", "#ba7517", "#185fa5", "#0f6e56", "#993556"]

    alertas_html = ""
    for i, item in enumerate(alta):
        bg, tc = cor_categoria(item["categoria"])
        borda = cores_borda[i % len(cores_borda)]
        alertas_html += f"""
        <div style="border:0.5px solid #e5e5e5;border-left:3px solid {borda};border-radius:0 10px 10px 0;padding:14px;margin-bottom:10px;background:#fafafa;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;background:{bg};color:{tc};">{item["categoria"]}</span>
          </div>
          <p style="font-size:14px;font-weight:500;color:#1a1a1a;margin-bottom:6px;line-height:1.4;">{item["titulo"]}</p>
          <p style="font-size:12px;color:#555;line-height:1.6;margin-bottom:8px;">{item["resumo"]}</p>
          <p style="font-size:12px;color:#888;line-height:1.5;margin-bottom:8px;font-style:italic;">{item["importa"]}</p>
          <p style="font-size:12px;color:#185fa5;padding-top:8px;border-top:0.5px solid #e5e5e5;">→ {item["acao"]}</p>
        </div>"""

    if not alertas_html:
        alertas_html = '<p style="font-size:13px;color:#888;">Nenhum item de alta relevância extraído.</p>'

    opps_html = ""
    for i, opp in enumerate(opps, 1):
        opps_html += f"""
        <div style="display:flex;gap:12px;padding:12px 0;border-bottom:0.5px solid #f5f5f5;">
          <span style="font-size:14px;font-weight:600;color:#ccc;min-width:20px;">{i}</span>
          <div>
            <p style="font-size:13px;font-weight:500;color:#1a1a1a;margin-bottom:3px;">{opp["titulo"]}</p>
            <p style="font-size:12px;color:#666;line-height:1.5;">{opp["desc"]}</p>
          </div>
        </div>"""

    if not opps_html:
        opps_html = '<p style="font-size:13px;color:#888;padding:8px 0;">Nenhuma oportunidade extraída.</p>'

    regs_html = ""
    for reg in regs:
        bg, tc = cor_nivel(reg["nivel"])
        regs_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:0.5px solid #f5f5f5;">
          <span style="font-size:13px;color:#1a1a1a;">{reg["texto"]}</span>
          <span style="font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;background:{bg};color:{tc};white-space:nowrap;margin-left:12px;">{reg["nivel"]}</span>
        </div>"""

    if not regs_html:
        regs_html = '<p style="font-size:13px;color:#888;padding:8px 0;">Nenhum item regulatório extraído.</p>'

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
  .section {{ background: white; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; border: 0.5px solid #e5e5e5; }}
  .section-title {{ font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #888; margin-bottom: 14px; }}
  .hist-link {{ display:inline-block; font-size:12px; padding:4px 10px; border-radius:6px; text-decoration:none; margin:3px; }}
  .hist-link:hover {{ opacity:0.8; }}
  details summary {{ font-size:13px; color:#185fa5; cursor:pointer; padding:4px 0; }}
  details pre {{ font-size:12px; line-height:1.6; color:#444; white-space:pre-wrap; padding:12px; background:#fafafa; border-radius:8px; margin-top:10px; }}
</style>
</head>
<body>
<div class="container">

  <div style="background:#1a1a1a;color:white;padding:1.75rem;border-radius:12px;margin-bottom:1rem;">
    <p style="font-size:11px;opacity:0.4;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.08em;">Vector Unitech</p>
    <h1 style="font-size:22px;font-weight:500;margin-bottom:6px;">Inteligência Competitiva</h1>
    <p style="font-size:13px;opacity:0.55;">Semana de {periodo}</p>
    <div style="display:flex;gap:8px;margin-top:16px;flex-wrap:wrap;">
      <span style="font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;background:#fce8e8;color:#a32d2d;">{metricas["alta"]} alertas altos</span>
      <span style="font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;background:#fef3e2;color:#854f0b;">{metricas["players"]} players monitorados</span>
      <span style="font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px;background:#e0f5ee;color:#0f6e56;">5 oportunidades</span>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:1rem;">
    <div style="background:white;border-radius:10px;padding:16px;text-align:center;border:0.5px solid #e5e5e5;">
      <p style="font-size:11px;color:#888;margin-bottom:6px;">Notícias analisadas</p>
      <p style="font-size:24px;font-weight:500;">{metricas["total"]}</p>
    </div>
    <div style="background:white;border-radius:10px;padding:16px;text-align:center;border:0.5px solid #e5e5e5;">
      <p style="font-size:11px;color:#888;margin-bottom:6px;">Alta relevância</p>
      <p style="font-size:24px;font-weight:500;color:#a32d2d;">{metricas["alta"]}</p>
    </div>
    <div style="background:white;border-radius:10px;padding:16px;text-align:center;border:0.5px solid #e5e5e5;">
      <p style="font-size:11px;color:#888;margin-bottom:6px;">Players monitorados</p>
      <p style="font-size:24px;font-weight:500;">{metricas["players"]}</p>
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
    <p class="section-title">📋 Regulatório da semana</p>
    {regs_html}
  </div>

  <div class="section">
    <p class="section-title">📁 Edições anteriores</p>
    {historico}
  </div>

  <div class="section">
    <p class="section-title">📄 Relatório completo</p>
    <details>
      <summary>Ver relatório completo desta semana</summary>
      <pre>{md}</pre>
    </details>
  </div>

  <p style="text-align:center;font-size:11px;color:#aaa;margin-top:1.5rem;padding-bottom:2rem;">{rodape} · gabrielacorpur.github.io/intel-competitiva</p>

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

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
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
            print("❌ Nenhum relatório encontrado.")
            sys.exit(1)
    else:
        arquivo = sys.argv[1]

    publicar(arquivo)
