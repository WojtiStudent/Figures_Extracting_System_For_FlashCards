"""
Script template for processing images in a folder.

This script demonstrates how to use the components from the src/ directory
to process multiple images in a folder.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from src.system import System


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Process images in a folder using the figure extraction pipeline"
    )
    parser.add_argument(
        "-i", "--input_folder",
        type=str,
        help="Path to the input folder containing images"
    )
    parser.add_argument(
        "-o", "--output_folder",
        type=str,
        default="output",
        help="Output folder path (default: 'output')"
    )
    return parser


def process_folder(
    source_folder: Path,
    output_folder: Path,
) -> bool:
    """Process a single image through the pipeline."""
    load_dotenv(".env", override=True)
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    model = os.getenv("OPENAI_MODEL")
    system = System(endpoint, key, model, output_folder)
    system.run_folder(source_folder)


def main():
    """Main function to run the script."""
    # Parse command line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Validate input folder
    input_folder = Path(args.input_folder)
    if not input_folder.exists():
        print(f"Error: Input folder '{args.input_folder}' does not exist.")
        sys.exit(1)
    
    process_folder(input_folder, args.output)
    

if __name__ == "__main__":
    main()
