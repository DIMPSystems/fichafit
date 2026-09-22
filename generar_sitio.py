"""
Generador del sitio de fichas por máquina.

Lee data/maquinas.json (la lista de máquinas del gimnasio, con qué músculos
trabaja cada una, el video y los pasos de uso) y arma automáticamente una
carpeta por máquina dentro de docs/, lista para subir a GitHub y activar
GitHub Pages. También genera, para cada máquina, un cartel PNG listo para
imprimir con su código QR (apunta a la ficha de esa máquina) dentro de qr/.
No hace falta tocar HTML a mano: agregar o corregir una máquina es solo
editar el JSON y volver a correr este script.

Uso:
    python3 generar_sitio.py
"""
import json
import re
import shutil
import unicodedata
from pathlib import Path

import qrcode
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).parent
DATA_FILE = RAIZ / "data" / "maquinas.json"
ASSETS_DIR = RAIZ / "assets"
TEMPLATES_DIR = RAIZ / "templates"
SALIDA_DIR = RAIZ / "docs"
QR_DIR = RAIZ / "qr"

# Sitio publicado en GitHub Pages. Cuando el gym real tenga su propio
# dominio (o el repo pase a ser uno por cliente), solo hay que cambiar
# esta constante y volver a correr el script: todos los QR se regeneran
# apuntando a la URL nueva.
BASE_URL_SITIO = "https://dimpsystems.github.io/fichafit"

# Tipografías para el cartel del QR (DejaVu viene instalada en el sistema).
FUENTE_DIR = Path("/usr/share/fonts/truetype/dejavu")
FUENTE_TITULO = FUENTE_DIR / "DejaVuSans-Bold.ttf"
FUENTE_TEXTO = FUENTE_DIR / "DejaVuSans.ttf"

COLOR_PRINCIPAL = (175, 9, 48)      # var(--principal) del sitio
COLOR_GRIS = (90, 90, 90)           # var(--gris)
COLOR_NEGRO = (23, 23, 26)          # var(--negro)

# Color por nivel de participación del músculo en el ejercicio (el trazo
# clarito entre piezas se mantiene siempre, incluso pintado, para que se
# sigan viendo las líneas de separación de cada músculo).
NIVELES = {
    "principal": "var(--principal)",
    "secundario": "var(--secundario)",
    "terciario": "var(--terciario)",
}


def slugify(texto):
    """'Prensa de Piernas' -> 'prensa-de-piernas', para que cada máquina
    tenga una URL prolija (y estable, para que el QR no se rompa si se
    corrige el nombre después)."""
    sin_acentos = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", sin_acentos).strip("-").lower()
    return slug


def armar_estilo_musculos(musculos):
    """Genera el bloque de CSS que resalta, para ESTA máquina puntual, solo
    los músculos que trabaja (el diagrama SVG es el mismo archivo siempre;
    lo único que cambia de página a página es qué músculos se pintan)."""
    lineas = []
    for musculo_id, nivel in musculos.items():
        color = NIVELES.get(nivel)
        if not color:
            print(f"  ! nivel desconocido '{nivel}' para '{musculo_id}' (uso: principal/secundario/terciario)")
            continue
        lineas.append(f'[data-musculo="{musculo_id}"] {{ fill: {color}; }}')
    return "\n".join(lineas)


def _texto_centrado(draw, y, texto, fuente, color, ancho_lienzo):
    """Dibuja una línea de texto centrada horizontalmente y devuelve el alto
    que ocupó, para poder apilar líneas una debajo de la otra."""
    caja = draw.textbbox((0, 0), texto, font=fuente)
    ancho_texto = caja[2] - caja[0]
    alto_texto = caja[3] - caja[1]
    x = (ancho_lienzo - ancho_texto) / 2
    draw.text((x, y), texto, font=fuente, fill=color, anchor=None)
    return alto_texto


def generar_qr(gimnasio_nombre, maquina, slug):
    """Arma un cartel PNG listo para imprimir: nombre del gimnasio, nombre
    de la máquina y el código QR que lleva directo a la ficha de esa
    máquina en el sitio publicado."""
    url = f"{BASE_URL_SITIO}/maquinas/{slug}/"

    qr = qrcode.QRCode(border=2, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color=COLOR_NEGRO, back_color="white").convert("RGB")

    ancho, alto = 1200, 1320
    cartel = Image.new("RGB", (ancho, alto), "white")
    draw = ImageDraw.Draw(cartel)

    fuente_gym = ImageFont.truetype(str(FUENTE_TEXTO), 34)
    fuente_maquina = ImageFont.truetype(str(FUENTE_TITULO), 56)
    fuente_caption = ImageFont.truetype(str(FUENTE_TEXTO), 30)

    y = 70
    y += _texto_centrado(draw, y, gimnasio_nombre.upper(), fuente_gym, COLOR_PRINCIPAL, ancho) + 24

    # El nombre de la máquina puede no entrar en una sola línea: lo partimos
    # en hasta 2 líneas por palabras.
    palabras = maquina["nombre"].split()
    lineas_nombre, actual = [], ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        if draw.textbbox((0, 0), prueba, font=fuente_maquina)[2] > ancho - 100 and actual:
            lineas_nombre.append(actual)
            actual = palabra
        else:
            actual = prueba
    lineas_nombre.append(actual)
    for linea in lineas_nombre:
        y += _texto_centrado(draw, y, linea, fuente_maquina, COLOR_NEGRO, ancho) + 12

    y += 20
    draw.line([(ancho / 2 - 60, y), (ancho / 2 + 60, y)], fill=COLOR_PRINCIPAL, width=4)
    y += 40

    qr_lado = 820
    img_qr = img_qr.resize((qr_lado, qr_lado))
    cartel.paste(img_qr, (int((ancho - qr_lado) / 2), int(y)))
    y += qr_lado + 36

    _texto_centrado(draw, y, "Escaneá para ver cómo usarla", fuente_caption, COLOR_GRIS, ancho)

    QR_DIR.mkdir(exist_ok=True)
    ruta = QR_DIR / f"{slug}.png"
    cartel.save(ruta)
    return ruta


def main():
    if SALIDA_DIR.exists():
        shutil.rmtree(SALIDA_DIR)
    SALIDA_DIR.mkdir(parents=True)

    if QR_DIR.exists():
        shutil.rmtree(QR_DIR)
    QR_DIR.mkdir(parents=True)

    # Copiamos los assets compartidos (CSS) una sola vez.
    (SALIDA_DIR / "assets").mkdir()
    shutil.copy(ASSETS_DIR / "style.css", SALIDA_DIR / "assets" / "style.css")

    diagrama_svg = (ASSETS_DIR / "diagrama-muscular.svg").read_text(encoding="utf-8")

    maquinas = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    gimnasio_nombre = maquinas.get("gimnasio", "Mi Gimnasio")
    lista_maquinas = maquinas.get("maquinas", [])

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)
    plantilla = env.get_template("maquina.html.jinja")

    indice = []
    for maquina in lista_maquinas:
        slug = maquina.get("slug") or slugify(maquina["nombre"])
        carpeta = SALIDA_DIR / "maquinas" / slug
        carpeta.mkdir(parents=True, exist_ok=True)

        html = plantilla.render(
            gimnasio_nombre=gimnasio_nombre,
            maquina=maquina,
            diagrama_svg=diagrama_svg,
            estilo_musculos=armar_estilo_musculos(maquina.get("musculos", {})),
            ruta_assets="../../assets/",
        )
        (carpeta / "index.html").write_text(html, encoding="utf-8")
        indice.append({"nombre": maquina["nombre"], "slug": slug})
        print(f"  ✓ maquinas/{slug}/index.html")

        generar_qr(gimnasio_nombre, maquina, slug)
        print(f"  ✓ qr/{slug}.png")

    # Página de inicio: no es lo que ve el socio en el uso normal (él llega
    # directo a la ficha de su máquina escaneando el QR), pero queda
    # prolija y con la marca del sitio por si alguien entra al dominio
    # directamente (por ejemplo, mostrándola en una reunión).
    filas = "\n".join(
        f'<li><a href="maquinas/{m["slug"]}/">{m["nombre"]}</a></li>' for m in indice
    )
    (SALIDA_DIR / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{gimnasio_nombre} · Fichas de máquinas</title>
<link rel="stylesheet" href="assets/style.css">
<style>
  .indice-maquinas {{ list-style: none; margin: 0; padding: 0 20px; }}
  .indice-maquinas li {{ border-bottom: 1px solid var(--borde); }}
  .indice-maquinas a {{
    display: block; padding: 16px 4px; color: var(--negro);
    text-decoration: none; font-size: 15px; font-weight: 600;
  }}
  .indice-maquinas a:after {{ content: "›"; float: right; color: var(--principal); font-weight: 700; }}
  .indice-intro {{ padding: 0 20px; color: var(--gris); font-size: 14px; line-height: 1.5; }}
</style>
</head>
<body>
<div class="contenedor">
  <header class="encabezado">
    <p class="marca">{gimnasio_nombre.upper()}</p>
    <h1>Fichas por máquina</h1>
  </header>
  <p class="indice-intro">Cada máquina del gimnasio tiene su propio cartel con código QR: escaneándolo, el socio entra directo a su ficha. Este índice es solo de referencia.</p>
  <ul class="indice-maquinas">{filas}</ul>
  <footer class="pie">
    <p class="nombre-gym">{gimnasio_nombre}</p>
    <p>Sistema de fichas por máquina · DIMP Systems</p>
  </footer>
</div>
</body></html>""",
        encoding="utf-8",
    )

    print(f"\nListo: {len(indice)} máquina(s) generada(s) en docs/")


if __name__ == "__main__":
    main()
