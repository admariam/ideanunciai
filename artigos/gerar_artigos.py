"""Gera artigos.html e as páginas de artigos do site Ide, anunciai! a partir de arquivos .md.

Uso: python3 gerar_artigos.py <raiz_do_site>
Os artigos ficam em <raiz>/artigos/fontes/<slug>.md, com um cabeçalho de metadados:
---
titulo: ...
frase: ...
autor: ...
data: AAAA-MM-DD
imagem: assets/artigos/<slug>.jpg   (opcional)
---
"""
import html, json, os, re, sys, datetime
from urllib.parse import quote
import markdown

RAIZ = sys.argv[1]
FONTES = os.path.join(RAIZ, "artigos", "fontes")
SITE = "https://ideanunciai.com.br"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Ide, anunciai!">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
{ogimage}<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#ffffff;color:#1b2436;font-family:'EB Garamond',Georgia,serif}}
a{{color:#8a2f2a;text-decoration:none}}a:hover{{color:#6b221e}}::selection{{background:#dbe3f0}}
.nav a{{color:#d3d9e6;padding:7px 14px;border-radius:999px;white-space:nowrap}}
.nav a:hover{{color:#fff;background:#23325a}}
.nav a.ativo{{color:#fff;background:#23325a}}
.rodape a{{color:#a7b0c4}}.rodape a:hover{{color:#fff}}
.texto{{font-size:19px;line-height:1.7;text-align:justify;hyphens:auto}}
.texto p{{margin:0 0 1.1em}}
.texto h2{{margin:1.6em 0 0.6em;font-weight:500;font-size:27px;line-height:1.2;text-align:left;color:#14213d}}
.texto h2:first-child{{margin-top:0}}
.texto em{{color:#2a3450}}
.texto ul{{margin:0 0 1.1em;padding-left:1.2em}}
.texto li{{margin:0 0 0.3em}}
.texto .refs{{margin-top:2.4em;padding-top:1.6em;border-top:1px solid #e3e8f0;font-family:'Source Sans 3',sans-serif;font-size:14px;line-height:1.55;text-align:left;color:#3a4458}}
.texto .refs h2{{font-family:'EB Garamond',serif;font-size:22px;margin-top:0}}
.texto .refs p{{margin:1em 0 0.4em}}
.cartao{{display:flex;gap:18px;align-items:center;padding:12px;border:1px solid #e3e8f0;border-radius:18px;color:#1b2436}}
.cartao:hover{{color:#1b2436;border-color:#c9d3e3;box-shadow:0 8px 22px rgba(20,33,61,0.08)}}
@media (max-width:560px){{.cartao .img{{width:88px!important}}.texto{{font-size:18px}}}}
</style>
</head>
<body>
<div style="min-height:100vh;display:flex;flex-direction:column">
  <header style="background:#14213d;color:#f3efe8">
    <div style="max-width:1120px;margin:0 auto;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap">
      <a href="/index.html" style="display:flex;flex-direction:column;gap:2px;color:#f3efe8">
        <span style="font-size:21px;font-weight:500;letter-spacing:0.02em;line-height:1">Ide, anunciai!</span>
        <span style="font-family:'Source Sans 3',sans-serif;font-size:9px;letter-spacing:0.24em;text-transform:uppercase;color:#a7b0c4">Meditação diária do Evangelho</span>
      </a>
      <nav class="nav" style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-family:'Source Sans 3',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.06em">
        <a href="/index.html">Início</a>
        <a href="/reflexao.html">Evangelho do dia</a>
        <a href="/artigos.html" class="ativo">Artigos</a>
      </nav>
    </div>
  </header>
"""

FOOT = """
  <footer class="rodape" style="background:#14213d;color:#a7b0c4;font-family:'Source Sans 3',sans-serif;font-size:12px">
    <div style="max-width:1120px;margin:0 auto;padding:30px 20px 20px;display:flex;flex-wrap:wrap;gap:30px;justify-content:space-between">
      <div style="flex:1 1 238px;display:flex;flex-direction:column;gap:8px">
        <span style="font-family:'EB Garamond',serif;font-size:20px;color:#f3efe8">Ide, anunciai!</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px">
        <span style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:#f3efe8">Navegação</span>
        <a href="/index.html">Início</a>
        <a href="/reflexao.html">Evangelho do dia</a>
        <a href="/todas.html">Todas as reflexões</a>
        <a href="/artigos.html">Artigos</a>
      </div>
    </div>
    <div style="max-width:1120px;margin:0 auto;padding:12px 20px 20px;border-top:1px solid #23325a;font-size:11px">© 2026 Ide, anunciai!</div>
  </footer>
</div>
</body>
</html>
"""


def ler(caminho):
    bruto = open(caminho, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n(.*)", bruto, re.S)
    meta = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    corpo = m.group(2).strip()
    corpo = re.sub(r"^# .*\n+", "", corpo)  # o título vem dos metadados
    meta["slug"] = os.path.splitext(os.path.basename(caminho))[0]
    meta["corpo"] = corpo
    d = datetime.date.fromisoformat(meta["data"])
    meta["dataLonga"] = f"{d.day} de {MESES[d.month - 1]} de {d.year}"
    meta["minutos"] = max(1, round(len(re.findall(r"\w+", corpo)) / 200))
    return meta


def quadro_partilha(a):
    url = f'{SITE}/artigos/{a["slug"]}.html'
    texto = f'{a["titulo"]} · por {a["autor"]}\n{url}'
    thumb = a.get("thumb") or a.get("imagem")
    story = f'assets/artigos/{a["slug"]}-story.jpg'
    tem_story = os.path.exists(os.path.join(RAIZ, story))
    mini = (f'<div role="img" aria-label="{html.escape(a["titulo"])}" style="width:100%;aspect-ratio:16/9;border-radius:12px;'
            f'background:#23325a url(/{thumb}) center/cover no-repeat"></div>') if thumb else ""
    botao_story = f"""
          <button id="btnStory" data-story="/{story}" data-nome="{a["slug"]}.jpg" title="Compartilhar nos Stories / Status" aria-label="Compartilhar nos Stories do Instagram ou Status do WhatsApp" style="width:42px;height:42px;flex-shrink:0;border-radius:50%;border:1px solid #c9d3e3;background:#fff;color:#14213d;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.1 2.18a9.9 9.9 0 0 1 3.8 0"></path><path d="M17.6 3.71a9.95 9.95 0 0 1 2.69 2.7"></path><path d="M21.82 10.1a9.9 9.9 0 0 1 0 3.8"></path><path d="M20.29 17.6a9.95 9.95 0 0 1-2.7 2.69"></path><path d="M13.9 21.82a9.9 9.9 0 0 1-3.8 0"></path><path d="M6.4 20.29a9.95 9.95 0 0 1-2.69-2.7"></path><path d="M2.18 13.9a9.9 9.9 0 0 1 0-3.8"></path><path d="M3.71 6.4a9.95 9.95 0 0 1 2.7-2.69"></path><path d="M12 8v8"></path><path d="M8 12h8"></path></svg>
          </button>""" if tem_story else ""
    return f"""
    <section style="margin-top:40px;background:#f3f6fb;border-radius:18px;padding:20px;display:flex;flex-direction:column;gap:12px;font-family:'Source Sans 3',sans-serif;max-width:460px">
      {mini}
      <div style="font-family:'EB Garamond',serif;font-size:21px;line-height:1.25">Este artigo tocou você?</div>
      <div style="font-size:13px;line-height:1.5;color:#5a6478">Leve este artigo a alguém.</div>
      <div style="display:flex;gap:8px;align-items:center">
        <a href="https://api.whatsapp.com/send?text={html.escape(quote(texto))}" target="_blank" rel="noopener" style="font-size:13px;font-weight:600;white-space:nowrap;background:#1f8a4c;color:#fff;border-radius:999px;padding:11px 18px;flex:1;display:flex;align-items:center;justify-content:center;gap:8px">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"></path></svg>Enviar pelo WhatsApp
        </a>{botao_story}
      </div>
      <div id="avisoCopiado" style="display:none;font-size:12px;line-height:1.45;color:#1f5f3a;background:#e6f3ea;border-radius:12px;padding:8px 12px">Link copiado! Nos Stories, use o adesivo “Link” e cole. No Status, cole na legenda.</div>
    </section>
    <script>
    (function(){{
      var b=document.getElementById('btnStory'); if(!b) return;
      var link={json.dumps(url)}, legenda={json.dumps(a["titulo"] + " · por " + a["autor"])}, t;
      b.addEventListener('click', async function(){{
        try {{ await navigator.clipboard.writeText(link); }} catch(e) {{}}
        var av=document.getElementById('avisoCopiado'); av.style.display='block'; clearTimeout(t); t=setTimeout(function(){{av.style.display='none';}},6000);
        try {{
          var blob=await (await fetch(b.dataset.story)).blob();
          var file=new File([blob], b.dataset.nome, {{type:'image/jpeg'}});
          if (navigator.canShare && navigator.canShare({{files:[file]}})) {{ await navigator.share({{files:[file], text: legenda+'\\n'+link}}); return; }}
          var u=URL.createObjectURL(blob), el=document.createElement('a'); el.href=u; el.download=file.name; document.body.appendChild(el); el.click(); el.remove(); setTimeout(function(){{URL.revokeObjectURL(u);}},2000);
        }} catch(e) {{}}
      }});
    }})();
    </script>
"""


def pagina_artigo(a):
    partes = re.split(r"\n(?=## Referências)", a["corpo"], maxsplit=1)
    texto = markdown.markdown(partes[0])
    if len(partes) > 1:
        texto += '<div class="refs">' + markdown.markdown(partes[1]) + "</div>"
    img = a.get("imagem")
    thumb = a.get("thumb") or img
    figura = (f'<figure style="margin:0 0 36px"><img src="/{img}" alt="{html.escape(a.get("legenda", a["titulo"]))}" '
              f'style="display:block;width:100%;max-width:560px;margin:0 auto;border-radius:16px">'
              f'<figcaption style="max-width:560px;margin:10px auto 0;font-family:\'Source Sans 3\',sans-serif;font-size:13px;line-height:1.45;color:#5a6478;text-align:center">'
              f'{html.escape(a.get("legenda", ""))}</figcaption></figure>') if img else ""
    head = HEAD.format(
        title=html.escape(f'{a["titulo"]} — Ide, anunciai!'), desc=html.escape(a["frase"]),
        ogtype="article", ogtitle=html.escape(a["titulo"]),
        ogimage=(f'<meta property="og:image" content="{SITE}/{thumb}">\n<meta property="og:image:type" content="image/jpeg">\n'
                 f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="675">\n' if thumb else ""),
        url=f'{SITE}/artigos/{a["slug"]}.html')
    corpo = f"""
  <section style="position:relative;background:#14213d;color:#f3efe8;overflow:hidden">
    <div style="position:absolute;inset:0;background:linear-gradient(0deg,rgba(14,24,48,0.96) 0%,rgba(20,33,61,0.72) 50%,rgba(20,33,61,0.2) 100%)"></div>
    <div style="position:relative;max-width:1120px;min-height:300px;margin:0 auto;padding:34px 20px 40px;display:flex;flex-direction:column;justify-content:flex-end;gap:12px">
      <div style="display:flex;gap:8px;font-family:'Source Sans 3',sans-serif;font-size:11px;color:#a7b0c4;flex-wrap:wrap">
        <a href="/index.html" style="color:#a7b0c4">Início</a><span>/</span><a href="/artigos.html" style="color:#a7b0c4">Artigos</a>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;font-family:'Source Sans 3',sans-serif;font-size:11px;font-weight:600;letter-spacing:0.08em">
        <span style="background:#8a2f2a;color:#fff;padding:5px 12px;border-radius:999px;white-space:nowrap">Artigo</span>
        <span style="background:rgba(255,255,255,0.14);color:#fff;padding:5px 12px;border-radius:999px;white-space:nowrap">{a["dataLonga"]} · {a["minutos"]} min de leitura</span>
      </div>
      <h1 style="margin:0;font-weight:500;font-size:clamp(32px,5vw,50px);line-height:1.05;letter-spacing:-0.01em;max-width:760px;text-wrap:balance;color:#f3efe8">{html.escape(a["titulo"])}</h1>
      <p style="margin:0;font-size:19px;line-height:1.45;font-style:italic;color:#c8cfdd;max-width:620px;text-align:justify;hyphens:auto">{html.escape(a["frase"])}</p>
      <span style="font-family:'Source Sans 3',sans-serif;font-size:13px;color:#d3d9e6">por {html.escape(a["autor"])}</span>
    </div>
  </section>

  <main style="flex:1;max-width:760px;width:100%;margin:0 auto;padding:44px 20px 60px">
    {figura}
    <article class="texto">
{texto}
    </article>
{quadro_partilha(a)}
    <a href="/artigos.html" style="display:inline-block;margin-top:28px;font-family:'Source Sans 3',sans-serif;font-size:13px;font-weight:600;color:#14213d;border:1.5px solid #14213d;padding:11px 22px;border-radius:999px">← Todos os artigos</a>
  </main>
"""
    return head + corpo + FOOT


def pagina_lista(artigos):
    head = HEAD.format(
        title="Artigos — Ide, anunciai!", desc="Artigos de formação católica do Ide, anunciai!",
        ogtype="website", ogtitle="Artigos — Ide, anunciai!", ogimage="", url=f"{SITE}/artigos.html")
    cartoes = []
    for a in artigos:
        img = a.get("thumb") or a.get("imagem")
        fundo = f"background:#23325a url(/{img}) center 40%/cover no-repeat" if img else "background:#23325a"
        cartoes.append(f"""      <a class="cartao" href="/artigos/{a['slug']}.html">
        <div class="img" role="img" style="width:150px;aspect-ratio:16/10;border-radius:12px;flex-shrink:0;{fundo}"></div>
        <span style="display:flex;flex-direction:column;gap:5px;min-width:0;flex:1">
          <span style="font-family:'Source Sans 3',sans-serif;font-size:11px;color:#5a6478">{a['dataLonga']} · {a['minutos']} min de leitura</span>
          <span style="font-size:23px;font-weight:500;line-height:1.15">{html.escape(a['titulo'])}</span>
          <span style="font-size:16px;line-height:1.4;font-style:italic;color:#5a6478;text-align:justify;hyphens:auto">{html.escape(a['frase'])}</span>
        </span>
      </a>""")
    corpo = f"""
  <main style="flex:1;max-width:880px;width:100%;margin:0 auto;padding:40px 20px 56px;display:flex;flex-direction:column;gap:22px">
    <div style="display:flex;flex-direction:column;gap:6px">
      <div style="display:flex;gap:8px;font-family:'Source Sans 3',sans-serif;font-size:11px;color:#5a6478"><a href="/index.html" style="color:#5a6478">Início</a><span>/</span><span>Artigos</span></div>
      <h1 style="margin:0;font-weight:500;font-size:clamp(30px,4.5vw,40px);line-height:1.1">Artigos</h1>
      <p style="margin:0;font-family:'Source Sans 3',sans-serif;font-size:13px;color:#5a6478">{len(artigos)} {'artigo publicado' if len(artigos) == 1 else 'artigos publicados'}</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:12px">
{chr(10).join(cartoes)}
    </div>
  </main>
"""
    return head + corpo + FOOT


artigos = sorted((ler(os.path.join(FONTES, f)) for f in os.listdir(FONTES) if f.endswith(".md")),
                 key=lambda a: a["data"], reverse=True)
for a in artigos:
    open(os.path.join(RAIZ, "artigos", a["slug"] + ".html"), "w", encoding="utf-8").write(pagina_artigo(a))
open(os.path.join(RAIZ, "artigos.html"), "w", encoding="utf-8").write(pagina_lista(artigos))
print(f"{len(artigos)} artigo(s) gerado(s)")
