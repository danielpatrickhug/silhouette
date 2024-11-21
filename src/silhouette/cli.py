# src/silhouette/cli.py

import argparse
import os
from silhouette.code_processor import CodeProcessor

def main():
    parser = argparse.ArgumentParser(
        description="Silhouette: Enhance your Python code with docstrings and type hints."
    )
    parser.add_argument(
        "path",
        help="Path to the Python file or directory to process."
    )
    parser.add_argument(
        "-d", "--docstrings",
        action="store_true",
        help="Add docstrings to functions and classes."
    )
    parser.add_argument(
        "-t", "--type-hints",
        action="store_true",
        help="Add type hints to function signatures."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory or file. Defaults to overwriting the input files."
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively process directories."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity."
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key. If not provided, the OPENAI_API_KEY environment variable will be used."
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.docstrings and not args.type_hints:
        parser.error("At least one of --docstrings or --type-hints must be specified.")

    if not os.path.exists(args.path):
        parser.error(f"The path {args.path} does not exist.")

    # Get the API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        parser.error("An OpenAI API key must be provided via --api-key or the OPENAI_API_KEY environment variable.")

    # Collect files to process
    files_to_process = []
    if os.path.isfile(args.path):
        if args.path.endswith(".py"):
            files_to_process.append(args.path)
        else:
            parser.error("The specified file is not a Python (.py) file.")
    elif os.path.isdir(args.path):
        if args.recursive:
            for root, _, files in os.walk(args.path):
                for file in files:
                    if file.endswith(".py"):
                        files_to_process.append(os.path.join(root, file))
        else:
            for file in os.listdir(args.path):
                if file.endswith(".py"):
                    files_to_process.append(os.path.join(args.path, file))
    else:
        parser.error(f"The path {args.path} is neither a file nor a directory.")

    if args.verbose:
        print(f"Processing {len(files_to_process)} files...")

    for file_path in files_to_process:
        if args.verbose:
            print(f"Processing {file_path}...")

        with open(file_path, 'r') as f:
            source_code = f.read()

        processor = CodeProcessor(
            source_code=source_code,
            api_key=api_key,
            add_docstrings=args.docstrings,
            add_type_hints=args.type_hints,
            verbose=args.verbose
        )

        modified_code = processor.process()

        # Determine output path
        output_path = file_path
        if args.output:
            if os.path.isdir(args.output):
                relative_path = os.path.relpath(file_path, args.path)
                output_path = os.path.join(args.output, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                output_path = args.output

        # Write the modified code to the output file
        with open(output_path, 'w') as f:
            f.write(modified_code)

    if args.verbose:
        print("Processing completed.")

if __name__ == "__main__":
    main()
