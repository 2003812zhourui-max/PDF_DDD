from __future__ import annotations

import argparse
import csv
import os
import shutil
from pathlib import Path


CSV_FIELDS = [
    "deliveryNo",
    "sourceNo",
    "expressNo",
    "customerCode",
    "whCode",
    "logisticsCarrier",
    "logisticsChannel",
    "logisticsChannelName",
    "channelGroupCode",
    "channelGroupName",
    "status",
    "filePath",
    "error",
    "downloadedAt",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "utf-8", "gbk"):
        try:
            with path.open("r", newline="", encoding=encoding) as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError:
            continue
    return []


def unique_target(target_dir: Path, source: Path, delivery_no: str, index: int) -> Path:
    candidate = target_dir / source.name
    if not candidate.exists():
        return candidate
    stem = source.stem
    suffix = source.suffix
    safe_delivery = "".join(ch if ch.isalnum() else "_" for ch in delivery_no) or "row"
    return target_dir / f"{safe_delivery}_{index}_{stem}{suffix}"


def link_or_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return
    try:
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild an exact input folder and combined WMS log from batch logs.")
    parser.add_argument("--log-glob", required=True, help="Glob for batch download logs.")
    parser.add_argument("--staging-dir", required=True, help="Directory to hold hardlinks/copies for this rebuild.")
    parser.add_argument("--combined-log", required=True, help="Output combined CSV log path.")
    args = parser.parse_args()

    log_paths = sorted(Path().glob(args.log_glob), key=lambda path: path.stat().st_mtime)
    if not log_paths:
        raise SystemExit(f"No logs matched: {args.log_glob}")

    staging_dir = Path(args.staging_dir).resolve()
    combined_log = Path(args.combined_log).resolve()
    staging_dir.mkdir(parents=True, exist_ok=True)
    combined_log.parent.mkdir(parents=True, exist_ok=True)

    latest_by_delivery: dict[str, dict[str, str]] = {}
    for log_path in log_paths:
        for row in read_rows(log_path):
            if row.get("status") != "success":
                continue
            delivery_no = (row.get("deliveryNo") or "").strip()
            file_path = (row.get("filePath") or "").strip()
            if not delivery_no or not file_path:
                continue
            latest_by_delivery[delivery_no] = row

    output_rows: list[dict[str, str]] = []
    missing: list[str] = []
    for row in latest_by_delivery.values():
        linked_paths: list[str] = []
        for index, raw_path in enumerate(str(row.get("filePath") or "").split("|"), start=1):
            source = Path(raw_path)
            if not source.exists():
                missing.append(raw_path)
                continue
            target = unique_target(staging_dir, source, row.get("deliveryNo", ""), index)
            link_or_copy(source, target)
            linked_paths.append(str(target))

        for linked_path in linked_paths:
            out = {field: row.get(field, "") for field in CSV_FIELDS}
            out["filePath"] = linked_path
            output_rows.append(out)

    with combined_log.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"logs={len(log_paths)}")
    print(f"deliveries={len(latest_by_delivery)}")
    print(f"files={len(output_rows)}")
    print(f"staging_dir={staging_dir}")
    print(f"combined_log={combined_log}")
    if missing:
        print(f"missing_files={len(missing)}")
        for item in missing[:20]:
            print(f"missing: {item}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
