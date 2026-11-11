#!/usr/bin/env python3
"""Prepare the static website data and browser-ready photo copies."""

import json
import posixpath
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "abril2022anov2026_VPA.xlsx"
SITE = ROOT / "docs"
DATA_DIR = SITE / "data"
PHOTO_SOURCE = ROOT / "fotos"
PHOTO_OUTPUT = SITE / "fotos"

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"main": MAIN_NS, "rel": REL_NS}

SHEET_STATIONS = {
    "Canelo_Maipo": ("canelo-maipo", "Canelo", "Maipo", -33.576468, -70.452054),
    "El Manzano_Maipo": ("manzano-maipo", "El Manzano", "Maipo", -33.601013, -70.359791),
    "El Manzano_Colorado": ("manzano-colorado", "El Manzano", "Colorado", -33.601013, -70.359791),
    "SanGab_Maipo": ("san-gabriel-maipo", "San Gabriel", "Maipo", -33.786392, -70.229894),
    "San Gab_Yeso": ("san-gabriel-yeso", "San Gabriel", "Yeso", -33.786392, -70.229894),
    "BM_estero": ("banos-morales-estero", "Baños Morales", "Estero", -33.826691, -70.064452),
    "BañosMorales_Volcán": ("banos-morales-volcan", "Baños Morales", "Volcán", -33.826691, -70.064452),
}

PARAMETERS = [
    {"id": "waterTemp", "label": "Temperatura del agua", "unit": "°C"},
    {"id": "ph", "label": "pH", "unit": ""},
    {"id": "conductivity", "label": "Conductividad", "unit": "µS/cm"},
    {"id": "tds", "label": "Sólidos disueltos", "unit": "ppm"},
    {"id": "salinity", "label": "Salinidad", "unit": "ppm"},
    {"id": "orp", "label": "ORP", "unit": "mV"},
    {"id": "hardness", "label": "Dureza", "unit": "ppm"},
    {"id": "alkalinity", "label": "Alcalinidad", "unit": ""},
    {"id": "turbidity", "label": "Turbidez", "unit": "NTU"},
]

# The worksheet columns follow the same order in every station sheet.
VALUE_COLUMNS = {
    "conductivity": 1,
    "hardness": 2,
    "ph": 3,
    "salinity": 4,
    "tds": 5,
    "waterTemp": 6,
    "orp": 7,
    "turbidity": 8,
    "alkalinity": 9,
}


def read_shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(part.text or "" for part in item.findall(".//main:t", NS))
        for item in root.findall("main:si", NS)
    ]


def cell_value(cell, shared_strings):
    value = cell.find("main:v", NS)
    if cell.attrib.get("t") == "inlineStr":
        return "".join(part.text or "" for part in cell.findall(".//main:t", NS))
    if value is None:
        return None
    if cell.attrib.get("t") == "s":
        return shared_strings[int(value.text)]
    return value.text


def column_index(reference):
    letters = "".join(character for character in reference if character.isalpha())
    index = 0
    for letter in letters:
        index = index * 26 + ord(letter.upper()) - ord("A") + 1
    return index - 1


def sheet_path(target):
    target = target.lstrip("/")
    if target.startswith("xl/"):
        return target
    return posixpath.normpath(posixpath.join("xl", target))


def parse_workbook():
    if not WORKBOOK.is_file():
        raise FileNotFoundError(f"No se encontró la planilla: {WORKBOOK}")

    records = []
    stations = []
    with zipfile.ZipFile(WORKBOOK) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in relationships.findall(f"{{{PKG_REL_NS}}}Relationship")
        }
        shared_strings = read_shared_strings(archive)
        found_sheets = set()

        for sheet in workbook.findall("main:sheets/main:sheet", NS):
            name = sheet.attrib["name"]
            if name not in SHEET_STATIONS:
                continue
            found_sheets.add(name)
            station_id, site, river, latitude, longitude = SHEET_STATIONS[name]
            stations.append({
                "id": station_id,
                "site": site,
                "river": river,
                "location": {"lat": latitude, "lon": longitude},
            })
            worksheet = ET.fromstring(archive.read(sheet_path(targets[sheet.attrib[f"{{{REL_NS}}}id"]])))
            rows = worksheet.findall("main:sheetData/main:row", NS)
            for row in rows:
                if int(row.attrib["r"]) < 3:
                    continue
                cells = {
                    column_index(cell.attrib["r"]): cell_value(cell, shared_strings)
                    for cell in row.findall("main:c", NS)
                }
                raw_date = cells.get(0)
                if raw_date in (None, ""):
                    continue
                try:
                    date = (datetime(1899, 12, 30) + timedelta(days=float(raw_date))).date().isoformat()
                except (TypeError, ValueError, OverflowError) as error:
                    raise ValueError(f"Fecha inválida en hoja {name}, fila {row.attrib['r']}: {raw_date}") from error
                values = {}
                for parameter, index in VALUE_COLUMNS.items():
                    raw_value = cells.get(index)
                    try:
                        values[parameter] = None if raw_value in (None, "") else float(raw_value)
                    except (TypeError, ValueError) as error:
                        raise ValueError(
                            f"Valor inválido para {parameter} en hoja {name}, fila {row.attrib['r']}: {raw_value}"
                        ) from error
                records.append({"date": date, "stationId": station_id, "values": values})

        missing = set(SHEET_STATIONS) - found_sheets
        if missing:
            raise ValueError(f"Faltan hojas esperadas en la planilla: {', '.join(sorted(missing))}")

    records.sort(key=lambda record: (record["date"], record["stationId"]))
    stations.sort(key=lambda station: station["id"])
    return {
        "source": WORKBOOK.name,
        "parameters": PARAMETERS,
        "stations": stations,
        "records": records,
    }


def build_photo_index():
    if not PHOTO_SOURCE.is_dir():
        raise FileNotFoundError(f"No se encontró la carpeta de fotografías: {PHOTO_SOURCE}")
    supported = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    if PHOTO_OUTPUT.exists():
        shutil.rmtree(PHOTO_OUTPUT)
    PHOTO_OUTPUT.mkdir(parents=True)

    photos = []
    skipped = []
    for image in sorted(PHOTO_SOURCE.rglob("*")):
        if not image.is_file():
            continue
        if image.suffix.lower() not in supported:
            skipped.append(image.relative_to(ROOT).as_posix())
            continue
        relative = image.relative_to(PHOTO_SOURCE)
        target = PHOTO_OUTPUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, target)
        photos.append({
            "location": relative.parts[0] if len(relative.parts) > 1 else "Otros",
            "filename": image.name,
            "path": (Path("fotos") / relative).as_posix(),
        })

    if skipped:
        print("Se omitieron formatos no compatibles con navegadores:", file=sys.stderr)
        for filename in skipped:
            print(f"  - {filename}", file=sys.stderr)
    return photos


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    measurements = parse_workbook()
    photos = build_photo_index()
    (DATA_DIR / "measurements.json").write_text(
        json.dumps(measurements, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (DATA_DIR / "photos.json").write_text(
        json.dumps(photos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Estaciones: {len(measurements['stations'])}; mediciones: {len(measurements['records'])}")
    print(f"Fotografías listas para la web: {len(photos)}")
    if measurements["records"]:
        print(f"Rango de fechas: {measurements['records'][0]['date']} a {measurements['records'][-1]['date']}")


if __name__ == "__main__":
    main()
