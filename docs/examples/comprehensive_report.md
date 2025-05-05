---
title: "Comprehensive Report Generation with Twinizer"
description: "Learn how to generate complete project reports with multiple formats using Twinizer's generate-report command"
author: "Tom Sapletta"
keywords: "twinizer, report generation, project analysis, hardware analysis, code analysis, documentation, SVG, HTML, PDF"
lang: "pl"
category: "examples"
toc: true
sidebar: true
permalink: /docs/examples/comprehensive-report/
last_modified_at: 2025-05-05
---

# Comprehensive Report Generation Example

This guide demonstrates how to generate a complete project report using Twinizer's `generate-report` command.

## Basic Usage

The simplest way to generate a comprehensive report is:

```bash
twinizer generate-report /path/to/project --output-dir ./reports --build-website
```

This will:
- Analyze the project structure
- Generate a basic HTML report
- Create a website to navigate the report

## Complete Example

For a more comprehensive report with all available features:

```bash
twinizer generate-report /path/to/my_hardware_project \
  --output-dir ./project_reports \
  --include-formats svg,html,pdf,markdown,json \
  --analyze-code \
  --analyze-hardware \
  --extract-schematics \
  --build-website \
  --serve \
  --port 8080 \
  --theme dark \
  --title "My Hardware Project Analysis" \
  --logo /path/to/logo.png
```

## Report Structure

The generated report will have the following structure:

```
project_reports/
├── code/                  # Code analysis reports
│   ├── metrics/           # Code metrics
│   ├── linting/           # Linting results
│   ├── security/          # Security analysis
│   └── documentation/     # Generated code documentation
├── hardware/              # Hardware analysis
│   ├── schematics/        # Extracted schematics
│   │   ├── svg/           # SVG format schematics
│   │   ├── pdf/           # PDF format schematics
│   │   └── html/          # Interactive HTML schematics
│   ├── bom/               # Bill of materials
│   └── connections/       # Connection diagrams
├── diagrams/              # Project structure diagrams
│   ├── dependency/        # Dependency graphs
│   ├── component/         # Component diagrams
│   └── flow/              # Flow diagrams
├── downloads/             # Downloadable reports
│   ├── full_report.pdf    # Complete PDF report
│   ├── code_report.pdf    # Code analysis PDF
│   └── hardware_report.pdf # Hardware analysis PDF
├── assets/                # Website assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images used in the report
└── index.html             # Main report page
```

## Website Features

The generated website includes:

- **Interactive Navigation**: Easy navigation between different sections of the report
- **Search Functionality**: Search across all report content
- **Filtering Options**: Filter results by severity, type, or component
- **Dark/Light Mode**: Toggle between dark and light themes
- **Download Options**: Download reports in various formats
- **Interactive Diagrams**: Zoomable and clickable SVG diagrams
- **Code Highlighting**: Syntax highlighting for code snippets
- **Responsive Design**: Works on desktop and mobile devices

## Real-World Example

Here's a complete example using a KiCad project:

```bash
# Clone a sample KiCad project
git clone https://github.com/KiCad/kicad-source-mirror.git
cd kicad-source-mirror

# Generate a comprehensive report
twinizer generate-report . \
  --output-dir ./twinizer_report \
  --include-formats svg,html,pdf \
  --analyze-code \
  --analyze-hardware \
  --extract-schematics \
  --build-website \
  --serve \
  --title "KiCad Source Analysis"
```

After running this command:
1. Open your browser to http://localhost:8000
2. Navigate through the generated report
3. Download the PDF version for offline viewing
4. Explore the interactive schematics and code analysis

## Customizing the Report

You can customize the report by creating a configuration file:

```json
// twinizer-report.json
{
  "report": {
    "title": "Custom Project Report",
    "logo": "/path/to/logo.png",
    "theme": "dark",
    "sections": [
      {
        "name": "Overview",
        "enabled": true
      },
      {
        "name": "Code Analysis",
        "enabled": true,
        "subsections": ["metrics", "linting", "security"]
      },
      {
        "name": "Hardware Analysis",
        "enabled": true,
        "subsections": ["schematics", "bom", "connections"]
      },
      {
        "name": "Documentation",
        "enabled": true
      }
    ],
    "formats": ["html", "pdf", "svg"],
    "website": {
      "enabled": true,
      "port": 8080,
      "custom_css": "/path/to/custom.css",
      "custom_js": "/path/to/custom.js"
    }
  }
}
```

Then use it with:

```bash
twinizer generate-report /path/to/project --config twinizer-report.json
```

## Integration with CI/CD

You can integrate the report generation into your CI/CD pipeline:

```yaml
# .github/workflows/twinizer-report.yml
name: Generate Project Report

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install twinizer
    - name: Generate report
      run: |
        twinizer generate-report . \
          --output-dir ./report \
          --include-formats svg,html,pdf \
          --analyze-code \
          --analyze-hardware \
          --extract-schematics \
          --build-website
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./report
```

This will automatically generate and publish the report to GitHub Pages whenever changes are pushed to the main branch.

## Troubleshooting

### Common Issues

1. **Missing dependencies**:
   ```
   pip install twinizer[all]
   ```

2. **Permission errors**:
   ```
   twinizer generate-report /path/to/project --output-dir /path/with/write/permissions
   ```

3. **Memory issues with large projects**:
   ```
   twinizer generate-report /path/to/project --chunk-size 100 --max-files 1000
   ```

4. **Port already in use**:
   ```
   twinizer generate-report /path/to/project --serve --port 8081
   ```

### Getting Help

For more help with report generation:
```bash
twinizer generate-report --help
```
