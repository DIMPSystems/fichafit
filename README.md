# FichaFit

Sitio de fichas por máquina para gimnasios: cada máquina tiene una página
propia (accesible vía código QR pegado en la máquina) con un video de uso,
un diagrama muscular interactivo que muestra qué músculos trabaja, los
pasos de uso y un consejo de seguridad.

Proyecto de [DIMP Systems](https://github.com/DIMPSystems).

## Cómo funciona

Nada de esto se edita a mano por máquina. Todo sale de un único archivo de
datos:

1. `data/maquinas.json` — la lista de máquinas del gimnasio: nombre,
   qué músculos trabaja cada una (`principal` / `secundario` / `terciario`),
   los pasos de uso y el consejo de seguridad.
2. `generar_sitio.py` — lee ese JSON y genera automáticamente una página
   HTML por máquina dentro de `docs/`, lista para publicarse con
   GitHub Pages.

Agregar o corregir una máquina es editar `data/maquinas.json` y volver a
correr:

```bash
python3 generar_sitio.py
```

## Estructura

- `assets/` — el diagrama muscular (SVG, reutilizado por todas las
  máquinas) y los estilos del sitio.
- `templates/` — la plantilla Jinja2 de la ficha de cada máquina.
- `data/` — los datos de las máquinas del gimnasio.
- `docs/` — el sitio ya generado (lo que sirve GitHub Pages).

## Créditos

El diagrama muscular usa datos de silueta corporal de la librería open
source `@musclemap/assets` (MIT License) — ver
[`THIRD-PARTY-LICENSES.md`](THIRD-PARTY-LICENSES.md).
