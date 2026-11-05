import argparse
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-") or "other"


def key_for(parts):
    return "org-" + "--".join(slug(p) for p in parts)


def read_entries(path: Path):
    header = "#EXTM3U"
    entries, pending = [], []
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.rstrip("\r")
        if line.startswith("#EXTM3U"):
            header = line
        elif line.startswith("#EXTINF"):
            pending = [line]
        elif pending and line.startswith("#"):
            pending.append(line)
        elif pending and line.strip():
            entries.append((pending, line.strip()))
            pending = []
    return header, entries


def replace_group(extinf: str, group: str) -> str:
    safe = group.replace('"', "'")
    if re.search(r'group-title="[^"]*"', extinf):
        return re.sub(r'group-title="[^"]*"', f'group-title="{safe}"', extinf)
    comma = extinf.find(",")
    return (extinf[:comma] + f' group-title="{safe}"' + extinf[comma:]) if comma >= 0 else extinf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", required=True, type=Path)
    ap.add_argument("--playlist", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--assets", required=True, type=Path)
    args = ap.parse_args()

    rows = list(csv.DictReader(args.mapping.open(encoding="utf-8-sig", newline="")))
    by_url = {r["Stream URL"].strip(): r for r in rows if r["Stream URL"].strip()}
    header, entries = read_entries(args.playlist)
    counts, labels, parents, url_tags = Counter(), {}, {}, {}

    for r in rows:
        url = r["Stream URL"].strip()
        parts = [p.strip() for p in r["Full navigation path"].split("/") if p.strip()]
        if not url or not parts:
            continue
        tags = []
        for depth in range(1, len(parts) + 1):
            k = key_for(parts[:depth])
            tags.append(k)
            labels[k] = ("★ " if depth == 1 else "  " * (depth - 1) + "• ") + parts[-1 if depth == len(parts) else depth - 1]
            parents[k] = key_for(parts[: depth - 1]) if depth > 1 else ""
            counts[k] += 1
        url_tags[url] = (tags, int(r["Display order"] or 999999), r["Channel"])

    fallback = ["International", "Unclassified / review"]
    for depth in range(1, 3):
        k = key_for(fallback[:depth])
        labels[k] = ("★ " if depth == 1 else "  • ") + fallback[depth - 1]
        parents[k] = key_for(fallback[: depth - 1]) if depth > 1 else ""

    order = {"lebanon-arabic": 0, "english": 1, "international": 2}
    def node_sort(k):
        path = k.removeprefix("org-").split("--")
        return (order.get(path[0], 9), len(path), k)

    fav_lines = ["# stream-url\tfolders\tsort-name"]
    playlist_lines = [header]
    unmatched = 0
    for meta, url in entries:
        mapped = by_url.get(url)
        if mapped:
            parts = [p.strip() for p in mapped["Full navigation path"].split("/") if p.strip()]
            group = " / ".join(parts)
            tags, display, channel = url_tags[url]
        else:
            unmatched += 1
            group = "International / Unclassified / review"
            tags = [key_for(fallback[:1]), key_for(fallback)]
            display, channel = 999999, meta[0].split(",", 1)[-1]
            for k in tags:
                counts[k] += 1
        fav_lines.append(f"{url}\t{','.join(tags)}\t{display:06d}-{slug(channel)}")
        playlist_lines.append(replace_group(meta[0], group))
        playlist_lines.extend(meta[1:])
        playlist_lines.append(url)

    catalog_lines = ["# key\tlabel\tparent\tchannel-count"]
    for k in sorted(labels, key=node_sort):
        catalog_lines.append(f"{k}\t{labels[k]}\t{parents[k]}\t{counts[k]}")

    args.out.mkdir(parents=True, exist_ok=True)
    args.assets.mkdir(parents=True, exist_ok=True)
    (args.out / "folder-catalog.tsv").write_text("\n".join(catalog_lines) + "\n", encoding="utf-8")
    (args.out / "favourite-folders.tsv").write_text("\n".join(fav_lines) + "\n", encoding="utf-8")
    (args.out / "dtv.m3u8").write_text("\n".join(playlist_lines) + "\n", encoding="utf-8")
    for name in ("folder-catalog.tsv", "favourite-folders.tsv"):
        (args.assets / name).write_bytes((args.out / name).read_bytes())
    print(f"mapping={len(rows)} playlist={len(entries)} matched={len(entries)-unmatched} unmatched={unmatched} folders={len(labels)}")


if __name__ == "__main__":
    main()
