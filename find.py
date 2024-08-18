"""
Find notes in a vault
"""

import json
from pathlib import Path
import re
import subprocess
from shutil import which

import yaml

import config


def find_rg_iter(vault_dir):
    process = subprocess.Popen(
        [
            which("rg"),
            config.SEARCH_PATTERN,
            vault_dir,
            "-U",
            "--type",
            "markdown",
            "--json",
        ],
        stdout=subprocess.PIPE,
    )

    file_tags = []
    for raw in process.stdout:
        data = json.loads(raw)
        match data:
            case {
                "type": "begin",
                "data": {
                    "path": {"text": path},
                },
            }:
                file_tags = get_anki_tags(path)
            case {
                "type": "match",
                "data": {
                    "path": {"text": filepath},
                    "lines": {"text": content},
                    "line_number": lineno,
                    "absolute_offset": _,
                    "submatches": [*_],
                },
            }:
                yield file_tags, content, Path(filepath), lineno
            case _:
                continue


def get_anki_tags(filepath):
    with open(filepath, encoding="utf-8") as f:
        if not f.readline().startswith("---"):
            return []
        properties = next(yaml.safe_load_all(f))
    tags = properties.get("anki-tag", [])
    if not isinstance(tags, list):
        tags = [tags]
    return tags


def parse_table(content):
    lines = (
        [i.strip() for i in row.strip("|").split("|")] for row in content.splitlines()
    )
    header = next(lines)
    next(lines)  # skip head/body separator
    # ignore empty sort field
    yield from (dict(zip(header, card)) for card in lines if not card[0].isspace())


def pop_tags(data):
    return (data.pop("tags") or "").split() if "tags" in data else []


def find_notes(vault_dir, verbose_print):
    for file_tags, match, filepath, lineno in find_rg_iter(vault_dir):
        info = re.match(config.SEARCH_PATTERN, match).groupdict()
        content = info.pop("content")
        tags = pop_tags(info)
        group_tags = config.GLOBAL_TAGS + file_tags + tags
        verbose_print(
            f"Match at {filepath.relative_to(vault_dir)}:{lineno}\n"
            f"    info: {info}\n"
            f"    tags: global={config.GLOBAL_TAGS} file={file_tags} group={tags}"
        )
        for fields in parse_table(content):
            yield {
                **info,
                "tags": group_tags + pop_tags(fields),
                "fields": fields,
            }
