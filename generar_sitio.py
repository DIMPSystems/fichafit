"""
Generador del sitio de fichas por máquina.

Lee data/maquinas.json (la lista de máquinas del gimnasio, con qué músculos
trabaja cada una, el video y los pasos de uso) y arma automáticamente una
carpeta por máquina dentro de docs/, lista para subir a GitHub y activar
GitHub Pages. No hace falta tocar HTML a mano: agregar o corregir una
máquina es solo editar el JSON y volver a correr este script.

Uso:
    python3 generar_sitio.py
"""
import json
import re
import shutil
import unicodedata
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

RAIZ = Path(__file__).parent
DATA_FILE = RAIZ / "data" / "maquinas.json"
ASSETS_DIR = RAIZ / "assets"
TEMPLATES_DIR = RAIZ / "templates"
SALIDA_DIR = RAIZ / "docs"

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


def main():
    if SALIDA_DIR.exists():
        shutil.rmtree(SALIDA_DIR)
    SALIDA_DIR.mkdir(parents=True)

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

    # Página de inicio simple, solo para probar el sitio de punta a punta
    # (no es lo que ve el socio, que llega directo a la ficha de su máquina
    # escaneando el QR).
    filas = "\n".join(
        f'<li><a href="maquinas/{m["slug"]}/">{m["nombre"]}</a></li>' for m in indice
    )
    (SALIDA_DIR / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{gimnasio_nombre} · Fichas de máquinas</title></head>
<body style="font-family:sans-serif;max-width:480px;margin:40px auto;padding:0 20px;">
<h1>{gimnasio_nombre}</h1>
<p>Fichas de uso por máquina (de prueba — el socio entra directo por QR):</p>
<ul>{filas}</ul>
</body></html>""",
        encoding="utf-8",
    )

    print(f"\nListo: {len(indice)} máquina(s) generada(s) en docs/")


if __name__ == "__main__":
    main()
