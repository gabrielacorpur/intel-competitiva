#!/usr/bin/env python3
import sys, re, subprocess
from pathlib import Path

LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCACQAcADASIAAhEBAxEB/8QAHQABAAICAwEBAAAAAAAAAAAAAAYHBQgDBAkCAf/EAE0QAAEDAwEEBAkGCwcCBwAAAAEAAgMEBREGBxIhMQgTQVEUFRYiVWGBk9EyVnGRktIXGDNCVGWClKGjsSMkUlOVwuJisjRyc6LB0+H/xAAcAQEAAQUBAQAAAAAAAAAAAAAAAQIDBAUGBwj/xAA6EQACAQMCAgYHBQgDAAAAAAAAAQIDBBEFIRIxBhNRcZGhFCIyQWGBsVLB0eHwFSMzQlNikvGCorL/2gAMAwEAAhEDEQA/ANwkRFUUhERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBEUXv20HRVhuktru+pKCjrYg0yQyP85mQCMgcsgg/QQrtGhVry4aUXJ/BZ+hTOcYLMnglCLE6Z1HY9TUclZYbnT3CCKTqnvhdkNdgHB9hCyyoqU505OM1hr3MmMlJZTygi+JZI4onyyvbHGxpc5zjgNA5knsChr9q+zlri06wteQccJCR9YCu0bWvXz1UHLHYm/oUzqwh7TSJqixd/1BZLBbmXG9XSloKR7gxk00ga1ziC4AHtJAJwO5R38LOzj532z7Z+CqpWVzWjxU6cmvgmyJVqcHiUkvmTZFCfws7OPnfbPtn4LtWnaRoS7XKC3W/VFunq6h25FEJMF7uwDPae7tVctOvIpt0pJL+1/gUq4ot4U14oliIuKqqIKWnkqaqeOCGNu8+SR4a1o7yTwAWGk28IvHKiglbtg2a0cvVy6uoXO4cYWvlHH1saR8Fl9Pa80bqCUQ2fUttqpjjEImDZDnAGGOw48SBy5nCzJ6dd048c6Uku1xePoWY3FGTwpLPeiSIuOoljp4JJ5nhkUbS97jyAAySoc/avs5a4tOsLXkHHCQkfWArVG1r189VByx2Jv6Fc6sIe00iaooT+FnZx877Z9s/BPws7OPnfbPtn4K9+zL3+jL/F/gUek0ftrxRNkUUs+0bQ14ucFttmp7fU1k7t2KJr+LzjOBkc+Clax61vVoPhqxcX8Vj6lyFSM1mLyEUf1RrTSmmHtjv1+oaCVzd5sUkmZCO/dGTj2LC0O17ZtWyBkOrqBpLtz+2D4hnOOb2gY9fLt5K9T0+7qQ6yFKTj2pPHjgolcUovhlJJ95OkXFTVEFVA2emmjnidndfG4OacHBwR61yrEaaeGXQiw2p9U6d0yyF9/vFJbhPvdT18m6ZN3G9ujmcbwz9KwX4WdnHzvtn2z8FlUrG5qx46dOTXak2i1KvSg8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9+c+R2FtolCNNdasv5mg20XQWotCXTwO90mIpHEU9VHxhnAxxae/iMg4IUWW+G2jTVNqnZteLfNB1s8VO+ppCG5c2eNpLC3tyeLeHHDiO1aHruujOty1a2cqixOLw8cn2M0WqWKtKqUeT5G4PRR1XS3rZ42wMhkjq7HhkziBuPbK+RzC3jzwCCPV61cKpHoh6XdatEVGpTViUX0txCGY6oQSTM59uckq7l5V0jjRjqldUeXF5/zf9snV6a5u1g588eXu8giItKZoREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQHzuM6zrNxu/jd3sccd2V9IiAIiIAiIgCwNfozR9wrJayv0pYqupldvSTTW+J73nvLi3JKzyKunVnSeYSa7tiJQjLaSyRryA0J8ytN/6XB91fcWhNEQysli0bp2ORjg5j22yEFpHIg7vAqRIr3plx/Ufiyjqaf2V4BERYxcCjsuhNETSvll0bp2SR7i573WyElxPMk7vEqRIrlOtUpexJrueCmUIy9pZOCgo6Sgo4qOhpYKWmibuxwwxhjGDuDRwAXOiK2228sqSwEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAf/9k="

MESES = {
    "jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,
    "jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12
}

def ler(arquivo):
    with open(arquivo, encoding="utf-8") as f:
        return f.read()

def normalizar_data(texto):
    texto = texto.strip().lower()
    m = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})", texto)
    if m:
        d, mes, ano = m.group(1), m.group(2), m.group(3)
        if len(ano) == 2: ano = "20" + ano
        return f"{ano}{int(mes):02d}{int(d):02d}"
    m = re.search(r"([a-z]{3})[/\s](\d{4})", texto)
    if m:
        mes_num = MESES.get(m.group(1), 0)
        return f"{m.group(2)}{mes_num:02d}00"
    m = re.search(r"(\d{4})", texto)
    if m:
        return f"{m.group(1)}0000"
    return "00000000"

def badge_rel(texto):
    mapa = {
        "Alta": ("#fce8e8", "#a32d2d", "Alta"),
        "A":    ("#fce8e8", "#a32d2d", "Alta"),
        "Média":("#fef3e2", "#854f0b", "Média"),
        "Media":("#fef3e2", "#854f0b", "Média"),
        "M":    ("#fef3e2", "#854f0b", "Média"),
        "Baixa":("#e0f5ee", "#0f6e56", "Baixa"),
        "B":    ("#e0f5ee", "#0f6e56", "Baixa"),
        "—":    ("#f0f0f0", "#888", "—"),
        "-":    ("#f0f0f0", "#888", "—"),
    }
    if texto not in mapa:
        return texto
    bg, tc, label = mapa[texto]
    return f'<span style="font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px;background:{bg};color:{tc};">{label}</span>'

ORDER_REL = {"Alta":0,"A":0,"Média":1,"Media":1,"M":1,"Baixa":2,"B":2,"—":3,"-":3}

def md_para_html(md):
    html = md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html = re.sub(r"^# (.+)$", r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r'<h2>\1</h2>', html, flags=re.MULTILINE)

    def h3_fmt(m):
        texto = m.group(1)
        rel_m = re.search(r"—\s*(Alta|Média|Media|Baixa)\s*$", texto)
        badge = ""
        if rel_m:
            badge = " " + badge_rel(rel_m.group(1))
            texto = texto[:rel_m.start()].rstrip(" —")
        return f'<h3><strong style="font-size:15px;">{texto}</strong>{badge}</h3>'
    html = re.sub(r"^### (.+)$", h3_fmt, html, flags=re.MULTILINE)

    html = re.sub(r"\*\*(.+?)\*\*", r'<strong>\1</strong>', html)
    html = re.sub(r"\*(.+?)\*", r'<em>\1</em>', html)
    html = re.sub(r"`(.+?)`", r'<code>\1</code>', html)

    # Fontes menores
    html = re.sub(r"<strong>(Fontes?:?)</strong>([^\n]+)",
        r'<span class="fonte"><strong>\1</strong>\2</span>', html)

    # Emojis + quebra de linha antes da ação sugerida
    html = re.sub(r"<strong>(Por que importa[^<]*)</strong>",
        r'<strong>🔔 \1</strong>', html)
    html = re.sub(r"<strong>(Ação sugerida[^<]*)</strong>",
        r'<br><strong>👉 \1</strong>', html)

    html = re.sub(r"^- (.+)$", r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*?</li>\n?)+", lambda m: f'<ul>{m.group()}</ul>', html, flags=re.DOTALL)

    def converter_tabela(m):
        linhas = m.group().strip().split("\n")
        cabecalho, dados, sep_idx = [], [], None
        for i, linha in enumerate(linhas):
            if re.match(r"\|[-| :]+\|", linha):
                sep_idx = i
            elif sep_idx is None:
                cabecalho.append(linha)
            else:
                if linha.strip():
                    dados.append(linha)

        cab_cells = [c.strip().lower() for c in cabecalho[0].strip("|").split("|")] if cabecalho else []
        idx_data = next((i for i,c in enumerate(cab_cells) if "data" in c), None)
        idx_rel  = next((i for i,c in enumerate(cab_cells) if "relev" in c or c == "r"), None)

        def chave(linha):
            cells = [c.strip() for c in linha.strip("|").split("|")]
            dv = cells[idx_data] if idx_data is not None and idx_data < len(cells) else ""
            rv = cells[idx_rel]  if idx_rel  is not None and idx_rel  < len(cells) else "Z"
            dn = normalizar_data(dv)
            rn = ORDER_REL.get(rv.strip(), 9)
            return (dn, rn)

        if idx_data is not None or idx_rel is not None:
            try: dados = sorted(dados, key=chave, reverse=True)
            except: pass

        res = '<div class="table-wrap"><table>'
        for linha in cabecalho:
            cells = [c.strip() for c in linha.strip("|").split("|")]
            res += "<tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>"
        for linha in dados:
            cells = [c.strip() for c in linha.strip("|").split("|")]
            tds = []
            for j, c in enumerate(cells):
                if j == idx_rel and c.strip() in ("Alta","A","Média","Media","M","Baixa","B","—","-"):
                    tds.append(f"<td>{badge_rel(c.strip())}</td>")
                else:
                    tds.append(f"<td>{c}</td>")
            res += "<tr>" + "".join(tds) + "</tr>"
        return res + "</table></div>"

    html = re.sub(r"(\|.+\|\n)+", converter_tabela, html)
    html = re.sub(r"^---$", "<hr>", html, flags=re.MULTILINE)

    linhas = html.split("\n")
    resultado = []
    for linha in linhas:
        s = linha.strip()
        if s and not s.startswith("<"):
            resultado.append(f"<p>{s}</p>")
        else:
            resultado.append(linha)
    return "\n".join(resultado)

def gerar_historico(data_atual):
    arquivos = sorted(Path(".").glob("relatorio-2*.html"), reverse=True)
    links = []
    for arq in arquivos[:10]:
        data = arq.stem.replace("relatorio-", "")
        ativo = "background:#1a1a1a;color:white;" if data == data_atual else "background:#f0f0f0;color:#444;"
        links.append(f'<a href="relatorio-{data}.html" style="{ativo}display:inline-block;font-size:12px;padding:4px 10px;border-radius:6px;text-decoration:none;margin:3px;">{data}</a>')
    return "\n".join(links) if links else '<p style="font-size:13px;color:#888;">Primeira edicao.</p>'

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f0; color: #1a1a1a; line-height: 1.6; }
.container { max-width: 860px; margin: 0 auto; padding: 1.25rem 1rem; }
.topbar { background: white; color: #1a1a1a; padding: 1.25rem 1.5rem; border-radius: 12px; margin-bottom: 1rem; display: flex; align-items: center; gap: 16px; border: 0.5px solid #e5e5e5; }
.topbar img { height: 36px; flex-shrink: 0; }
.topbar-text h1 { font-size: 17px; font-weight: 600; color: #1a1a1a; }
.topbar-text p { font-size: 12px; color: #888; margin-top: 2px; }
.content { background: white; border-radius: 12px; padding: 1.25rem; border: 0.5px solid #e5e5e5; margin-bottom: 1rem; }
.hist { background: white; border-radius: 12px; padding: 1rem 1.25rem; border: 0.5px solid #e5e5e5; margin-bottom: 1rem; }
.hist-title { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #888; margin-bottom: 10px; }
h1 { font-size: 20px; font-weight: 500; margin: 1.25rem 0 0.5rem; }
h2 { font-size: 15px; font-weight: 700; margin: 1.75rem 0 0.75rem; padding-bottom: 8px; border-bottom: 0.5px solid #e5e5e5; }
h3 { font-size: 14px; font-weight: 400; margin: 1.5rem 0 0.5rem; padding: 12px 14px; background: #fafafa; border-left: 3px solid #e24b4a; border-radius: 0 8px 8px 0; line-height: 1.5; }
p { font-size: 13px; color: #444; margin: 0.4rem 0; line-height: 1.65; }
strong { color: #1a1a1a; }
ul { margin: 0.4rem 0 0.4rem 1.2rem; }
li { font-size: 13px; color: #444; margin: 3px 0; }
code { font-size: 12px; background: #f0f0f0; padding: 2px 6px; border-radius: 4px; color: #333; }
hr { border: none; border-top: 0.5px solid #e5e5e5; margin: 1.25rem 0; }
.fonte { display: block; font-size: 11px; color: #999; margin: 6px 0 10px; }
.fonte strong { color: #999; font-weight: 600; }
.table-wrap { overflow-x: auto; margin: 0.75rem 0; -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; font-size: 12px; min-width: 480px; }
th { background: #f5f5f0; font-weight: 600; text-align: left; padding: 7px 8px; border-bottom: 1px solid #e5e5e5; white-space: nowrap; }
td { padding: 7px 8px; border-bottom: 0.5px solid #f0f0f0; color: #444; vertical-align: top; }
tr:last-child td { border-bottom: none; }
.footer { text-align: center; font-size: 11px; color: #aaa; margin-top: 0.75rem; padding-bottom: 2rem; }
@media (max-width: 600px) {
  .container { padding: 0.75rem; }
  .topbar { padding: 1rem; }
  .content { padding: 1rem; }
  h2 { font-size: 14px; }
  h3 { font-size: 13px; }
}
"""

def gerar_pagina(md, data):
    conteudo = md_para_html(md)
    historico = gerar_historico(data)
    m = re.search(r"Semana de (.+?)$", md, re.MULTILINE)
    periodo = m.group(1).strip() if m else ""
    return (
        "<!DOCTYPE html>\n<html lang=\"pt-BR\">\n<head>\n"
        "<meta charset=\"UTF-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "<title>Intel Competitiva — Vector Unitech</title>\n"
        "<style>" + CSS + "</style>\n</head>\n<body>\n"
        "<div class=\"container\">\n"
        "  <div class=\"topbar\">\n"
        f'    <img src="data:image/png;base64,{LOGO_B64}" alt="Vector">\n'
        "    <div class=\"topbar-text\">\n"
        "      <h1>Intelig&ecirc;ncia Competitiva</h1>\n"
        f"      <p>Semana de {periodo}</p>\n"
        "    </div>\n  </div>\n"
        "  <div class=\"content\">\n" + conteudo + "\n  </div>\n"
        "  <div class=\"hist\">\n"
        "    <p class=\"hist-title\">&#128193; Edi&ccedil;&otilde;es anteriores</p>\n"
        + historico + "\n  </div>\n"
        "  <p class=\"footer\">gabrielacorpur.github.io/intel-competitiva</p>\n"
        "</div>\n</body>\n</html>"
    )

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
    result = subprocess.run(["git", "commit", "-m", f"update {data}"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "--allow-empty", "-m", f"force update {data}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"🌐 Publicado: https://gabrielacorpur.github.io/intel-competitiva")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        relatorios = sorted(Path(".").glob("relatorio-*.md"), reverse=True)
        if relatorios:
            arquivo = str(relatorios[0])
            print(f"Usando: {arquivo}")
        else:
            print("Nenhum relatorio encontrado.")
            sys.exit(1)
    else:
        arquivo = sys.argv[1]
    publicar(arquivo)
