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
from itertools import groupby


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
        urls = [
            line.strip() if is_url(line.strip()) else os.path.join(base_dir, line.strip())
            for line in f
            if line.strip() and not line.strip().startswith('#')
        ]
    return sorted(urls)

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

def group_and_distinct_templates(templates: List[dict]) -> List[dict]:
    def template_to_tuple(template):
        return tuple(sorted((k, json.dumps(v, sort_keys=True).lower()) for k, v in template.items()))

    # First, make templates distinct by all fields
    distinct_templates = list({template_to_tuple(template): template for template in templates}.values())

    def group_key(template):
        def to_str(value):
            return json.dumps(value, sort_keys=True).lower() if isinstance(value, dict) else str(value).lower()

        return (
            to_str(template.get("name", "")),
            to_str(template.get("command", "")),
            to_str(template.get("platform", "")),
            ",".join(sorted(to_str(v) for v in template.get("volumes", []))),
            ",".join(sorted(to_str(p) for p in template.get("ports", []))),
            to_str(template.get("image", "")),
            to_str(template.get("repository", "")),
            to_str(template.get("type", ""))
        )

    def sort_key(template):
        return sum(len(json.dumps(template.get(field, ""))) for field in ["env", "description", "title", "note", "ports"])

    # Sort distinct templates by group key
    sorted_templates = sorted(distinct_templates, key=group_key)

    # Group templates and select the one with the highest sort key from each group
    final_distinct_templates = []
    for _, group in groupby(sorted_templates, key=group_key):
        final_distinct_templates.append(max(group, key=sort_key))

    return final_distinct_templates

def normalize_category(category: str) -> str:
    # Remove ':', remove whitespace, change case to first upper rest lower
    return category.replace(':', '').replace(' ', '').strip().capitalize()

def merge_unique_templates(files: list[dict]) -> dict:
    version = None
    all_templates = []
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

        for template in f["templates"]:
            if "categories" in template:
                template["categories"] = [normalize_category(cat) for cat in template["categories"]]
        all_templates.extend(f["templates"])

    distinct_templates = group_and_distinct_templates(all_templates)
    
    # Sort the distinct templates by title
    sorted_templates = sorted(distinct_templates, key=lambda x: x.get('title', '').lower())
    
    return {
        "version": version,
        "templates": sorted_templates,
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

def save_unclean_output(output: str, all_templates: dict, num_files: int) -> None:
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_templates, f, indent=2)
    print(
        colorize(
            (
                f"Saved unclean templates from {num_files} files\n"
                f"Total templates: {len(all_templates['templates'])}\n"
                f"Output file: {Path(f.name).absolute()}\n"
            ),
            Color.SUCCESS,
        ),
        flush=True,
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Download and merge Portainer templates from multiple URLs")
    parser.add_argument("-o", "--output", help="Output file (default: releases/templates.json)", default="releases/templates.json")
    parser.add_argument("-s", "--sources", help="File containing source URLs", default="sources.txt")
    args = parser.parse_args()

    # Ensure the output path is valid
    if not args.output:
        args.output = "releases/templates.json"
    
    # Ensure the releases directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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
            # Load all templates without distinction/groupby
            all_templates = {
                "version": "2",
                "templates": []
            }
            for f in downloaded_files:
                data = json.load(open(f))
                all_templates["templates"].extend(data["templates"])

            # Sort all templates by title
            all_templates["templates"] = sorted(all_templates["templates"], key=lambda x: x.get('title', '').lower())

            # Save unclean templates
            unclean_output = os.path.join(output_dir, "templates_unclean.json")
            save_unclean_output(unclean_output, all_templates, len(downloaded_files))

            # Process and save clean templates
            merged_templates = merge_unique_templates([json.load(open(f)) for f in downloaded_files])
            save_output(args.output, merged_templates, len(downloaded_files))
        except Exception as e:
            print(colorize(f"Error processing templates: {str(e)}", Color.FAIL), file=sys.stderr)
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
