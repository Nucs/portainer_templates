#!/usr/bin/env python3

import argparse
import json
import os
import sys
import traceback as tb
from pathlib import Path
from typing import Literal, NamedTuple


class Color(NamedTuple):
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Color.ENDC}"


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


def save_output(args: argparse.Namespace, merged_templates: dict) -> None:
    if args.output in ["-", "/dev/stdout", sys.stdout]:
        sys.stdout.writelines(json.dumps(merged_templates, indent=2) + "\n")
        sys.stdout.flush()
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(merged_templates, f, indent=2)
        print(
            colorize(
                (
                    f"Merged {len(args.files)} template files\n"
                    f"Total unique templates: {len(merged_templates['templates'])}\n"
                    f"Output file: {Path(f.name).absolute()}\n"
                ),
                Color.SUCCESS,
            ),
            flush=True,
        )


def main() -> Literal[0]:
    parser = argparse.ArgumentParser(description="Merge portainer templates without duplicates", add_help=False)
    parser.add_argument(
        "files",
        help="Portainer template files (JSON)",
        nargs="+",
        type=argparse.FileType("r"),
        metavar="INPUT_FILES",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Example: ./merge_portainer_templates -o merged.json templates_1.json templates_2.json",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file, by default output to stdout",
        default=sys.stdout,
        metavar="OUTPUT_FILE",
    )
    args = parser.parse_args()
    if len(args.files) == 1:
        print(
            colorize("\nAt least two template files are required\n", Color.FAIL),
            file=sys.stderr,
            flush=True,
        )
        parser.print_help()
        sys.exit(1)

    try:
        merged_templates = merge_unique_templates([json.load(f) for f in args.files])
        save_output(args, merged_templates)
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(tb.format_exc())
    except Exception:
        print(
            colorize("Unknown error occured during merging, files closed\n", Color.FAIL),
            file=sys.stderr,
            flush=True,
        )
        sys.exit(tb.format_exc())
    finally:
        for f in args.files:
            f.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
