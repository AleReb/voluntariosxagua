import copy
import unittest

from kobo_data import ASSET, merge, normalize


def submission(identifier=1, **fields):
    return {"_id": identifier, "_Cual_es_la_fecha": "2026-12-06",
            "Punto_de_medicion": "manzano_maipo", "_validation_status": {}, **fields}


def workbook(records=None):
    return {"source": "historico.xlsx", "stations": [{"id": "guayacan-maipo"}],
            "records": records or []}


class NormalizationTests(unittest.TestCase):
    def test_replicate_means_aliases_missing_values_and_zero(self):
        payload = normalize([submission(
            Temperatura1="10", Temperatura2="11", Temeratura3="12",
            Multiparameter_pH1="8,1", Multiparameter_pH2="8.3",
            Dureza_ppm="0", Alcalinidad_ppm="90",
        )])
        record = payload["records"][0]
        self.assertEqual(record["stationId"], "guayacan-maipo")
        self.assertEqual(record["values"]["waterTemp"], 11)
        self.assertEqual(record["values"]["ph"], 8.2)
        self.assertEqual(record["values"]["hardness"], 0)
        self.assertEqual(record["values"]["alkalinity"], 90)
        self.assertIsNone(record["values"]["tds"])
        self.assertEqual(record["samples"]["ph"], [8.1, 8.3, None])

    def test_private_fields_never_reach_snapshot(self):
        row = normalize([submission(_submitted_by="PRIVATE", Comentarios_extra="PRIVATE",
                                    _attachments=[{"url": "PRIVATE"}])])["records"][0]
        self.assertNotIn("PRIVATE", str(row))
        self.assertEqual(set(row), {"date", "stationId", "koboId", "validationStatus", "samples", "values"})

    def test_invalid_data_requires_manual_mapping_or_correction(self):
        for fields in [
            {"Punto_de_medicion": "new_station"}, {"_Cual_es_la_fecha": "bad-date"},
            {"pH1": "NaN"}, {"pH1": "inf"}, {"pH1": True},
            {"pH1": "7", "Multiparameter_pH1": "8"},
            {"_validation_status": {"uid": "new_status"}},
        ]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                normalize([submission(**fields)])

    def test_duplicate_submission_id_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize([submission(), submission()])

    def test_snapshot_is_independent_of_api_order(self):
        rows = [submission(2), submission(1)]
        self.assertEqual(normalize(rows), normalize(list(reversed(rows))))


class MergeTests(unittest.TestCase):
    def test_multiple_historical_rows_on_same_date_are_preserved(self):
        rows = [
            {"date": "2026-12-06", "stationId": "guayacan-maipo", "values": {"ph": 7}},
            {"date": "2026-12-06", "stationId": "guayacan-maipo", "values": {"ph": 8}},
        ]
        result = merge(workbook(copy.deepcopy(rows)), normalize([submission(pH1="9")]))
        self.assertEqual(result["records"], rows)
        self.assertEqual(result["integration"]["koboAdded"], 0)

    def test_preserves_curated_excel_record_including_missing_values(self):
        old = {"date": "2026-12-06", "stationId": "guayacan-maipo", "values": {"ph": None}}
        result = merge(workbook([copy.deepcopy(old)]), normalize([submission(pH1="8")]))
        self.assertEqual(result["records"], [old])
        self.assertEqual(result["integration"]["koboAdded"], 0)

    def test_new_date_is_added_and_latest_id_wins_without_duplicates(self):
        snapshot = normalize([submission(2, pH1="8"), submission(1, pH1="7")])
        result = merge(workbook(), snapshot)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["values"]["ph"], 8)
        self.assertEqual(result["integration"]["koboAdded"], 1)

    def test_rejected_or_on_hold_measurements_are_not_published(self):
        for status in ["validation_status_not_approved", "validation_status_on_hold"]:
            snapshot = normalize([submission(_validation_status={"uid": status})])
            self.assertEqual(merge(workbook(), snapshot)["records"], [])

    def test_approved_measurement_is_published(self):
        snapshot = normalize([submission(_validation_status={"uid": "validation_status_approved"})])
        self.assertEqual(len(merge(workbook(), snapshot)["records"]), 1)

    def test_wrong_asset_is_rejected(self):
        snapshot = normalize([])
        self.assertEqual(snapshot["asset"], ASSET)
        snapshot["asset"] = "other-project"
        with self.assertRaises(ValueError):
            merge(workbook(), snapshot)


if __name__ == "__main__":
    unittest.main()
