#!/usr/bin/env python3

"""
This script downloads and merges Portainer templates from multiple URLs.
It reads source URLs from a file, downloads JSON data from each URL,
merges the templates, and saves the result to an output file.

Usage:
    python portainer_templates_generate.py [-o OUTPUT] [-s SOURCES]

Arguments:
    -o, --output: Output file path (default: releases\templates.json)
    -s, --sources: File containing source URLs (default: sources.txt)
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.request
import traceback as tb
from pathlib import Path
from typing import List, Literal, NamedTuple, Union


class Color(NamedTuple):
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Color.ENDC}"


def is_url(path: str) -> bool:
    return path.startswith(('http://', 'https://'))

def read_urls_from_file(file_path: str) -> List[str]:
    base_dir = os.path.dirname(os.path.abspath(file_path))
    with open(file_path, 'r') as f:
        return [
            line.strip() if is_url(line.strip()) else os.path.join(base_dir, line.strip())
            for line in f
            if line.strip() and not line.strip().startswith('#')
        ]

def download_or_read_json(source: str) -> Union[dict, None]:
    if is_url(source):
        return download_json(source)
    else:
        try:
            with open(source, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(colorize(f"Error reading {source}: {str(e)}", Color.FAIL), file=sys.stderr)
            return None


def download_json(url: str) -> dict:
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(colorize(f"Error downloading {url}: {str(e)}", Color.FAIL), file=sys.stderr)
        return None


def merge_unique_templates(files: list[dict]) -> dict:
    version = None
    unique_templates = []
    for f in files:
        if version is None:
            version = f["version"]
        elif version != f["version"]:
            print(
                colorize(
                    (
                        "Templates are not for the same portainer version, "
                        f"can't merge v{version} and v{f['version']}"
                    ),
                    Color.FAIL,
                ),
                file=sys.stderr,
                flush=True,
            )
            sys.exit(1)

        templates: list[dict] = f["templates"]
        for t in templates:
            if t not in unique_templates:
                unique_templates.append(t)
    return {
        "version": version,
        "templates": unique_templates,
    }


def save_output(output: str, merged_templates: dict, num_files: int) -> None:
    if output in ["-", "/dev/stdout", sys.stdout]:
        sys.stdout.writelines(json.dumps(merged_templates, indent=2) + "\n")
        sys.stdout.flush()
    else:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(merged_templates, f, indent=2)
        print(
            colorize(
                (
                    f"Merged {num_files} template files\n"
                    f"Total unique templates: {len(merged_templates['templates'])}\n"
                    f"Output file: {Path(f.name).absolute()}\n"
                ),
                Color.SUCCESS,
            ),
            flush=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and merge Portainer templates from multiple URLs")
    parser.add_argument("-o", "--output", help="Output file (default: releases\\templates.json)", default="releases\\templates.json")
    parser.add_argument("-s", "--sources", help="File containing source URLs", default="sources.txt")
    args = parser.parse_args()

    # Ensure the releases directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    urls = read_urls_from_file(args.sources)
    if not urls:
        print(colorize("No URLs found in the sources file.", Color.FAIL), file=sys.stderr)
        return 1

    downloaded_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, source in enumerate(urls):
            print(f"Processing {source}...", flush=True)
            data = download_or_read_json(source)
            if data:
                temp_file = os.path.join(temp_dir, f"template_{i}.json")
                with open(temp_file, "w") as f:
                    json.dump(data, f)
                downloaded_files.append(temp_file)

        if not downloaded_files:
            print(colorize("No files were successfully processed.", Color.FAIL), file=sys.stderr)
            return 1

        print(f"Successfully processed {len(downloaded_files)} files.", flush=True)
        
        try:
            merged_templates = merge_unique_templates([json.load(open(f)) for f in downloaded_files])
            save_output(args.output, merged_templates, len(downloaded_files))
        except Exception as e:
            print(colorize(f"Error merging templates: {str(e)}", Color.FAIL), file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    except Exception:
        print(
            colorize("Unknown error occurred during execution\n", Color.FAIL),
            file=sys.stderr,
            flush=True,
        )
        sys.exit(tb.format_exc())
