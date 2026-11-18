# Integración de KoboToolbox

Proyecto de Zoe: [Voluntarios por el Agua en Kobo](https://eu.kobotoolbox.org/#/forms/aMh8DJzqhNkKhKNt3GDSiS/summary).

Servidor: `https://eu.kobotoolbox.org`. UID: `aMh8DJzqhNkKhKNt3GDSiS`.
La autenticación usa el secreto de Actions `KOBO_API_TOKEN` y requiere permiso
**Ver envíos** sobre el proyecto compartido. La clave no se guarda en Git.

## Datos guardados en este repositorio

[measurements.json](measurements.json) es una copia normalizada de las mediciones
descargadas. Contiene identificador numérico del envío, fecha de medición,
estación, estado de validación, lecturas originales numéricas y valores resumidos.
Excluye usuarios, comentarios, coordenadas de dispositivos, nombres de archivos,
enlaces y archivos adjuntos. La copia íntegra recibida de la API queda solo en
`.kobo/submissions.json`, excluida de Git y de Pages.

El respaldo inicial procede de la ejecución de Actions `44232451037`: **77
registros**, siete estaciones, fechas del **4 de enero al 1 de noviembre de
2026**. Todos estaban sin revisión explícita en Kobo. Las 77 combinaciones de
estación y fecha ya existen en el Excel, por lo que esta integración inicial
conserva las **394 mediciones históricas** sin agregar duplicados.

El JSON representa la última descarga completa accesible para la cuenta, no un
acumulado de envíos eliminados. Cada cambio confirmado por Actions queda en el
historial de Git. Un cambio de permisos puede reducir los registros visibles;
una descarga exitosa no demuestra que la cuenta tenga acceso a todo el proyecto.

## Flujo automático

1. `.github/workflows/kobo.yml` corre diariamente a las **10:23 UTC** y permite
   ejecución manual. Siempre trabaja sobre la rama predeterminada.
2. `scripts/fetch_kobo_data.py` descarga todas las páginas de
   `/api/v2/assets/{uid}/data/`, con autenticación y sin seguir redirecciones ni
   enviar credenciales a otros dominios.
3. `scripts/kobo_data.py` valida y normaliza todos los registros antes de
   reemplazar `data/kobo/measurements.json`.
4. Se ejecutan las pruebas y se genera la web para comprobar la integración.
5. Si cambió el JSON, Actions crea un commit y lo sube a la rama predeterminada.
   Solo agrega ese archivo al commit. Si no cambió, no crea un commit vacío.
6. Se guarda además un artifact de las mediciones normalizadas durante siete días.
7. Se llama al workflow reutilizable `pages.yml` con el SHA exacto verificado;
   genera y publica la web desde ese commit, incluso si no hubo cambios de datos.

La llamada explícita a Pages evita depender de que el push del bot active otro
workflow: los pushes con `GITHUB_TOKEN` no activan workflows por `push`.
Referencia: [documentación de GitHub](https://docs.github.com/en/actions/concepts/security/github_token).

## Correspondencia de estaciones

| Valor de Kobo | Estación de la web |
| --- | --- |
| `canelo` | Canelo · Maipo |
| `manzano_maipo` | Guayacán · Maipo |
| `manzano_colorado` | Guayacán · Colorado |
| `san_gabriel_maipo` | San Gabriel · Maipo |
| `san_gabriel_yeso` | San Gabriel · Yeso |
| `ba_os_morales_volc_n` | Baños Morales · Volcán |
| `ba_os_morales_estero_morales` | Baños Morales · Estero |

La fecha se obtiene de `_Cual_es_la_fecha`, no de la fecha de envío a Kobo.
Un punto desconocido o una fecha inválida detienen la sincronización para que se
revise el mapeo, en vez de omitir la medición silenciosamente.

## Parámetros y lecturas

| Parámetro de la web | Campos de Kobo |
| --- | --- |
| Temperatura del agua | `Temperatura1`, `Temperatura2`, `Temeratura3` |
| pH | `pH1`, `pH2`, `pH3` |
| Conductividad | `Conductividad1` a `Conductividad3` |
| Sólidos disueltos | `TDS1` a `TDS3` |
| Salinidad | `Salinidad1` a `Salinidad3` |
| ORP | `ORP1` a `ORP3` |
| Turbidez | `Turibidez_1` a `Turibidez_3` |
| Dureza | `Dureza_ppm` |
| Alcalinidad | `Alcalinidad_ppm` |

Se soporta la primera versión del formulario con prefijo `Multiparameter_`, y
`Turibidez_NTU_1` a `Turibidez_NTU_3`. Se conserva la ortografía de los nombres
reales del formulario. Dos alias de la misma lectura con valores contradictorios
detienen la sincronización.

Para los parámetros repetidos se calcula la **media aritmética de las lecturas
disponibles**, redondeada a seis decimales; no se convierte un vacío en cero.
Los nueve parámetros mantienen las unidades del catálogo de la web; no hay
conversión de unidades. Se debe confirmar su correspondencia con el instrumento
si cambia el formulario. Dureza y alcalinidad usan su lectura única. Se conservan
los ceros, se admite coma decimal y se rechazan valores no numéricos o no finitos.

## Unión con el Excel histórico

`scripts/build_site_data.py` lee la planilla y el JSON versionado, sin pedir la
API key ni conectarse a Kobo durante la publicación.

- Clave de unión: **fecha de medición + identificador de estación**.
- Si la combinación existe en el Excel, se conserva íntegro su registro,
  incluidos los valores vacíos. El Excel se considera el historial curado.
  También se conservan sus filas repetidas: hay tres combinaciones de fecha y
  estación repetidas en Guayacán · Colorado entre octubre y diciembre de 2025,
  algunas con valores distintos. Su revisión queda pendiente; la integración
  no las elimina ni las reemplaza por Kobo.
- Las combinaciones nuevas se agregan desde Kobo. Si hay varios envíos elegibles
  para la misma combinación, se conserva el de mayor `_id`; es una regla técnica
  determinista que requiere revisión si se hacen varias jornadas en un mismo día.
- Se incluyen envíos aprobados y sin revisar. Los rechazados y en espera se
  conservan en el respaldo del repositorio, pero no se incorporan a la web.
  La ausencia de revisión no se presenta como aprobación científica.
- Cambiar o eliminar un envío en Kobo actualiza la copia normalizada; no modifica
  ni elimina un registro existente en el Excel.

El resultado unificado se genera en `docs/data/measurements.json`; lo utilizan
gráficos, estadísticas, mapa y descargas CSV/JSON del sitio. Ese archivo derivado
sigue excluido de Git. La web muestra una nota sobre las fuentes y la prioridad
del historial. Las fotografías continúan viniendo de `fotos/`.

## Activación y uso local

El secreto `KOBO_API_TOKEN` ya permitió la descarga inicial. Para habilitar esta
nueva integración, sube los cambios del código, datos y workflows a GitHub y
ejecuta **Actions → Rescatar datos de KoboToolbox → Run workflow**.

El workflow necesita `contents: write` para guardar los datos y los permisos
habituales de Pages para publicar. Si una regla de protección impide el push del
bot, la ejecución falla: configura un mecanismo permitido de escritura o de PR
para esa rama. Un push concurrente puede exigir repetir la ejecución; nunca se
usa force push.

Para reconstruir la web con los datos ya guardados, sin credenciales:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/build_site_data.py
python3 -m http.server 8000 --directory docs
```

Para rescatar datos nuevos localmente en Bash, sin escribir la clave en el historial:

```sh
read -rsp 'API key de Kobo: ' KOBO_API_TOKEN
export KOBO_API_TOKEN
python3 scripts/fetch_kobo_data.py
unset KOBO_API_TOKEN
python3 scripts/build_site_data.py
```

Revisa el diff de `data/kobo/measurements.json` antes de confirmarlo. Los errores
401 indican un problema con la clave; 403/404 pueden indicar permisos o proyecto
inaccesible. Los fallos de red o mapeo detienen el proceso sin publicar una nueva
versión. La configuración del secreto y los permisos se gestionan en GitHub;
ninguna credencial debe ponerse en HTML, JavaScript, README o archivos versionados.
