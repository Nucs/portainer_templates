# portainer_templates

This project provides a Python script and automated pipelines that generates a merge Portainer templates file from multiple sources into a single templates.json you can reference in portainer settings.

Capable of combining templates from various URLs and local files into a single, comprehensive template file for use with Portainer.

**Fork** me! and the have your own automation for generating in a private/public!<br/>
**Pull Request** me! and add your / other templates.json to this project.

## Features

- Merges Portainer templates from multiple sources (URLs and local files)
- Generates a single JSON file compatible with Portainer
- Automated weekly updates via GitHub Actions
- Removes duplicate templates, Case-insensitive distinction of templates between all sources
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
