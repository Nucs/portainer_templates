# Portainer Templates Generator

This project provides a Python script that generates a merged Portainer templates file from multiple sources. It's designed to combine templates from various URLs and local files into a single, comprehensive template file for use with Portainer.

## Features

- Merges Portainer templates from multiple sources (URLs and local files)
- Removes duplicate templates
- Generates a single JSON file compatible with Portainer
- Automated weekly updates via GitHub Actions

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Nucs/portainer_templates.git
   cd portainer_templates
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Manual Execution

Run the script manually:

```
python portainer_templates_generate.py
```

Optional arguments:
- `-o`, `--output`: Specify the output file path (default: `releases/templates.json`)
- `-s`, `--sources`: Specify the file containing source URLs (default: `sources.txt`)

### Automated Execution (Windows)

Use the `run.bat` script:

```
run.bat
```

To commit and push changes automatically, use:

```
run.bat --commit
```

### Using the Generated Template in Portainer

Add this URL in Portainer's settings:

```
https://raw.githubusercontent.com/Nucs/portainer_templates/main/releases/templates.json
```

## Contributing

1. Add new template sources to `sources.txt`.
2. Create a pull request with your changes.

## License

[MIT License](LICENSE)

## Acknowledgements

This project is maintained by [Nucs](https://github.com/Nucs). Thanks to all contributors who have helped improve and expand the template collection.
