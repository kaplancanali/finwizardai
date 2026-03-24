"""
Build KAP şirket özet URLs.

KAP uses path segments like ``832-adel-kalemcilik-ticaret-ve-sanayi-a-s``, not bare BIST codes.
See: https://www.kap.org.tr/tr/sirket-bilgileri/ozet/832-adel-kalemcilik-ticaret-ve-sanayi-a-s
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional

from utils.config import get_settings

_SLUG_SAFE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9-]*$")

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "kap_ozet_slugs.json"


def _parse_slug_overrides_json(raw: str) -> Dict[str, str]:
    raw = (raw or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, str] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str):
            seg = v.strip().strip("/")
            if seg and _SLUG_SAFE.match(seg):
                out[k.upper().strip()] = seg
    return out


def _load_data_file_slugs() -> Dict[str, str]:
    if not _DATA_FILE.is_file():
        return {}
    try:
        text = _DATA_FILE.read_text(encoding="utf-8")
    except OSError:
        return {}
    return _parse_slug_overrides_json(text)


def kap_ozet_path_segment(
    bist_symbol: str,
    slug_override: Optional[str] = None,
) -> str:
    """
    Return the URL path segment after ``.../ozet/`` (no slashes).

    Resolution: optional per-disclosure override, then env JSON overrides,
    then ``data/kap_ozet_slugs.json``, else uppercase BIST code (legacy).
    """
    sym = bist_symbol.upper().strip()
    if slug_override:
        seg = slug_override.strip().strip("/")
        if seg and _SLUG_SAFE.match(seg):
            return seg

    settings = get_settings()
    env_map = _parse_slug_overrides_json(
        getattr(settings, "KAP_OZET_SLUG_OVERRIDES_JSON", "") or ""
    )
    file_map = _load_data_file_slugs()
    merged = {**file_map, **env_map}
    return merged.get(sym, sym)


def kap_company_ozet_url(
    bist_symbol: str,
    slug_override: Optional[str] = None,
) -> str:
    """Full HTTPS URL for the company özet page."""
    base = get_settings().KAP_BASE_URL.rstrip("/")
    segment = kap_ozet_path_segment(bist_symbol, slug_override=slug_override)
    return f"{base}/tr/sirket-bilgileri/ozet/{segment}"
