#!/usr/bin/env python3
"""Refuse to publish an APK that is not the self-contained D TV variant."""

from __future__ import annotations

import argparse
import re
import subprocess
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("apk", type=Path)
    parser.add_argument("--aapt", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--version-code", required=True, type=int)
    args = parser.parse_args()

    badging = subprocess.run(
        [str(args.aapt), "dump", "badging", str(args.apk)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout
    first = badging.splitlines()[0] if badging else ""
    expected = {
        "name": "app.opentv.stremiolab",
        "versionCode": str(args.version_code),
        "versionName": f"{args.version}-stremio-lab",
    }
    for key, value in expected.items():
        if not re.search(rf"\b{key}='{re.escape(value)}'", first):
            raise SystemExit(f"wrong APK {key}: expected {value!r}; badging={first}")

    required = {
        "assets/dtv/dtv.m3u8",
        "assets/dtv/favourite-folders.tsv",
        "assets/dtv/folder-catalog.tsv",
        "assets/dtv/guide.xmltvz",
        "assets/dtv/stream-headers.tsv",
    }
    with zipfile.ZipFile(args.apk) as archive:
        missing = required - set(archive.namelist())
        if missing:
            raise SystemExit(f"APK is missing bundled D TV assets: {sorted(missing)}")
        playlist = archive.read("assets/dtv/dtv.m3u8")
        channels = playlist.count(b"#EXTINF")
        if channels < 25_000:
            raise SystemExit(f"bundled playlist is unexpectedly small: {channels} channels")
    print(f"verified {expected['name']} {expected['versionName']} with {channels} bundled channels")


if __name__ == "__main__":
    main()
