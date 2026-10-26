#!/usr/bin/env python3
"""Translate D TV's multi-folder map into one no-duplicate M3U category per channel."""

from __future__ import annotations

import re
import sys
from pathlib import Path


LABELS = {
    "australia": "01 · Australia",
    "lebanon": "02 · Lebanon",
    "arabic": "03 · Arabic",
    "news-australia": "04 · News · Australia",
    "news-arabic": "04 · News · Arabic",
    "news-business": "04 · News · Business",
    "news-weather": "04 · News · Weather",
    "news-world": "04 · News · World",
    "news": "04 · News · General",
    "science": "05 · Science, Space & Discovery",
    "youtube-live": "06 · Official YouTube Live",
    "sports-rugby": "07 · Sports · 01 Rugby",
    "sports-australia": "07 · Sports · 02 Australian Sports",
    "sports-golf": "07 · Sports · 03 Golf",
    "sports-poker": "07 · Sports · 04 Poker & Triton",
    "sports-motorsport": "07 · Sports · 05 Motorsport",
    "sports-combat": "07 · Sports · 06 Combat",
    "sports-extreme": "07 · Sports · 07 Extreme",
    "sports-soccer": "07 · Sports · 08 Soccer",
    "sports-basketball": "07 · Sports · 09 Basketball",
    "sports-american-football": "07 · Sports · 10 American Football",
    "sports-baseball": "07 · Sports · 11 Baseball",
    "sports-other": "07 · Sports · 12 Other",
    "sports": "07 · Sports · 12 Other",
    "tvshows-a-e": "08 · TV Shows · A–E",
    "tvshows-f-j": "08 · TV Shows · F–J",
    "tvshows-k-o": "08 · TV Shows · K–O",
    "tvshows-p-t": "08 · TV Shows · P–T",
    "tvshows-u-z": "08 · TV Shows · U–Z",
    "tvshows-other": "08 · TV Shows · 0–9 & Other",
    "tvshows": "08 · TV Shows · Other",
    "movies-action": "09 · Movies · Action",
    "movies-comedy": "09 · Movies · Comedy",
    "movies-horror": "09 · Movies · Horror",
    "movies-thriller": "09 · Movies · Thriller & Crime",
    "movies-romance": "09 · Movies · Romance",
    "movies-sci-fi": "09 · Movies · Science Fiction",
    "movies-western": "09 · Movies · Western",
    "movies-classics": "09 · Movies · Classics",
    "movies-documentary": "09 · Movies · Documentary",
    "movies-family": "09 · Movies · Family",
    "movies-animation": "09 · Movies · Animation & Anime",
    "movies-war": "09 · Movies · War",
    "movies-mystery": "09 · Movies · Mystery & Film Noir",
    "movies-other": "09 · Movies · Other",
    "movies": "09 · Movies · Other",
    "comedy-standup": "10 · Comedy · Stand-up",
    "comedy-sitcom": "10 · Comedy · Sitcoms",
    "comedy-other": "10 · Comedy · Sketch & Other",
    "comedy": "10 · Comedy · Other",
    "music-english-pop": "11 · Music · English · Pop & Hits",
    "music-english-rock": "11 · Music · English · Rock & Metal",
    "music-english-hip-hop-rnb": "11 · Music · English · Hip-Hop & R&B",
    "music-english-country": "11 · Music · English · Country",
    "music-english-classical": "11 · Music · English · Classical",
    "music-english-jazz": "11 · Music · English · Jazz & Blues",
    "music-english-dance-electronic": "11 · Music · English · Dance & Electronic",
    "music-language-english": "11 · Music · English · Other",
    "music-language-arabic": "11 · Music · Arabic",
    "music-language-french": "11 · Music · French",
    "music-language-spanish": "11 · Music · Spanish",
    "music-language-other": "11 · Music · Other Languages",
    "music": "11 · Music · Other",
    "kids-preschool": "12 · Kids · Preschool",
    "kids-animation": "12 · Kids · Animation",
    "kids-education": "12 · Kids · Learning",
    "kids-family": "12 · Kids · Family",
    "kids": "12 · Kids · Other",
}

# Most-specific entertainment sections win. Country sections collect everything not already
# assigned to a more useful browsing shelf, keeping one physical channel row and no duplicates.
PRIORITY = [
    "sports-rugby", "sports-australia", "sports-golf", "sports-poker",
    "sports-motorsport", "sports-combat", "sports-extreme", "sports-soccer",
    "sports-basketball", "sports-american-football", "sports-baseball", "sports-other",
    "tvshows-a-e", "tvshows-f-j", "tvshows-k-o", "tvshows-p-t", "tvshows-u-z", "tvshows-other",
    "movies-action", "movies-comedy", "movies-horror", "movies-thriller", "movies-romance",
    "movies-sci-fi", "movies-western", "movies-classics", "movies-documentary",
    "movies-family", "movies-animation", "movies-war", "movies-mystery", "movies-other",
    "comedy-standup", "comedy-sitcom", "comedy-other",
    "music-english-pop", "music-english-rock", "music-english-hip-hop-rnb",
    "music-english-country", "music-english-classical", "music-english-jazz",
    "music-english-dance-electronic", "music-language-english", "music-language-arabic",
    "music-language-french", "music-language-spanish", "music-language-other",
    "kids-preschool", "kids-animation", "kids-education", "kids-family",
    "news-australia", "news-arabic", "news-business", "news-weather", "news-world",
    "science", "youtube-live", "lebanon", "arabic", "australia",
    "sports", "tvshows", "movies", "comedy", "music", "kids", "news",
]


def folder_map(path: Path) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 2:
            result[fields[0]] = {tag for tag in fields[1].split(",") if tag}
    return result


def choose(tags: set[str], fallback: str) -> str:
    for tag in PRIORITY:
        if tag in tags:
            return LABELS[tag]
    return f"13 · More Channels · {fallback}" if fallback else "13 · More Channels"


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: build_organised_playlist.py INPUT_M3U FOLDERS_TSV OUTPUT_M3U")
    source, folders_path, output = map(Path, sys.argv[1:])
    folders = folder_map(folders_path)
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    out = ['#EXTM3U x-tvg-url="https://enlb.github.io/dtv-opentv-installer/guide.xml.gz"']
    pending: list[str] = []
    extinf = ""
    seen_urls: set[str] = set()
    for line in lines[1:]:
        if line.startswith("#EXTINF"):
            if pending:
                out.extend(pending)
            pending = []
            extinf = line
        elif line.startswith("#") or not line.strip():
            pending.append(line)
        else:
            url = line.strip()
            if url in seen_urls:
                extinf = ""
                pending = []
                continue
            seen_urls.add(url)
            match = re.search(r'group-title="([^"]*)"', extinf)
            fallback = match.group(1) if match else "Other"
            label = choose(folders.get(url, set()), fallback)
            replacement = f'group-title="{label}"'
            if match:
                extinf = extinf[: match.start()] + replacement + extinf[match.end() :]
            else:
                extinf = extinf.replace("#EXTINF:-1", f"#EXTINF:-1 {replacement}", 1)
            out.append(extinf)
            out.extend(pending)
            out.append(line)
            extinf = ""
            pending = []
    output.write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
