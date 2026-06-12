from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
CURRENT_WORK_DIR = Path(os.getcwd()).resolve()
CONFIG_FILE = BASE_DIR / "config.json"


def _load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    with CONFIG_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"config.json must contain a JSON object: {CONFIG_FILE}")
    return data


APP_CONFIG = _load_config()


def get_config(*keys: str, default: Any = None) -> Any:
    value: Any = APP_CONFIG
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def config_path(*keys: str, default: str) -> Path:
    raw = str(get_config(*keys, default=default)).strip() or default
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def config_bool(*keys: str, default: bool = False) -> bool:
    value = get_config(*keys, default=default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def config_int(*keys: str, default: int) -> int:
    value = get_config(*keys, default=default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


DEFAULT_LOG_DIR = config_path("paths", "log_dir", default="logs")
DEFAULT_INPUT_DIR = config_path("paths", "pdf_download_dir", default="pdf_downloads")
DEFAULT_OUTPUT_DIR = config_path("paths", "output_dir", default="output/pdf")
DEFAULT_DOWNLOAD_LOG = config_path("paths", "download_log", default="logs/download_log.csv")
DEFAULT_STORAGE_STATE = config_path("paths", "storage_state", default="wms_storage_state.json")
DEFAULT_DPI = config_int("recognition", "dpi", default=200)
DEFAULT_TIMEOUT = config_int("recognition", "timeout", default=30)
DEFAULT_MAX_PAGES = config_int("recognition", "max_pages", default=1)

WMS_BASE_URL = str(get_config("wms", "base_url", default="https://omp.xlwms.com")).rstrip("/")
WMS_TARGET_PAGE = str(
    get_config("wms", "target_page", default=f"{WMS_BASE_URL}/wms/outbound/parcel")
)

DEFAULT_START_TIME = str(get_config("download", "start_time", default=""))
DEFAULT_END_TIME = str(get_config("download", "end_time", default=""))
DEFAULT_WH_CODES = str(get_config("download", "wh_codes", default=""))
DEFAULT_STATUSES = str(get_config("download", "statuses", default="15"))
DEFAULT_CHANNEL = str(get_config("download", "channel", default=""))
DEFAULT_WORKERS = config_int("download", "workers", default=5)
DEFAULT_LIMIT = config_int("download", "limit", default=0)
DEFAULT_OUTPUT_NAME = str(get_config("paths", "output_name", default="pdf_label_pipeline_result"))
DEFAULT_BROWSER_MODE = config_bool("download", "browser_mode", default=False)

DEFAULT_WMS_USERNAME = os.environ.get("WMS_USERNAME") or str(get_config("wms", "username", default=""))
DEFAULT_WMS_PASSWORD = os.environ.get("WMS_PASSWORD") or str(get_config("wms", "password", default=""))
