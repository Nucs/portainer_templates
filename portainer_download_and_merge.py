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

URLS = [
    "https://raw.githubusercontent.com/Lissy93/portainer-templates/main/templates.json",
    "https://raw.githubusercontent.com/xneo1/portainer_templates/master/Template/template.json",
    "https://raw.githubusercontent.com/technorabilia/portainer-templates/main/lsio/templates/templates-2.0.json",
    "https://raw.githubusercontent.com/Qballjos/portainer_templates/master/Template/template.json",
    "https://raw.githubusercontent.com/TheLustriVA/portainer-templates-Nov-2022-collection/main/templates_2_2_rc_2_2.json",
    "https://raw.githubusercontent.com/ntv-one/portainer/main/template.json",
    "https://raw.githubusercontent.com/mycroftwilde/portainer_templates/master/Template/template.json",
    "https://raw.githubusercontent.com/mikestraney/portainer-templates/master/templates.json",
    "https://raw.githubusercontent.com/dnburgess/self-hosted-template/master/template.json",
    "https://raw.githubusercontent.com/SelfhostedPro/selfhosted_templates/portainer-2.0/Template/template.json",
    "https://raw.githubusercontent.com/mediadepot/templates/master/portainer.json"
]

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
    args = parser.parse_args()

    downloaded_files = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, url in enumerate(URLS):
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
