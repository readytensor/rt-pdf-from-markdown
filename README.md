# Markdown to PDF Converter

A Python utility to convert Markdown documents to PDF with customizable styling and page numbers.

## Prerequisites

- Python 3.6+
- wkhtmltopdf:
  - Windows: Download installer from https://wkhtmltopdf.org/downloads.html
  - macOS: `brew install wkhtmltopdf`
  - Linux: `sudo apt-get install wkhtmltopdf`

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/rt-pdf-from-markdown.git
cd rt-pdf-from-markdown
```

2. Create and activate virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Add your markdown files to the `data/inputs/my_scenario` directory. You may create another scenario folder if needed. Update the `scenario` variable in `src/main.py` accordingly.

2. Run the converter:

```bash
cd src
python main.py
```

3. Find the generated PDFs in `data/outputs/my_scenario`

## Customization

Style settings (fonts, colors, margins, etc.) can be modified in `config/styles.yaml`.

## Project Structure

```
rt-pdf-from-markdown/
├── config/
│   └── styles.yaml     # Style configuration
├── data/
│   ├── inputs/         # Input markdown files inside your scenario folder
│   └── outputs/        # Generated PDFs inside your scenario folder
├── src/
│   ├── main.py
│   └── paths.py
└── requirements.txt
```
