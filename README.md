# Voluntarios por el Agua

## Propósito

Este proyecto busca publicar un sitio web para consultar y descargar las mediciones
mensuales de calidad del agua que realizan voluntarios en ríos del Cajón del Maipo.
La idea es reemplazar la consulta de datos que antes se hacía en ArcGIS por una
herramienta pública, fácil de explorar y que el equipo pueda actualizar cada mes.
Se inspira en el sitio de salud del río Aconcagua y en la presentación de datos de
Aconcagua Aire.

Hay una primera versión estática del sitio en `docs/`. Está pensada para
publicarse con GitHub Pages y lee los datos de la planilla y las fotografías
mediante un generador local. GitHub Actions sincroniza las mediciones de Kobo y
publica el resultado estático, sin servidor de aplicación ni base de datos.

Esta versión inicial implementa las cuatro secciones descritas abajo. Las
coordenadas del mapa se convierten desde las UTM del documento suponiendo zona
19 sur y datum WGS 84; esa referencia y las ubicaciones requieren validación.
Los valores proceden de la planilla histórica y del respaldo normalizado de Kobo.

La versión indicada en el footer es **v1**. El pie incluye **Webmaster: Alejandro
Rebolledo**, con enlace de correo a [arebolledo@udd.cl](mailto:arebolledo@udd.cl).
Este correo corresponde al webmaster; el contacto del proyecto continúa en
Instagram. La etiqueta v1 es informativa y no cambia automáticamente al editar
el sitio. Los cambios de esta revisión están en el repositorio local; este
documento no acredita un despliegue remoto.

## Probar y publicar

Se requiere Python 3; no hay paquetes adicionales que instalar.

1. Desde la carpeta principal, genera los archivos que consume la web:

   ```sh
   python3 scripts/build_site_data.py
   ```

2. Inicia un servidor local:

   ```sh
   python3 -m http.server 8000 --directory docs
   ```

   Abre <http://localhost:8000>.

Los archivos de datos JSON y las copias de las fotos se generan dentro de
`docs/` y están excluidos de Git; el archivo Excel, `data/kobo/measurements.json`
y `fotos/` son las fuentes versionadas.
El generador omite HEIC y TIFF porque no todos los navegadores los muestran.

Para publicar, crea un repositorio en GitHub con estos archivos y sube la rama
`main` o `master`. El workflow
`.github/workflows/pages.yml` genera los datos y despliega únicamente `docs/`
con GitHub Pages al hacer push (también se puede ejecutar manualmente desde
Actions). En la configuración del repositorio, habilita **Settings → Pages →
Build and deployment → Source: GitHub Actions**. Los documentos originales y la
planilla no se publican como archivos descargables del sitio; sus mediciones sí
se incluyen en el CSV y JSON que ofrece la web.

## Integración automática con KoboToolbox

La web combina la planilla histórica con las mediciones descargadas del proyecto
compartido de Zoe. Los datos de Kobo quedan versionados en
[data/kobo/measurements.json](data/kobo/measurements.json), junto con un
[README de integración](data/kobo/README.md) que explica campos, estaciones,
lecturas, permisos, ejecución y reglas de combinación.

- El workflow [Kobo](.github/workflows/kobo.yml) descarga los registros cada día
  a las **10:23 UTC**, o manualmente desde **Run workflow**.
- Usa el secreto `KOBO_API_TOKEN`; la clave y la respuesta íntegra de la API no
  se guardan en Git. El respaldo versionado contiene solo mediciones e
  identificadores técnicos, sin usuarios, comentarios ni adjuntos.
- Las lecturas repetidas de Kobo se promedian. Si ya hay un registro de la misma
  estación y fecha en el Excel, se conserva el del Excel sin modificarlo.
- Después de verificar los datos, Actions guarda los cambios del JSON con un
  commit y llama a Pages para publicar la web desde el commit verificado.
- El respaldo inicial contiene **77 registros**, de enero a noviembre de 2026.
  Todos coinciden con fechas y estaciones del Excel: el total unificado sigue
  siendo **394 mediciones**, sin duplicar los envíos de Kobo. Las próximas combinaciones nuevas
  se incorporarán a gráficos, mapa, estadísticas y descargas.

La primera descarga autenticada se verificó en Actions. La nueva integración se
comprobó localmente con ese respaldo; requiere subir estos cambios y ejecutar el
workflow actualizado para verificar el guardado y despliegue automáticos.
El repositorio conserva la última copia normalizada y Git registra sus cambios;
los artifacts adicionales de Actions caducan a los siete días.

## Qué se quería construir

El sitio se organizaría en cuatro secciones:

1. **Series de tiempo (página principal)**
   - Mostrar por defecto las mediciones de temperatura del agua.
   - Permitir elegir uno de los parámetros y activar o quitar estaciones de la
     leyenda para comparar varios puntos o concentrarse en uno.
   - Organizar las series por año hídrico, de abril a marzo. Los años definidos
     son: 2022–2023, 2023–2024, 2024–2025, 2025–2026 y 2026–2027; se agregarían
     nuevos años a medida que lleguen datos.
   - Mostrar resúmenes de promedio, mínimo y máximo. Para pH y conductividad se
     indicaron como referencias preliminares pH 6,5–8,7 y conductividad menor
     que 1900 µS/cm.
   - Incluir un botón para descargar los datos.

2. **Mapa de estaciones**
   - Mostrar los siete puntos de monitoreo con colores y una leyenda.
   - Permitir seleccionar un parámetro y consultar sus mediciones y resumen
     (promedio, mínimo y máximo) al elegir un punto.
   - Se propuso una línea de tiempo para explorar cómo cambian los datos.

3. **Fotografías repetitivas**
   - Presentar las fotografías comparables tomadas periódicamente en un mismo
     lugar.
   - La propuesta inicial contempla galerías para Guayacán, San Gabriel y
     Baños Morales. La carga automática quedó para una etapa posterior; por ahora
     las fotos se entregarían manualmente.

4. **El proyecto**
   - Explicar el propósito de la iniciativa, el trabajo de ciencia ciudadana,
     los métodos e instrumentos, y cómo participar o colaborar.
   - Incluir contacto, Instagram, informe del primer año y videos.

## Monitoreo y datos

- Se mide una vez al mes, normalmente el primer domingo, en siete puntos de
  monitoreo de ríos del Cajón del Maipo. Los nuevos registros llegan a
  KoboCollect después de la jornada mensual.
- El año hídrico se cuenta de abril a marzo. El proyecto comenzó en abril de
  2022.
- Los parámetros descritos para el sitio son temperatura del agua, pH,
  conductividad, sólidos disueltos, salinidad, ORP, dureza y alcalinidad.
- La planilla disponible agrega también turbidez. Conviene acordar si este
  parámetro se mantendrá en la selección final; actualmente está disponible en
  los gráficos y filtros del sitio.
- Cada registro debe conservar al menos la fecha, la estación y los valores
  medidos. Se mencionan fotos repetitivas para tres lugares.

La planilla `abril2022anov2026_VPA.xlsx` tiene siete hojas, que corresponden a
estos puntos:

| Sector | Río / punto según la planilla |
|---|---|
| Canelo | Maipo |
| Guayacán | Maipo |
| Guayacán | Colorado |
| San Gabriel | Maipo |
| San Gabriel | Yeso |
| Baños Morales | Estero |
| Baños Morales | Volcán |

El archivo se llama abril 2022–noviembre 2026, pero antes de publicar o comparar
los datos se deben revisar la cobertura real de cada hoja, las fechas, los valores
faltantes, las unidades y la consistencia de las mediciones.

## Descarga y uso responsable

Actualmente los botones CSV y JSON descargan todos los registros, sin aplicar
los filtros visibles de estaciones o parámetros. La descarga por sitio
solicitada en el Word todavía está pendiente.

Las mediciones
son realizadas por voluntarios con instrumentos calibrados por ellos mismos;
buscan la mayor precisión posible con los recursos disponibles, pero los
instrumentos no están certificados por la DGA. Se propone seguir protocolos de
datos abiertos de UNESCO.

Quienes usen los datos o gráficos deben considerar el lugar, la fecha y hora de
medición y las condiciones climáticas recientes, y dar crédito a **Voluntarios
por el Agua**. Los valores de pH y conductividad mencionados en los documentos
son referencias a mostrar, no una evaluación regulatoria completa; las normas y
su fuente deben confirmarse antes de presentarlas como tales.

El aviso «Sobre los datos» de la web recoge parte de este contenido. Falta
completarlo con la hora como contexto de interpretación, el esfuerzo por obtener
la mayor precisión posible y la intención de seguir los protocolos de datos
abiertos de UNESCO. Esa intención no equivale a una certificación. También falta
hacer accesible el aviso junto a los botones de descarga; no se ha solicitado una
ventana de aceptación. El texto completo y su estado se registran en
[cambiosv1.md](cambiosv1/cambiosv1.md#disclaimer-y-descarga-de-datos).

## Archivos y fuentes

- `docs/`: código de la web estática (HTML, CSS y JavaScript) y salida para
  publicación desde la carpeta `docs` de GitHub Pages.
- `scripts/build_site_data.py`: convierte la planilla XLSX a JSON y prepara
  copias web de las fotos.
- `.github/workflows/pages.yml`: publicación automática con GitHub Pages.
- `.github/workflows/kobo.yml`: descarga diaria, commit de mediciones y publicación.
- `scripts/kobo_data.py`: mapeo de campos y unión con el Excel.
- `scripts/fetch_kobo_data.py`: descarga autenticada con paginación.
- `data/kobo/`: respaldo normalizado de mediciones y README de integración.
- `Sitio web Voluntarios por el Agua2026.docx`: descripción más reciente de las
  secciones, visualizaciones, datos, contenido del proyecto y coordenadas en la
  raíz. La copia revisada con comentarios está en `cambiosv1/`.
- [cambiosv1/cambiosv1.md](cambiosv1/cambiosv1.md): requisitos consolidados del
  Word y los mensajes originales, con estado aplicado, parcial o pendiente.
- [cambiosv1/revision-aplicada.md](cambiosv1/revision-aplicada.md): detalle de la
  implementación, criterios visuales y verificaciones previas.
- `Base de Datos Voluntarios por el Agua2026.docx`: antecedentes sobre la pérdida
  del acceso a ArcGIS, la estructura de datos y la propuesta inicial.
- `abril2022anov2026_VPA.xlsx`: datos históricos en siete hojas.
- `antecedentes.txt`: mensaje con la idea general y las referencias de inspiración.
- `fotos/`: fotografías organizadas por carpetas. Además de los tres lugares
  publicados, se conservan fuentes de Canelo, Puente Alto y San Alfonso que se
  excluyen de las galerías públicas.

## Pendientes y propuestas para la siguiente revisión

Prioridad propuesta: completar primero el aviso y aclarar las descargas;
después validar ubicaciones y referencias; finalmente ampliar las funciones de
contacto, navegación temporal y actualización. Estas propuestas no se consideran
implementadas.

- **Disclaimer y descargas:** incorporar el texto completo documentado, vincularlo
  desde los botones e indicar que la descarga actual contiene todos los registros.
  Agregar una opción explícita de descarga por sitio, conservando la descarga
  completa.
- **Coordenadas y mapa:** confirmar el sistema de referencia de las coordenadas
  UTM y validar las ubicaciones. En el documento hay una coordenada repetida para
  Guayacán en los ríos Maipo y Colorado, además de valores con formato ambiguo
  para Canelo y Baños Morales. También hay coordenadas geográficas de puntos de
  encuentro, que no necesariamente identifican cada estación de muestreo.
- **Puntos de encuentro:** incorporar los cuatro sectores con coordenadas y
  altitud después de validar la notación del Word. Se deben distinguir de los
  puntos de muestreo. Guayacán reemplaza a El Manzano también en esta sección.
- **Parámetros y normas:** confirmar si se mantiene turbidez y documentar las
  unidades, límites, fuente y alcance de cada norma o referencia.
- **Navegación temporal del mapa:** agregar la línea de tiempo solicitada para
  explorar mediciones por fecha. Actualmente se filtra por año hídrico mediante
  un selector. Los gráficos ya se adaptan a los años presentes en los registros;
  no se genera un panel vacío para 2027–2028.
- **Actualización mensual:** acordar cómo se validan y publican los datos que
  llegan desde KoboCollect y quién los revisa antes de reemplazar o actualizar
  la planilla pública. El workflow ya integra el respaldo normalizado y guarda
  sus cambios en Git; falta verificar la nueva ejecución remota y acordar la
  revisión científica de los registros sin validar.
- **Fotos:** las galerías incluyen Guayacán, San Gabriel, Baños Morales y resúmenes en Otros. Queda pendiente asociar cada foto con una fecha verificada y acordar la carga mensual.
- **Adjuntos faltantes:** recibir los originales de las dos nuevas fotos de
  Guayacán y los nuevos resúmenes independientes de San Gabriel y Baños Morales.
- **Contacto del proyecto:** implementar el formulario solicitado, dirigido a
  `zoefleming24@gmail.com`, y acordar su mecanismo de envío. Actualmente está
  disponible Instagram `@voluntariosxelagua`; el correo del footer es del webmaster.
- **Video de Vimeo:** obtener la URL del video mencionado desde el minuto 20.
  El informe del primer año y los dos videos de YouTube ya están enlazados.
- **Frecuencia de monitoreo:** precisar en el texto público que la jornada
  mensual normalmente se realiza el primer domingo, como indica el Word.


## Cambios aplicados en v1

Cambios aplicados en `docs/`, el generador y GitHub Actions:

- Logo original visible en cabecera, portada y pie; imágenes de instrumentos y del equipo.
- Guayacán reemplaza a El Manzano en nombres públicos, dos hojas de la planilla y carpeta de fotos. Los valores y el formato de la planilla se conservan.
- Siete estaciones con colores y trazos estables; triángulos para las tres del Maipo, círculos para las otras cuatro. La vista inicial muestra las tres del Maipo. Se pueden sumar los grupos Maipo, Colorado y Yeso, y Volcán y Estero Morales; las casillas y botones Todas / Solo río Maipo / Ninguna controlan gráficos y estadísticas.
- Fotografías repetitivas solo de Guayacán, San Gabriel y Baños Morales; resúmenes en Otros. Se conserva el material fuente de los demás sectores sin publicarlo.
- Se incorpora el resumen de Guayacán hasta noviembre de 2026 del Word revisado. Las dos fotos individuales nuevas mencionadas en el mensaje no vienen como archivos separados: aparecen en el resumen, no se reconstruyeron desde él. Los otros dos resúmenes disponibles siguen siendo los originales recibidos en `fotos/`.
- Disclaimer abreviado al final de Mediciones; CSV y JSON con todos los registros.
  La ampliación del aviso y la descarga por sitio siguen pendientes.
- Footer con webmaster Alejandro Rebolledo, correo clickeable
  `arebolledo@udd.cl` y etiqueta de versión v1, con ajuste para pantallas móviles.
- Integración de Kobo con el historial, respaldo de mediciones versionado y
  workflow para sincronizar, guardar y publicar. Detalles en
  [data/kobo/README.md](data/kobo/README.md).
- Documentación de cambios completada con los requisitos omitidos del Word y su
  estado real, conservando los mensajes originales.

Los criterios de diseño están documentados en [cambiosv1/revision-aplicada.md](cambiosv1/revision-aplicada.md).


## Paleta de estaciones

Se seleccionaron siete colores originales de **Dark, de Paul Tol**, como alternativa
adicional a las referencias de `cambiosv1/cambiosv1.md`:
[Paul Tol — Qualitative colour schemes, figura 6](https://sronpersonalpages.nl/~pault/#fig:scheme_dark).
Se usa una sola familia, sin oscurecer colores ni mezclar paletas.

El azul petróleo y el ocre acompañan al turquesa y amarillo del logo con tonos
legibles sobre blanco. Los tres puntos del Maipo usan petróleo, ocre y púrpura
para diferenciarlos también dentro del grupo. El logo conserva sus colores.

| Estación | Color | Símbolo | Trazo | Contraste sobre blanco |
| --- | --- | --- | --- | --- |
| Canelo · Maipo | Petróleo `#117788` | Triángulo | Continuo | 5,23:1 |
| Guayacán · Maipo | Ocre `#775500` | Triángulo | Guiones | 6,81:1 |
| San Gabriel · Maipo | Púrpura `#882288` | Triángulo | Punteado | 7,98:1 |
| Guayacán · Colorado | Rosa `#CC4466` | Círculo | Guion y punto | 4,58:1 |
| San Gabriel · Yeso | Azul `#4477BB` | Círculo | Guiones largos | 4,56:1 |
| Baños Morales · Volcán | Verde `#228833` | Círculo | Guiones cortos | 4,53:1 |
| Baños Morales · Estero | Gris `#444444` | Círculo | Punto y guion largo | 9,74:1 |

La fuente prioriza contraste sobre blanco y advierte una menor separación entre
algunos tonos con daltonismo y en escala de grises. No se garantiza accesibilidad
solo por color: se conservan trazos únicos, símbolos y nombres, además de los
filtros para comparar pocas series y las tablas de valores. El mapa usa los mismos
colores y símbolos, con borde blanco para separar los marcadores del fondo.
Los contrastes de la tabla se calcularon mediante luminancia relativa sRGB;
no miden la diferencia entre pares de colores ni el contraste sobre el mapa.

La [muestra de la paleta](cambiosv1/paleta-estaciones.svg) presenta los siete
colores y trazos junto con simulaciones aproximadas de protanopia, deuteranopia
y escala de grises. Las dos simulaciones de daltonismo siguen las fórmulas
publicadas por Tol. Permiten revisar las limitaciones; no certifican accesibilidad.

La guía IPCC sigue siendo referencia para evitar escalas arcoíris y distinguir
categorías de magnitudes. La tabla de líneas está en la **página 11 del PDF
(9 impresa)**; la página 13 (11 impresa) describe escalas secuenciales y divergentes.
La selección actual no se presenta como una paleta oficial del IPCC.
