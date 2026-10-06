# codex-pets

Mascotas personalizadas en formato **`.codex-pet`** para el IDE Orca (y cualquier app que entienda el mismo formato). Cada mascota reacciona a lo que hacen tus agentes: trabaja cuando ellos trabajan, espera cuando necesitan input, revisa cuando terminan y entra en pánico cuando algo falla.

| Barbaroot HD | Barbaroot | Pikorca |
|:---:|:---:|:---:|
| ![Barbaroot HD](docs/previews/barbaroot-hd.gif) | ![Barbaroot](docs/previews/barbaroot.gif) | ![Pikorca](docs/previews/pikorca.gif) |
| Hacker hipster calvo, barba negra con canas, franela y café. Ilustración generada con IA. | El mismo hacker en pixel art clásico de 48×52 dibujado por código. | Orca SRE de guardia con auriculares, lupa para las reviews y timón de Helm. |

## Instalación en Orca

1. Descarga la carpeta de la mascota que quieras de [`pets/`](pets/). Por ejemplo, `pets/barbaroot-hd.codex-pet/` (necesitas los dos ficheros: `pet.json` y `spritesheet.webp`).
2. En Orca, abre el **Pet menu** desde la barra de estado inferior.
3. Elige **Import .codex-pet bundle…** y selecciona la carpeta `*.codex-pet`.
4. Selecciónala en **Choose pet**.

> `Upload your own…` es para una imagen suelta (PNG, GIF, WebP, SVG…) sin animaciones por estado. Para estas mascotas usa siempre la importación de bundle.

## Formato `.codex-pet`

Un bundle es una carpeta con un manifiesto y una hoja de sprites:

```
mi-mascota.codex-pet/
├── pet.json
└── spritesheet.webp   # también PNG, APNG, JPG o GIF
```

Cada **fila** de la hoja es una animación y cada **columna** un frame. Si `pet.json` no declara `frame` ni `animations`, Orca asume frames de **192×208** en una rejilla de **8×9** con estas filas:

| Fila | Animación | Cuándo se muestra | Frames |
|---:|---|---|---:|
| 0 | `idle` | En reposo | 6 |
| 1 | `running-right` | Al arrastrarla a la derecha | 8 |
| 2 | `running-left` | Al arrastrarla a la izquierda | 8 |
| 3 | `waving` | Saludo | 4 |
| 4 | `jumping` | Al pasar el ratón por encima | 5 |
| 5 | `failed` | Error | 8 |
| 6 | `waiting` | Un agente está bloqueado o esperando input | 6 |
| 7 | `running` | Un agente está trabajando | 6 |
| 8 | `review` | Un agente ha terminado y hay algo que revisar | 6 |

Manifiesto completo (todos los campos son opcionales):

```json
{
  "id": "mi-mascota",
  "displayName": "Mi Mascota",
  "description": "...",
  "spritesheetPath": "spritesheet.webp",
  "frame": { "width": 256, "height": 320 },
  "fps": 8,
  "defaultAnimation": "idle",
  "animations": {
    "idle": { "row": 0, "frames": 6, "frameDurationsMs": [1680, 660, 660, 840, 840, 1920] }
  }
}
```

Reglas que valida Orca al importar:

- La hoja tiene que ser un múltiplo exacto del tamaño de frame.
- Ninguna animación puede tener más frames que columnas tiene la hoja.
- `frameDurationsMs`, si se indica, debe tener tantos valores como frames.
- El frame no puede superar 1024 px por lado, la hoja 64 MB y `pet.json` 64 KB.

## Regenerar o crear mascotas

Los generadores están en [`generators/`](generators/) y solo necesitan [Pillow](https://pypi.org/project/pillow/):

```bash
python -m venv .venv && .venv/bin/pip install pillow

# Pixel art dibujado por código
.venv/bin/python generators/pikorca.py   pets/pikorca.codex-pet   /tmp/pikorca.png
.venv/bin/python generators/barbaroot.py pets/barbaroot.codex-pet /tmp/barbaroot.png

# Versión HD a partir de las poses ilustradas (generators/barbaroot-hd/poses/)
.venv/bin/python generators/barbaroot-hd/build.py pets/barbaroot-hd.codex-pet /tmp/barbaroot-hd.png

# Vistas previas del README
.venv/bin/python generators/preview.py pets/barbaroot-hd.codex-pet docs/previews/barbaroot-hd
```

Barbaroot HD sigue este proceso:

1. Se genera **una pose por estado** con un modelo de imagen (aquí Nano Banana Pro en [Magnific](https://www.magnific.com)), usando la primera pose como referencia para mantener al personaje.
2. `build.py` recorta el fondo, escala todas las poses por igual y las anima: rebote, respiración, temblores y saltos.
3. Encima añade efectos en pixel art: vapor del café, bits, bocadillos, ✅, "!" y corazones.

## Licencia

[MIT](LICENSE)
