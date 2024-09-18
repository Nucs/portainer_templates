# portainer_templates

This project provides a Python script and automated pipelines that generates a merged Portainer templates file from multiple sources. 

It's designed to combine templates from various URLs and local files into a single, comprehensive template file for use with Portainer.

**Fork** me! and the have your own automation for generating!<br/>
**Pull Request** me! and add another source of local repository or url for a portainer templates json.

## Features

- Merges Portainer templates from multiple sources (URLs and local files)
- Removes duplicate templates
- Generates a single JSON file compatible with Portainer
- Automated weekly updates via GitHub Actions
- Distinction of templates between all sources
- Case-insensitive grouping of templates
- Generates both clean (grouped) and unclean (all) template files
- Implements distinct-by-all approach before grouping
## Installation

Add this URL in Portainer's settings:

```
https://raw.githubusercontent.com/Nucs/portainer_templates/main/releases/templates.json
```

## Usage

### Manual Execution


1. Clone this repository:
   ```
   git clone https://github.com/Nucs/portainer_templates.git
   cd portainer_templates
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the script manually:

   ```
   python portainer_templates_generate.py
   ```

   This will generate two files:
   - `releases/templates.json`: Contains the clean, grouped templates
   - `releases/templates_unclean.json`: Contains all templates without grouping

   Optional arguments:
   - `-o`, `--output`: Specify the output file path for clean templates (default: `releases/templates.json`)
   - `-s`, `--sources`: Specify the file containing source URLs (default: `sources.txt`)

   Note: The unclean templates file will always be saved as `releases/templates_unclean.json`

### Automated Execution (Windows)

Use the `run.bat` script:

```
run.bat
```

To commit and push changes to git, use:

```
run.bat --commit
```

## License

[MIT License](LICENSE)

## Acknowledgements

This project is maintained by [Nucs](https://github.com/Nucs). Thanks to all contributors who have helped improve and expand the template collection.
