# Licencias de terceros

Este proyecto usa datos de silueta corporal y musculares (formas anatómicas
en SVG) adaptados de una librería open source. El código y la lógica del
sitio (generador, plantilla, estilos) son propios de DIMP Systems; lo único
tomado de afuera son las formas del cuerpo y los músculos.

## @musclemap/assets

- Paquete: `@musclemap/assets` (npm)
- Descripción del paquete: "Body diagrams for MuscleMap — segmented muscle
  SVG path data with semantic IDs and region viewBoxes."
- Licencia: MIT License

Se tomó el contorno del cuerpo (silueta base) y las ~19 regiones musculares
(frente y espalda, lado izquierdo autoría original y lado derecho generado
por espejo, como indica la propia librería) y se adaptaron a
`assets/diagrama-muscular.svg`, agrupándolas bajo los ids propios del
proyecto (`pecho`, `hombros`, `biceps`, `triceps`, `dorsales`, `trapecios`,
`romboides`, `cuadriceps`, `gluteos`, `isquiotibiales`, `aductores`,
`abductores`, etc. — ver `data-musculo` en el SVG). No se usó ningún
componente de UI de la librería, solo los datos de las siluetas (paths).

Copia del texto completo de la licencia MIT: https://opensource.org/license/mit/
