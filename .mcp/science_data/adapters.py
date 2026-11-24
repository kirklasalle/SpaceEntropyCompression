"""Bounded public API adapters for astronomy and high-energy physics metadata."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from shared.network_safety import safe_https_open, validate_public_https_url

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 20
EXOPLANET_ENDPOINT = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
INSPIRE_ENDPOINT = "https://inspirehep.net/api/literature"

EXOPLANET_COLUMNS = frozenset({
    "pl_name",
    "hostname",
    "discoverymethod",
    "disc_year",
    "sy_snum",
    "sy_pnum",
    "pl_orbper",
    "pl_rade",
    "pl_bmasse",
})

SOURCES = {
    "astronomy": [
        {
            "id": "nasa-exoplanet-archive",
            "name": "NASA Exoplanet Archive",
            "url": "https://exoplanetarchive.ipac.caltech.edu/",
            "api": EXOPLANET_ENDPOINT,
            "access": "public",
            "implemented": True,
            "scope": "bounded, read-only TAP queries to the confirmed-planet table",
        },
        {
            "id": "mast",
            "name": "Mikulski Archive for Space Telescopes",
            "url": "https://mast.stsci.edu/",
            "access": "public data only",
            "implemented": False,
            "scope": "released public products; exclusive-access products are excluded",
        },
        {
            "id": "gaia",
            "name": "ESA Gaia Archive",
            "url": "https://gea.esac.esa.int/archive/",
            "access": "public",
            "implemented": False,
            "scope": "future TAP adapter",
        },
    ],
    "hep_quantum": [
        {
            "id": "inspire-hep",
            "name": "INSPIRE-HEP",
            "url": "https://inspirehep.net/",
            "api": INSPIRE_ENDPOINT,
            "access": "public metadata",
            "implemented": True,
            "scope": "bounded literature metadata search; not experimental measurements",
        },
        {
            "id": "hepdata",
            "name": "HEPData",
            "url": "https://www.hepdata.net/",
            "access": "public records subject to record-level terms",
            "implemented": False,
            "scope": "adapter pending API and per-record rights validation",
        },
        {
            "id": "cern-open-data",
            "name": "CERN Open Data",
            "url": "https://opendata.cern.ch/",
            "access": "public releases",
            "implemented": False,
            "scope": "released datasets only; dataset-specific license and schema review",
        },
    ],
}


class ScienceDataError(ValueError):
    """A validation or upstream response error from a science-data adapter."""


def _read_json(
    url: str,
    opener: Optional[Callable[..., Any]] = None,
) -> tuple[Any, str]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "SpaceEntropyCompression-ScienceData/1.0",
        },
    )
    try:
        with safe_https_open(
            request, timeout=REQUEST_TIMEOUT_SECONDS, opener=opener
        ) as response:
            geturl = getattr(response, "geturl", None)
            if callable(geturl):
                final_url = geturl()
                if isinstance(final_url, str) and final_url:
                    validate_public_https_url(final_url, resolve_dns=(opener is None))
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except ScienceDataError:
        raise
    except ValueError as exc:
        raise ScienceDataError(str(exc)) from exc
    if len(body) > MAX_RESPONSE_BYTES:
        raise ScienceDataError("upstream_response_too_large")
    try:
        data = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScienceDataError("upstream_response_invalid_json") from exc
    return data, hashlib.sha256(body).hexdigest()


def list_sources(domain: str = "all") -> dict[str, Any]:
    if domain not in {"all", *SOURCES}:
        raise ScienceDataError("domain must be all, astronomy, or hep_quantum")
    selected = SOURCES if domain == "all" else {domain: SOURCES[domain]}
    return {
        "domains": selected,
        "limitations": [
            "Only adapters marked implemented make API calls.",
            "Catalog membership does not imply complete archive coverage.",
            "Public metadata does not establish reuse or model-training rights.",
        ],
    }


def query_exoplanets(
    columns: Optional[list[str]] = None,
    limit: int = 20,
    opener: Optional[Callable[..., Any]] = None,
) -> dict[str, Any]:
    selected = columns or ["pl_name", "hostname", "discoverymethod", "disc_year"]
    if not 1 <= limit <= 100:
        raise ScienceDataError("limit must be between 1 and 100")
    if not selected or len(selected) > len(EXOPLANET_COLUMNS):
        raise ScienceDataError("columns must contain between 1 and 9 allowed fields")
    if any(column not in EXOPLANET_COLUMNS for column in selected):
        raise ScienceDataError("columns contains an unsupported field")

    query = (
        f"select top {limit} {', '.join(selected)} "
        "from pscomppars order by pl_name"
    )
    url = f"{EXOPLANET_ENDPOINT}?{urllib.parse.urlencode({'query': query, 'format': 'json'})}"
    records, digest = _read_json(url, opener)
    if not isinstance(records, list):
        raise ScienceDataError("upstream_response_shape_invalid")
    return {
        "source": "nasa-exoplanet-archive",
        "query": query,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": url,
        "sha256": digest,
        "record_count": len(records),
        "records": records,
        "evidence_class": "public archive data; not a model validation or physical confirmation",
    }


def search_inspire(
    query: str,
    limit: int = 10,
    opener: Optional[Callable[..., Any]] = None,
) -> dict[str, Any]:
    normalized_query = query.strip()
    if not normalized_query or len(normalized_query) > 500:
        raise ScienceDataError("query must contain 1 to 500 characters")
    if not 1 <= limit <= 20:
        raise ScienceDataError("limit must be between 1 and 20")
    params = urllib.parse.urlencode({
        "q": normalized_query,
        "size": limit,
        "fields": "control_number,titles,authors,arxiv_eprints,dois,publication_info",
    })
    url = f"{INSPIRE_ENDPOINT}?{params}"
    response, digest = _read_json(url, opener)
    try:
        hits = response["hits"]["hits"]
    except (KeyError, TypeError) as exc:
        raise ScienceDataError("upstream_response_shape_invalid") from exc
    return {
        "source": "inspire-hep",
        "query": normalized_query,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": url,
        "sha256": digest,
        "record_count": len(hits),
        "records": hits,
        "evidence_class": "public literature metadata; not experimental measurements",
    }
