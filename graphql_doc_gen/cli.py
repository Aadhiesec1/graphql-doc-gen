import argparse
import json
import sys
from pathlib import Path

from graphql_doc_gen.renderer import (
    generate_markdown,
    generate_html,
    generate_pdf,
)


def main():
    parser = argparse.ArgumentParser(
        description="GraphQL Schema Documentation Generator"
    )

    parser.add_argument(
        "schema",
        help="Path to GraphQL introspection schema JSON file"
    )

    parser.add_argument(
        "--format",
        choices=["md", "html", "pdf"],
        default="md",
        help="Output format: md | html | pdf"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: schema-docs.<ext>)"
    )

    args = parser.parse_args()

    # ---------------------------------
    # Read schema file
    # ---------------------------------
    try:
        with open(args.schema, "r") as f:
            schema = json.load(f)
    except Exception as e:
        print(f"Error: Failed to read schema file → {e}")
        sys.exit(1)

    # ---------------------------------
    # Determine output file name
    # ---------------------------------
    ext = args.format
    output_path = args.output or f"schema-docs.{ext}"

    # ---------------------------------
    # Markdown output
    # ---------------------------------
    if args.format == "md":
        md = generate_markdown(schema)
        Path(output_path).write_text(md, encoding="utf-8")
        print(f"Markdown generated → {output_path}")
        return

    # ---------------------------------
    # HTML output
    # ---------------------------------
    if args.format == "html":
        html = generate_html(schema)
        Path(output_path).write_text(html, encoding="utf-8")
        print(f"HTML generated → {output_path}")
        return

    # ---------------------------------
    # PDF output (requires optional dependency)
    # ---------------------------------
    if args.format == "pdf":
        html = generate_html(schema)
        try:
            generate_pdf(html, output_path)
        except RuntimeError as e:
            print("\n" + str(e))
            sys.exit(1)

        print(f"PDF generated → {output_path}")
        return
