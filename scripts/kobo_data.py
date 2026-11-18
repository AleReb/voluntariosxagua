"""Explicit Kobo field mapping and deterministic merge with the curated workbook."""

import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KOBO_FILE = ROOT / "data/kobo/measurements.json"
ASSET = "aMh8DJzqhNkKhKNt3GDSiS"
SERVER = "https://eu.kobotoolbox.org"

STATIONS = {
    "canelo": "canelo-maipo",
    "manzano_maipo": "guayacan-maipo",
    "manzano_colorado": "guayacan-colorado",
    "san_gabriel_maipo": "san-gabriel-maipo",
    "san_gabriel_yeso": "san-gabriel-yeso",
    "ba_os_morales_volc_n": "banos-morales-volcan",
    "ba_os_morales_estero_morales": "banos-morales-estero",
}

# Each tuple lists aliases for a single replicate, including the first form version.
FIELDS = {
    "waterTemp": [("Temperatura1", "Multiparameter_Temperatura1"),
                  ("Temperatura2", "Multiparameter_Temperatura2"),
                  ("Temeratura3", "Multiparameter_Temeratura3")],
    "ph": [(f"pH{i}", f"Multiparameter_pH{i}") for i in range(1, 4)],
    "conductivity": [(f"Conductividad{i}", f"Multiparameter_Conductividad{i}") for i in range(1, 4)],
    "tds": [(f"TDS{i}", f"Multiparameter_TDS{i}") for i in range(1, 4)],
    "salinity": [(f"Salinidad{i}", f"Multiparameter_Salinidad{i}") for i in range(1, 4)],
    "orp": [(f"ORP{i}", f"Multiparameter_ORP{i}") for i in range(1, 4)],
    "turbidity": [(f"Turibidez_{i}", f"Turibidez_NTU_{i}") for i in range(1, 4)],
    "hardness": [("Dureza_ppm",)],
    "alkalinity": [("Alcalinidad_ppm",)],
}
VALIDATION = {"", "validation_status_approved", "validation_status_not_approved", "validation_status_on_hold"}


def number(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("Kobo contiene una medición booleana.")
    result = float(str(value).strip().replace(",", "."))
    if not math.isfinite(result):
        raise ValueError("Kobo contiene una medición no finita.")
    return result


def normalize(records):
    normalized = []
    seen = set()
    for row in records:
        identifier = int(row["_id"])
        if identifier in seen:
            raise ValueError("Kobo devolvió un identificador de envío duplicado.")
        seen.add(identifier)
        station = STATIONS.get(row["Punto_de_medicion"])
        if not station:
            raise ValueError("Hay un punto de Kobo sin mapear; revisa STATIONS.")
        measured = date.fromisoformat(row["_Cual_es_la_fecha"]).isoformat()
        status = row.get("_validation_status", {}).get("uid", "")
        if status not in VALIDATION:
            raise ValueError("Estado de validación de Kobo desconocido.")
        samples = {}
        for parameter, replicates in FIELDS.items():
            samples[parameter] = []
            for aliases in replicates:
                candidates = [number(row[key]) for key in aliases if row.get(key) not in (None, "")]
                if len(set(candidates)) > 1:
                    raise ValueError("Dos versiones de un campo de Kobo tienen valores distintos.")
                samples[parameter].append(candidates[0] if candidates else None)
        values = {}
        for parameter, readings in samples.items():
            available = [value for value in readings if value is not None]
            values[parameter] = round(sum(available) / len(available), 6) if available else None
        normalized.append({
            "koboId": identifier, "date": measured, "stationId": station,
            "validationStatus": status or "not_reviewed", "samples": samples, "values": values,
        })
    normalized.sort(key=lambda row: (row["date"], row["stationId"], row["koboId"]))
    return {"schemaVersion": 1, "asset": ASSET, "server": SERVER,
            "count": len(normalized), "records": normalized}


def save_snapshot(records, destination=KOBO_FILE):
    payload = normalize(records)  # Validate everything before changing the tracked snapshot.
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return payload


def merge(workbook, snapshot):
    if snapshot.get("schemaVersion") != 1 or snapshot.get("asset") != ASSET:
        raise ValueError("El respaldo de Kobo tiene un esquema o proyecto inesperado.")
    historical = workbook["records"]
    excel_keys = {(row["date"], row["stationId"]) for row in historical}
    records = {}
    eligible = [row for row in snapshot["records"]
                if row["validationStatus"] in {"not_reviewed", "validation_status_approved"}]
    known_stations = {station["id"] for station in workbook["stations"]}
    for row in sorted(eligible, key=lambda row: row["koboId"]):
        if row["stationId"] not in known_stations:
            raise ValueError("La estación de Kobo no existe en el catálogo de la web.")
        key = (row["date"], row["stationId"])
        if key not in excel_keys:
            records[key] = {"date": row["date"], "stationId": row["stationId"],
                            "values": row["values"], "source": "kobo", "koboId": row["koboId"]}
    added = len(records)
    workbook["source"] += " + data/kobo/measurements.json"
    workbook["integration"] = {
        "koboRecords": snapshot["count"], "koboEligible": len(eligible),
        "koboAdded": added, "overlapPolicy": "excel-priority",
    }
    workbook["records"] = sorted(historical + list(records.values()), key=lambda row: (row["date"], row["stationId"]))
    return workbook
