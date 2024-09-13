#!/usr/bin/env python3

import argparse
import json
import os
import sys
import tempfile
import urllib.request
from typing import List

# Import the merge function from the existing script
from portainer_merge_jsons import merge_unique_templates, save_output, Color, colorize

def read_urls_from_file(file_path: str) -> List[str]:
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def download_json(url: str) -> dict:
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(colorize(f"Error downloading {url}: {str(e)}", Color.FAIL), file=sys.stderr)
        return None

def main() -> int:
    parser = argparse.ArgumentParser(description="Download and merge Portainer templates from multiple URLs")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)", default="-")
    parser.add_argument("-s", "--sources", help="File containing source URLs", default="sources.txt")
    args = parser.parse_args()

    urls = read_urls_from_file(args.sources)
    if not urls:
        print(colorize("No URLs found in the sources file.", Color.FAIL), file=sys.stderr)
        return 1

    downloaded_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, url in enumerate(urls):
            print(f"Downloading from {url}...", flush=True)
            data = download_json(url)
            if data:
                temp_file = os.path.join(temp_dir, f"template_{i}.json")
                with open(temp_file, "w") as f:
                    json.dump(data, f)
                downloaded_files.append(temp_file)

        if not downloaded_files:
            print(colorize("No files were successfully downloaded.", Color.FAIL), file=sys.stderr)
            return 1

        print(f"Successfully downloaded {len(downloaded_files)} files.", flush=True)
        
        try:
            merged_templates = merge_unique_templates([json.load(open(f)) for f in downloaded_files])
            save_output(args.output, merged_templates, len(downloaded_files))
        except Exception as e:
            print(colorize(f"Error merging templates: {str(e)}", Color.FAIL), file=sys.stderr)
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
