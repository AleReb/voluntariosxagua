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
mediante un generador local, sin depender de un servidor o base de datos.

Esta versión inicial implementa las cuatro secciones descritas abajo. Las
coordenadas del mapa son aproximadas y los valores son los de la planilla
disponible; revisa las decisiones pendientes antes de tratar la visualización
como una publicación validada.

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
`docs/` y están excluidos de Git; el archivo Excel y `fotos/` son las fuentes.
El generador omite HEIC y TIFF porque no todos los navegadores los muestran.

Para publicar, crea un repositorio en GitHub con estos archivos y sube la rama
`main` o `master`. El workflow
`.github/workflows/pages.yml` genera los datos y despliega únicamente `docs/`
con GitHub Pages al hacer push (también se puede ejecutar manualmente desde
Actions). En la configuración del repositorio, habilita **Settings → Pages →
Build and deployment → Source: GitHub Actions**. Los documentos originales y la
planilla no se publican como archivos descargables del sitio; sus mediciones sí
se incluyen en el CSV y JSON que ofrece la web.

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
   - La propuesta inicial contempla galerías para El Manzano, San Gabriel y
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
  parámetro debe incluirse en los gráficos y filtros del sitio.
- Cada registro debe conservar al menos la fecha, la estación y los valores
  medidos. Se mencionan fotos repetitivas para tres lugares.

La planilla `abril2022anov2026_VPA.xlsx` tiene siete hojas, que corresponden a
estos puntos:

| Sector | Río / punto según la planilla |
|---|---|
| Canelo | Maipo |
| El Manzano | Maipo |
| El Manzano | Colorado |
| San Gabriel | Maipo |
| San Gabriel | Yeso |
| Baños Morales | Estero |
| Baños Morales | Volcán |

El archivo se llama abril 2022–noviembre 2026, pero antes de publicar o comparar
los datos se deben revisar la cobertura real de cada hoja, las fechas, los valores
faltantes, las unidades y la consistencia de las mediciones.

## Descarga y uso responsable

El sitio debe dejar los datos mensuales descargables por punto. Las mediciones
son realizadas por voluntarios con instrumentos calibrados por ellos mismos;
buscan la mayor precisión posible con los recursos disponibles, pero los
instrumentos no están certificados por la DGA. Se propone seguir protocolos de
datos abiertos de UNESCO.

Quienes usen los datos o gráficos deben considerar el lugar, la fecha y hora de
medición y las condiciones climáticas recientes, y dar crédito a **Voluntarios
por el Agua**. Los valores de pH y conductividad mencionados en los documentos
son referencias a mostrar, no una evaluación regulatoria completa; las normas y
su fuente deben confirmarse antes de presentarlas como tales.

## Archivos y fuentes

- `docs/`: código de la web estática (HTML, CSS y JavaScript) y salida para
  publicación desde la carpeta `docs` de GitHub Pages.
- `scripts/build_site_data.py`: convierte la planilla XLSX a JSON y prepara
  copias web de las fotos.
- `.github/workflows/pages.yml`: publicación automática con GitHub Pages.
- `Sitio web Voluntarios por el Agua2026.docx`: descripción más reciente de las
  secciones, visualizaciones, datos, contenido del proyecto y coordenadas.
- `Base de Datos Voluntarios por el Agua2026.docx`: antecedentes sobre la pérdida
  del acceso a ArcGIS, la estructura de datos y la propuesta inicial.
- `abril2022anov2026_VPA.xlsx`: datos históricos en siete hojas.
- `antecedentes.txt`: mensaje con la idea general y las referencias de inspiración.
- `fotos/`: fotografías organizadas por carpetas. Además de los tres lugares
  prioritarios, hay carpetas para Canelo, Puente Alto y San Alfonso; confirmar
  cuáles deben aparecer en la primera versión.

## Decisiones pendientes antes de implementar

- **Coordenadas y mapa:** confirmar el sistema de referencia de las coordenadas
  UTM y validar las ubicaciones. En el documento hay una coordenada repetida para
  El Manzano en los ríos Maipo y Colorado, además de valores con formato ambiguo
  para Canelo y Baños Morales. También hay coordenadas geográficas de puntos de
  encuentro, que no necesariamente identifican cada estación de muestreo.
- **Estaciones visibles:** aclarar si el mapa y las series incluirán todas las
  siete estaciones, dado que un documento anterior dice explícitamente que el
  mapa sería sin San Alfonso y otro posterior especifica siete estaciones con
  nombres de ríos.
- **Ubicaciones en el mapa:** hasta recibir coordenadas confirmadas para cada
  punto de muestreo, el mapa agrupa las estaciones en ubicaciones de referencia
  por sector. No se deben interpretar como ubicaciones exactas.
- **Parámetros y normas:** resolver si se mostrará turbidez y documentar las
  unidades, límites, fuente y alcance de cada norma o referencia.
- **Años y gráficos:** confirmar el diseño final de las series. La lista define
  cinco años hasta 2026–2027, mientras que un boceto menciona seis paneles; conviene
  que la vista se adapte al historial disponible.
- **Actualización mensual:** acordar cómo se validan y publican los datos que
  llegan desde KoboCollect y quién los revisa antes de reemplazar o actualizar
  la planilla pública.
- **Fotos:** acordar el alcance de las galerías, cómo asociar fotos con estación
  y fecha, y el proceso manual inicial.
- **Contacto:** el documento propone un formulario al correo del equipo e
  Instagram `@voluntariosxelagua`; confirmar el canal público definitivo.
