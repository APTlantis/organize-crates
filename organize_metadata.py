import os
import json
import shutil
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def setup_logging(log_path):
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('organize_metadata')

def find_crate_file(crate_name, version, mirror_dir):
    """Find the corresponding crate file in the mirror directory."""
    # Expected filename pattern: {crate-name}-{version}.crate
    expected_filename = f"{crate_name}-{version}.crate"

    # Search recursively through the mirror directory
    for root, _, files in os.walk(mirror_dir):
        for file in files:
            if file == expected_filename:
                return os.path.join(root, file)

    return None

def process_metadata_file(args):
    """Process a single metadata file from the index."""
    metadata_file, mirror_dir, dry_run = args

    try:
        # Skip .git directory and config.json
        if os.path.basename(metadata_file) in ['.git', 'config.json']:
            return 0, 0

        # Skip directories
        if os.path.isdir(metadata_file):
            return 0, 0

        # Get crate name from the filename
        crate_name = os.path.basename(metadata_file)

        # Read the metadata file
        with open(metadata_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Process each line (each line is a JSON object for a version)
        success_count = 0
        total_count = 0

        for line in lines:
            if not line.strip():
                continue

            # Quick check if the line looks like JSON (starts with { and ends with })
            if not (line.strip().startswith('{') and line.strip().endswith('}')):
                continue

            try:
                # Parse the JSON
                metadata = json.loads(line)
                version = metadata.get('vers')

                if not version:
                    continue

                total_count += 1

                # Find the corresponding crate file
                crate_file_path = find_crate_file(crate_name, version, mirror_dir)

                if not crate_file_path:
                    logging.warning(f"Could not find crate file for {crate_name}-{version}")
                    continue

                # Create metadata file path next to the crate file
                crate_dir = os.path.dirname(crate_file_path)
                metadata_output_path = os.path.join(crate_dir, f"{crate_name}-{version}.metadata.json")

                # Write metadata to file
                if not dry_run:
                    with open(metadata_output_path, 'w', encoding='utf-8') as out_f:
                        json.dump(metadata, out_f, indent=2)

                    success_count += 1
                else:
                    # In dry-run mode, just count
                    success_count += 1

            except json.JSONDecodeError:
                logging.error(f"Error parsing JSON in {metadata_file}: {line}")
            except Exception as e:
                logging.error(f"Error processing metadata for {crate_name}: {e}")

        return success_count, total_count

    except Exception as e:
        logging.error(f"Error processing metadata file {metadata_file}: {e}")
        return 0, 0

def organize_metadata(index_dir, mirror_dir, max_workers=4, dry_run=False):
    """Organize metadata files from index directory to be alongside crate files."""
    # Find all metadata files in the index directory
    metadata_files = []

    for root, _, files in os.walk(index_dir):
        # Skip common directories that might contain non-metadata files
        if any(d in root for d in ['.git', '.venv', 'site-packages', 'pip', 'python', '__pycache__']):
            continue

        for file in files:
            # Skip config.json and common non-metadata file types
            if file == 'config.json':
                continue

            # Skip Python files and other non-metadata files
            if file.endswith(('.py', '.pyc', '.pyd', '.dll', '.exe', '.bat', '.sh', '.md', '.txt', '.html')):
                continue

            metadata_files.append(os.path.join(root, file))

    total_files = len(metadata_files)
    logging.info(f"Found {total_files} metadata files to process")

    if dry_run:
        logging.info("DRY RUN: No files will be created")

    # Process metadata files in parallel
    success_count = 0
    total_versions = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        args = [(file, mirror_dir, dry_run) for file in metadata_files]
        results = list(tqdm(executor.map(process_metadata_file, args), total=len(args), desc="Processing metadata files"))

        for s, t in results:
            success_count += s
            total_versions += t

    return success_count, total_versions

def main():
    parser = argparse.ArgumentParser(description='Organize metadata files from crates.io-index to be alongside their crate files')
    parser.add_argument('--index-dir', default='E:\\crates.io-index', help='Directory containing the crates.io index')
    parser.add_argument('--mirror-dir', default='E:\\crates-mirror', help='Directory containing the mirrored crates')
    parser.add_argument('--log-path', default='E:\\metadata-organize-log.txt', help='Path to log file')
    parser.add_argument('--threads', type=int, default=4, help='Number of worker threads')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no files will be created)')

    args = parser.parse_args()

    logger = setup_logging(args.log_path)

    logger.info(f"Starting organization of metadata from {args.index_dir} to {args.mirror_dir}")

    if not os.path.exists(args.index_dir):
        logger.error(f"Index directory {args.index_dir} does not exist")
        return 1

    if not os.path.exists(args.mirror_dir):
        logger.error(f"Mirror directory {args.mirror_dir} does not exist")
        return 1

    success_count, total_versions = organize_metadata(
        args.index_dir,
        args.mirror_dir,
        max_workers=args.threads,
        dry_run=args.dry_run
    )

    if args.dry_run:
        logger.info(f"DRY RUN COMPLETE: Would have organized {success_count} out of {total_versions} version metadata files")
    else:
        logger.info(f"Organization complete: {success_count} out of {total_versions} version metadata files successfully organized")

    return 0

if __name__ == "__main__":
    exit(main())
