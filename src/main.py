import markdown
import pdfkit
import tempfile
import os
import sys
import platform
import subprocess
import yaml
from pathlib import Path
from typing import List, Optional, Dict


def load_config(config_path: str) -> Dict:
    """Load YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config file: {str(e)}") from e


def generate_css(config: Dict) -> str:
    """Generate CSS from configuration."""
    return f"""
        body {{
            font-family: {config['fonts']['main']['family']};
            font-size: {config['fonts']['main']['size']};
            line-height: {config['fonts']['main']['line_height']};
            margin: {config['document']['margins']['top']};
            background-color: {config['colors']['background']};
            color: {config['colors']['text']};
        }}
        code {{
            font-family: {config['fonts']['code']['family']};
            font-size: {config['fonts']['code']['size']};
            background-color: {config['fonts']['code']['background']};
            padding: {config['fonts']['code']['padding']};
            border-radius: {config['fonts']['code']['border_radius']};
        }}
        pre {{
            font-family: {config['fonts']['pre']['family']};
            font-size: {config['fonts']['pre']['size']};
            background-color: {config['fonts']['pre']['background']};
            padding: {config['fonts']['pre']['padding']};
            border-radius: {config['fonts']['pre']['border_radius']};
            white-space: pre-wrap;
        }}
        table {{
            border-collapse: collapse;
            margin: {config['tables']['margin']};
            width: 100%;
        }}
        th, td {{
            border: {config['tables']['border_width']} solid {config['colors']['table_border']};
            padding: {config['tables']['cell_padding']};
            text-align: left;
        }}
        th {{
            background-color: {config['colors']['table_header_bg']};
        }}
        img {{
            max-width: {config['images']['max_width']};
            height: auto;
        }}
    """


def find_wkhtmltopdf() -> Optional[str]:
    """
    Find wkhtmltopdf executable on the system based on OS.
    Returns:
        Optional[str]: Path to wkhtmltopdf if found, None otherwise
    """
    system = platform.system().lower()

    if system == "windows":
        common_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
            os.path.join(sys.prefix, "Scripts", "wkhtmltopdf.exe"),
        ]
        search_command = "where"
    else:  # macOS and Linux
        common_paths = [
            "/usr/local/bin/wkhtmltopdf",
            "/usr/bin/wkhtmltopdf",
            "/opt/homebrew/bin/wkhtmltopdf",  # M1 Macs
        ]
        search_command = "which"

    # First check if wkhtmltopdf is in PATH
    try:
        result = subprocess.run(
            [search_command, "wkhtmltopdf"],
            capture_output=True,
            text=True,
            shell=True if system == "windows" else False,
        )

        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    # Check common installation paths
    for path in common_paths:
        if os.path.exists(path):
            return path

    # Last resort: try to find it anywhere in Program Files (Windows only)
    if system == "windows":
        program_files = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ]

        for root_dir in program_files:
            for root, dirs, files in os.walk(root_dir):
                if "wkhtmltopdf.exe" in files:
                    return os.path.join(root, "wkhtmltopdf.exe")

    return None


def find_markdown_files(directory: str) -> List[Path]:
    """Find all markdown files in directory."""
    markdown_files = []
    for ext in [".md", ".markdown"]:
        markdown_files.extend(Path(directory).rglob(f"*{ext}"))
    return markdown_files


def check_file_writable(file_path: str) -> bool:
    """Check if a file is writable or can be created."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "a"):
                return True
        except IOError:
            return False
    else:
        # Check if the directory is writable
        directory = os.path.dirname(file_path)
        try:
            with tempfile.NamedTemporaryFile(dir=directory) as tmp:
                return True
        except IOError:
            return False


def convert_markdown_to_pdf(input_path: str, output_path: str, wkhtmltopdf_path: str, config: Dict) -> None:
    """Convert a markdown file to PDF using the provided configuration."""
    try:
        # First check if we can write to the output file
        if not check_file_writable(output_path):
            raise PermissionError(
                f"Cannot write to {output_path}. Please make sure the file is not open in another program."
            )

        # Read the markdown file
        with open(input_path, 'r', encoding='utf-8') as md_file:
            markdown_content = md_file.read()
        
        # Convert markdown to HTML with extended features
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'codehilite', 'nl2br']
        )
        
        # Generate CSS from config
        css = generate_css(config)
        
        # Create HTML with styling
        styled_html = f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {css}
        </style>
    </head>
    <body>
        {html_content}
    </body>
</html>"""
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as temp_html:
            temp_html.write(styled_html)
            temp_html_path = temp_html.name

        try:
            # Configure pdfkit with options from config
            config_pdf = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            
            # Base options
            options = {
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
                'print-media-type': None,
                'page-size': config['document']['page_size'],
                'margin-top': config['document']['margins']['top'],
                'margin-right': config['document']['margins']['right'],
                'margin-bottom': config['document']['margins']['bottom'],
                'margin-left': config['document']['margins']['left'],
                'no-outline': None,
                'enable-smart-shrinking': None,
                'footer-right': 'Page [page]',
                'footer-font-name': 'Arial',
                'footer-font-size': '10',
                'footer-spacing': '5'
            }
            
            pdfkit.from_file(temp_html_path, output_path, configuration=config_pdf, options=options)
        finally:
            # Clean up temporary file
            os.unlink(temp_html_path)
            
        print(f"✓ {input_path}")
        
    except PermissionError as e:
        raise PermissionError(str(e)) from e
    except Exception as e:
        raise Exception(f"Error converting markdown to PDF: {str(e)}") from e

def process_directory(input_dir: str, output_dir: str, config_path: str) -> None:
    """Process all markdown files in directory using the specified configuration."""
    # Load configuration
    config = load_config(config_path)

    # Find wkhtmltopdf
    wkhtmltopdf_path = find_wkhtmltopdf()
    if not wkhtmltopdf_path:
        print("Error: wkhtmltopdf not found. Please install it:")
        print("- Windows: Download from https://wkhtmltopdf.org/downloads.html")
        print("- macOS: Run 'brew install wkhtmltopdf'")
        print("- Linux: Run 'sudo apt-get install wkhtmltopdf' or equivalent")
        sys.exit(1)

    # Find and process markdown files
    markdown_files = find_markdown_files(input_dir)
    if not markdown_files:
        print(f"No markdown files found in {input_dir}")
        return

    print(f"Converting {len(markdown_files)} files...")

    for md_file in markdown_files:
        rel_path = md_file.relative_to(input_dir)
        output_path = Path(output_dir) / rel_path.with_suffix(".pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            convert_markdown_to_pdf(
                str(md_file), str(output_path), wkhtmltopdf_path, config
            )
        except Exception as e:
            print(f"Error processing {md_file}: {str(e)}")

    print("\nDone!")


if __name__ == "__main__":
    import paths

    scenario = "my_scenario"

    input_dir = os.path.join(paths.INPUTS_DIR, scenario)
    output_dir = os.path.join(paths.OUTPUTS_DIR, scenario)
    config_path = os.path.join(paths.CONFIG_DIR, "styles.yaml")

    os.makedirs(output_dir, exist_ok=True)

    process_directory(input_dir, output_dir, config_path)
