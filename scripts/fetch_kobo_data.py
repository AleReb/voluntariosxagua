#!/usr/bin/env python3
"""Download Kobo submissions to a local directory, never the public website."""

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

SERVER = "https://eu.kobotoolbox.org"
ASSET = "aMh8DJzqhNkKhKNt3GDSiS"
OUTPUT = Path(__file__).resolve().parents[1] / ".kobo"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download(token, opener=None):
    opener = opener or build_opener(NoRedirect())
    endpoint = f"{SERVER}/api/v2/assets/{ASSET}/data/"
    url = endpoint + "?format=json&limit=1000"
    seen = set()
    records = []
    while url:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.netloc != "eu.kobotoolbox.org"
                or parsed.path != urlsplit(endpoint).path):
            raise ValueError("Kobo devolvió una URL de paginación no permitida.")
        if url in seen:
            raise ValueError("Kobo repitió una página; se detuvo la descarga.")
        seen.add(url)
        request = Request(url, headers={
            "Authorization": f"Token {token}", "Accept": "application/json",
        })
        with opener.open(request, timeout=90) as response:
            page = json.load(response)
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            raise ValueError("La respuesta de Kobo no contiene una lista de registros.")
        if not all(isinstance(record, dict) for record in page["results"]):
            raise ValueError("La respuesta de Kobo contiene registros inválidos.")
        records.extend(page["results"])
        following = page.get("next")
        if following is not None and not isinstance(following, str):
            raise ValueError("La paginación de Kobo no es válida.")
        url = urljoin(url, following) if following else None
    return records


def main():
    token = os.environ.get("KOBO_API_TOKEN", "").strip()
    if not token:
        sys.exit("Falta el secreto KOBO_API_TOKEN.")
    try:
        records = download(token)
    except HTTPError as error:
        hints = {
            401: "Revisa o regenera la API key.",
            403: "Revisa el permiso Ver envíos del proyecto compartido.",
            404: "Revisa el proyecto y el acceso de tu cuenta.",
        }
        sys.exit(f"Kobo respondió HTTP {error.code}. {hints.get(error.code, 'Reintenta la ejecución. No se generó un respaldo nuevo.')}")
    except (URLError, TimeoutError, ValueError):
        sys.exit("No se pudo completar la descarga de Kobo. No se generó un respaldo nuevo.")
    OUTPUT.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = {"asset": ASSET, "server": SERVER, "count": len(records), "results": records}
    temporary = OUTPUT / "submissions.json.tmp"
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT / "submissions.json")
    print(f"Descarga completa: {len(records)} registros. No se publicaron datos en la web.")


if __name__ == "__main__":
    main()
