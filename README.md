# Google Maps Contact Scraper - Perú

![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?logo=node.js&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-activo-brightgreen)

Herramienta para recolectar datos de contacto de negocios desde Google Maps. Diseñada para proyectos de logística que requieren identificar proveedores y colaboradores en múltiples categorías y distritos.

---

## ¿Qué extrae?

| Campo | Fuente |
|---|---|
| Nombre del negocio | Google Maps |
| Categoría | Configurada por el usuario (exacta) |
| Valoración | Google Maps |
| Dirección | Google Maps |
| Teléfono | Google Maps + Web del negocio |
| Correo electrónico | Web del negocio |
| WhatsApp | Web del negocio |
| Instagram | Web del negocio |
| Facebook | Web del negocio |
| TikTok | Web del negocio |
| URL de Maps | Google Maps |

---

## ¿Cómo funciona?

```
config.json (categorías × distritos)
        ↓
Google Maps → scroll infinito → lista de enlaces
        ↓
Pool persistente (4 páginas paralelas) → extrae fichas
        ↓
Fetch-first / Puppeteer fallback → web de cada negocio
        ↓
Detecta subpágina de contacto y "sobre nosotros" y las visita también
        ↓
Almacena en SQLite (contactos.db) → exporta a contactos.xlsx
        ↓
Reanudación automática: si se interrumpe, retoma donde quedó
```

---

## Instalación

**Requisitos:** Node.js 18 o superior

> **Nota:** Al ejecutar `npm install`, Puppeteer descargará Chromium (~300 MB) automáticamente.

```bash
# 1. Clona el repositorio
git clone https://github.com/C1FR4/maps-scraper.git

# 2. Instala las dependencias
cd maps-scraper
npm install

# 3. Ejecuta
npm start
```
> **Nota para Windows:** Si usas `npm start` desde el **Símbolo del sistema clásico (cmd.exe)** y presionas Ctrl+C, puede aparecer el mensaje `"¿Desea terminar el trabajo por lotes (S/N)?"`. Esto es comportamiento de Windows/npm, no del scraper. Recomendaciones:
> - Ejecuta con `node scraper.js` directamente para que el menú interactivo de pausa funcione correctamente.
> - O usa **PowerShell** o **Windows Terminal** en vez de cmd.exe — no tienen ese mensaje heredado.
> - Pase lo que pase, los datos ya recolectados están guardados en `contactos.db`. Siempre puedes recuperarlos con:
>   ```bash
>   node scraper.js --export
>   ```
>   Esto genera el Excel con todo lo recolectado hasta el momento sin volver a scrapear. Los términos ya completados se saltarán solos al reanudar.

---

## Configuración

### Categorías y distritos

El programa te pedirá ingresar **tus propias categorías y distritos** al iniciar.  
Escribe los valores separados por coma - puedes poner tantos como necesites:

```
?  Categorías a buscar [1/2]
   › Cafetería, Restaurante peruano, Tienda de ropa

?  Distritos a buscar [2/2]
   › Miraflores Lima, Barranco Lima, San Isidro Lima
```

Cada combinación de categoría × distrito genera una búsqueda en Google Maps.  
Por ejemplo, con 3 categorías y 3 distritos se ejecutarán 9 búsquedas.

> **Modo no interactivo** (sin prompts): `node scraper.js --categorias "Cafetería, Restaurante" --distritos "Miraflores, Barranco"` — salta la configuración interactiva y arranca directo.

### Parámetros adicionales (`config.json`)

Se pueden ajustar en `config.json` sin necesidad de editar categorías ni distritos:

| Parámetro | Descripción | Default |
|---|---|---|
| `archivoExcel` | Nombre del archivo de salida | `contactos.xlsx` |
| `maxResultadosPorBusqueda` | Negocios máximos por término de búsqueda | `50` |
| `visitarWebDelNegocio` | Enriquecer con datos de la web | `true` |
| `esperaMsEntreBusquedas` | Pausa entre búsquedas (ms) | `3000` |
| `umbralTextoUtil` | Mínimo de texto para considerar página válida | `400` |
| `concurrencia` | Cuántas webs visita en paralelo | `5` |
| `concurrenciaFichas` | Cuántas fichas de Maps extrae en paralelo | `4` |
| `palabrasContacto` | Palabras clave para detectar subpáginas de contacto | `[contacto, contactenos, ...]` |
| `palabrasLocalPlaceholder` | Frases en la parte local del correo a descartar | `[noreply, placeholder, dummy, ...]` |
| `dominiosPlaceholder` | Dominios completos a descartar como correo | `[example.com, test.com, ...]` |
| `agregadoresLinkInBio` | Dominios agregadores que no se scrapean | `[linktr.ee, beacons.ai, ...]` |

---

## Output

Genera `contactos.xlsx` con:

- 16 columnas: incluye Método (maps / maps+web)
- Encabezado azul oscuro con texto blanco, fila congelada
- Filas con colores alternos (blanco / azul claro)
- Filtros automáticos en todas las columnas
- Categoría exacta como la configuró el usuario
- Teléfonos normalizados (sin prefijo +51)
- Enlaces directos funcionales (WhatsApp, redes sociales)

---

## Características

- **Fetch-first**: intenta obtener la web con `fetch` (rápido); si la página requiere JS, cae automáticamente a Puppeteer.
- **Extracción paralela de fichas**: pool de 4 páginas de Puppeteer extrayendo fichas de Maps simultáneamente.
- **Pool persistente**: las páginas se crean una vez y se reúsan entre términos de búsqueda.
- **Reanudación automática**: si el proceso se interrumpe, al retomar salta los términos ya procesados (basado en SQLite).
- **Detección de bloqueo**: si Google detecta tráfico automatizado, espera 60s y reintenta una vez antes de fallar controladamente.
- **Extracción desde URL social**: si un negocio tiene Instagram/Facebook como su "sitio web" en Maps, el handle se extrae directamente.
- **Filtro de redes sociales**: descarta enlaces falsos de Facebook (login, share, recover, photo, l.php, messages, events, etc.) y WhatsApp sin número.
- **Filtro de correos basura**: descarta dominios de tracking (Sentry, Hotjar, Klaviyo, etc.) y extensiones de archivo.
- **Normalización de teléfonos**: elimina prefijo +51, 51 y 0 de números peruanos.
- **Pausas aleatorias**: agrega delays variables para simular comportamiento humano.
- **Sin API keys**: no requiere claves ni proxies pagados.
- **Exportación directa**: `node scraper.js --export` genera el Excel desde la BD sin volver a scrapear.
- **Manejo de Ctrl+C**: menú interactivo con opciones para continuar, terminar y exportar, o pausar (guarda progreso para reanudar después).

---

## Tiempo estimado

Para 30 términos (ej: 3 categorías × 10 distritos) y ~500 negocios:

| Fase | Por término |
|---|---|---|
| Maps scroll + enlaces | ~15s |
| Fichas en paralelo | ~20s |
| Enriquecimiento web | ~60–90s |
| **Total estimado** | **20–25 minutos** |

---

## Disclaimer

Este proyecto se proporciona exclusivamente con **fines educativos y de investigación**. El scraping automatizado de Google Maps puede violar sus [Términos de Servicio](https://policies.google.com/terms). 

El mantenedor de este repositorio **no se responsabiliza** por el uso que terceros hagan de esta herramienta. Úsala bajo tu propio criterio y responsabilidad.

---


