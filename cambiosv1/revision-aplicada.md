# Revisión aplicada a la web

Se revisaron `cambiosv1.md`, los comentarios del Word revisado, las imágenes adjuntas y la guía visual IPCC AR6 WGI 2022 facilitada. La guía se usa como referencia de diseño; sus instrucciones para publicar informes del IPCC no son requisitos de esta web.

## Identidad y legibilidad

- Se conserva el logo original, sin redibujarlo ni recolorearlo, en cabecera, portada y pie.
- El JPEG está en CMYK con perfil ICC. Su fondo convertido a sRGB es aproximadamente `#45bccc`; esta es la referencia turquesa usada en la interfaz, junto con amarillo y fondos claros. Se utilizan tonos oscuros para texto y botones.
- El turquesa y amarillo del logo no se emplean como líneas sobre blanco porque tienen menor contraste. El color de una estación identifica su ubicación, no calidad, riesgo ni cumplimiento normativo.
- La guía IPCC recomienda colores accesibles para gráficos de líneas (página impresa 9, página 11 del PDF) y evitar escalas arcoíris. La página 13 del PDF trata escalas para magnitudes continuas. La adaptación inicial de seis colores más una extensión se reemplazó por una selección de siete colores originales de Dark, de Paul Tol; la fuente y la justificación están en [el README](../README.md#paleta-de-estaciones).

## Clave de estaciones

| Estación | Color | Símbolo | Trazo |
| --- | --- | --- | --- |
| Canelo · Maipo | `#117788` | Triángulo | Continuo |
| Guayacán · Maipo | `#775500` | Triángulo | Guiones |
| San Gabriel · Maipo | `#882288` | Triángulo | Punteado |
| Guayacán · Colorado | `#cc4466` | Círculo | Guion y punto |
| San Gabriel · Yeso | `#4477bb` | Círculo | Guiones largos |
| Baños Morales · Volcán | `#228833` | Círculo | Guiones cortos |
| Baños Morales · Estero | `#444444` | Círculo | Punto y guion largo |

Se conservan los valores originales de una única paleta. El petróleo y el ocre
acompañan al turquesa y amarillo del logo sobre fondo blanco. Los siete colores
superan 4,5:1 frente a blanco (mínimo calculado 4,53:1). Esto comprueba contraste,
no garantiza distinguir todos los pares con cualquier tipo de daltonismo:
cada estación conserva además su trazo y las del Maipo comparten triángulo.
Los nombres acompañan las claves en filtros, resúmenes y lista del mapa.
Los marcadores del mapa comparten color y símbolo con los gráficos y tienen
borde blanco; el contraste calculado sobre blanco no se extrapola al mapa.

## Cambios funcionales y contenido

La revisión documental completa, incluidos los requisitos aún pendientes, está
en [cambiosv1.md](cambiosv1.md). Esta lista de cambios aplicados no significa que
se hayan completado todos los requisitos del Word.

- El disclaimer está aplicado parcialmente: el aviso «Sobre los datos» resume el texto del Word. Falta incluir el contexto de hora, el esfuerzo de precisión y la intención de seguir protocolos de datos abiertos de UNESCO, además de hacerlo accesible junto a la descarga. CSV y JSON descargan todos los registros, sin filtros; la descarga por sitio sigue pendiente.
- También siguen pendientes el formulario de contacto, los puntos de encuentro y la línea de tiempo del mapa (actualmente hay un selector de año hídrico). El video de Vimeo requiere la URL que no se incluyó en el Word.
- Se corrige un selector inexistente que detenía la carga de los filtros y de las secciones siguientes.
- Inicialmente se muestran las tres estaciones del Maipo. Se pueden combinar los grupos Río Maipo (3), Colorado y Yeso (2) y Volcán y Estero Morales (2), o mostrar todas juntas. Las casillas individuales permiten afinar la selección; los grupos indican selección parcial y se muestra un contador de estaciones visibles. Se mantienen Todas, Solo río Maipo y Ninguna.
- Se cambia El Manzano a Guayacán en las hojas del Excel, los datos generados y las etiquetas públicas. Las hojas usan `Guayacan_` y los identificadores `guayacan-` para mantener rutas sencillas. Se conserva cada valor de medición y el resto del contenido del XLSX.
- Las galerías mensuales publicadas se limitan a Guayacán, San Gabriel y Baños Morales. Las fuentes de Canelo, San Alfonso y Puente Alto se conservan, pero no se copian al sitio.
- Otros contiene los resúmenes disponibles, incluido el de Guayacán hasta noviembre de 2026 extraído del Word. Se conservan intactas las imágenes históricas, que pueden contener el nombre anterior dentro de la propia fotografía.
- Las dos fotos individuales de Guayacán anunciadas en el mensaje no aparecen como adjuntos independientes. El resumen recibido sí incluye octubre y noviembre; faltan los originales individuales. No se recibieron nuevos resúmenes independientes de San Gabriel y Baños Morales: se mantienen los disponibles.
- Se incorporan las imágenes de instrumentos y del equipo; se usa la versión de mayor resolución de la foto de marzo de 2025.
- Si una foto no carga, se retira su tarjeta completa y la galería se reordena sin huecos. El contador se actualiza y las fotos fallidas no reaparecen al cambiar de sector durante esa visita. Las fotos del proyecto también se omiten si fallan.
- La conexión con KoboCollect queda para la siguiente etapa.

## Verificación

Revisión de paleta: contraste calculado para los siete colores (4,53:1 a 9,74:1
sobre blanco), correspondencia con los siete identificadores y siete trazos únicos.
Comprobación en Chromium de cinco gráficos, quince series iniciales del Maipo y
siete marcadores del mapa. Inspección visual de la
[muestra de colores y simulaciones](paleta-estaciones.svg). Las simulaciones
aproximadas muestran tonos cercanos en algunos pares; se mantienen los trazos,
símbolos y nombres como claves adicionales.

Verificación previa de la implementación general:

Generación correcta de siete estaciones, 394 mediciones y 163 imágenes. Comparación del XLSX con el original: únicamente cambia `xl/workbook.xml`, por los dos nombres de hojas. Comprobaciones en Chrome: cinco años hídricos, siete filtros, triángulos del Maipo, selección individual y rápida, selección vacía, los nueve parámetros, resumen del mapa, filtro y visor de fotos, menú móvil, ajuste a 390 px y carga de imágenes. Inspección visual de la portada a 1440 px. Sin publicación remota ni conexión a servicios externos.
