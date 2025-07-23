import os
import shutil
import logging
import argparse
import string
import itertools
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
    return logging.getLogger('organize_crates')

def get_letter_groups():
    """Define letter groups for second-level directories."""
    # Define letter groups for A-Z
    letter_groups = {}

    # For A-Z, create groups like AA-AD, AE-AH, etc.
    for first_letter in string.ascii_uppercase:
        # Create groups of 3-4 letters for second letter
        second_letters = string.ascii_uppercase
        groups = []

        # Group second letters in chunks of 3-4
        chunk_size = 4  # Can be adjusted based on expected distribution
        for i in range(0, len(second_letters), chunk_size):
            chunk = second_letters[i:i+chunk_size]
            if chunk:  # Ensure we don't add empty chunks
                start = chunk[0]
                end = chunk[-1]
                group_name = f"{first_letter}{start}-{first_letter}{end}"
                group_prefix = f"{first_letter}"
                group_range = chunk
                groups.append((group_name, group_prefix, group_range))

        letter_groups[first_letter] = groups

    # For 0-9, create groups like 0-2, 3-5, 6-9
    number_groups = [
        ("0-2", "", ["0", "1", "2"]),
        ("3-5", "", ["3", "4", "5"]),
        ("6-9", "", ["6", "7", "8", "9"])
    ]
    letter_groups["0-9"] = number_groups

    # For OTHER, just one group
    letter_groups["OTHER"] = [("OTHER", "", [])]

    return letter_groups

def create_directories(base_dir):
    """Create hierarchical directory structure."""
    letter_groups = get_letter_groups()

    # Create first-level directories (A-Z, 0-9, OTHER)
    for first_level in list(string.ascii_uppercase) + ["0-9", "OTHER"]:
        first_dir = os.path.join(base_dir, first_level)
        if not os.path.exists(first_dir):
            os.makedirs(first_dir)
            logging.info(f"Created directory: {first_dir}")

        # Create second-level directories within each first-level directory
        for group_name, _, _ in letter_groups[first_level]:
            second_dir = os.path.join(first_dir, group_name)
            if not os.path.exists(second_dir):
                os.makedirs(second_dir)
                logging.info(f"Created directory: {second_dir}")

def get_target_directory(filename, base_dir):
    """Determine the target directory for a file based on its first two characters."""
    if not filename:
        return os.path.join(base_dir, "OTHER", "OTHER")

    # Get the first character to determine the first-level directory
    first_char = filename[0].upper()

    # Determine first-level directory
    if first_char in string.ascii_uppercase:
        first_level = first_char
    elif first_char.isdigit():
        first_level = "0-9"
    else:
        first_level = "OTHER"

    # Get letter groups for determining second-level directory
    letter_groups = get_letter_groups()

    # For files starting with letters (A-Z)
    if first_level in string.ascii_uppercase:
        # Get the second character if it exists, otherwise use 'A'
        second_char = filename[1].upper() if len(filename) > 1 else 'A'

        # Find the appropriate group for the second character
        # Only use second_char for grouping if it's a letter
        if second_char in string.ascii_uppercase:
            for group_name, prefix, range_chars in letter_groups[first_level]:
                if second_char in range_chars:
                    return os.path.join(base_dir, first_level, group_name)

        # If second character is not a letter or no matching group found,
        # use the first group as default
        return os.path.join(base_dir, first_level, letter_groups[first_level][0][0])

    # For files starting with numbers (0-9)
    elif first_level == "0-9":
        for group_name, _, range_chars in letter_groups["0-9"]:
            if first_char in range_chars:
                return os.path.join(base_dir, "0-9", group_name)

        # Default to first number group if no match
        return os.path.join(base_dir, "0-9", letter_groups["0-9"][0][0])

    # For files starting with other characters
    else:
        return os.path.join(base_dir, "OTHER", "OTHER")

def move_file(args):
    """Move a file to its target directory."""
    file_path, target_dir = args
    filename = os.path.basename(file_path)
    target_path = os.path.join(target_dir, filename)

    try:
        shutil.move(file_path, target_path)
        return True
    except Exception as e:
        logging.error(f"Error moving {file_path} to {target_path}: {e}")
        return False

def organize_files(source_dir, max_workers=4, dry_run=False):
    """Organize files from flat directory into hierarchical subdirectories."""
    # Get all files in the source directory (non-recursive)
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    total_files = len(files)

    logging.info(f"Found {total_files} files to organize")

    if dry_run:
        logging.info("DRY RUN: No files will be moved")

    # Create target directories if they don't exist
    if not dry_run:
        create_directories(source_dir)

    # Prepare arguments for move_file function
    move_args = []
    for filename in files:
        file_path = os.path.join(source_dir, filename)
        target_dir = get_target_directory(filename, source_dir)
        move_args.append((file_path, target_dir))

    # Move files in parallel
    success_count = 0
    if not dry_run:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(tqdm(executor.map(move_file, move_args), total=len(move_args), desc="Moving files"))
            success_count = sum(results)
    else:
        # In dry run mode, count how many files would go to each directory
        # Track both first-level and second-level directories
        first_level_counts = {}
        second_level_counts = {}

        for _, target_dir in move_args:
            # Extract first and second level directories from the path
            path_parts = os.path.normpath(target_dir).split(os.sep)
            if len(path_parts) >= 2:
                first_level = path_parts[-2]  # Second-to-last part is the first-level dir
                second_level = path_parts[-1]  # Last part is the second-level dir

                # Update counts
                first_level_counts[first_level] = first_level_counts.get(first_level, 0) + 1
                second_level_key = f"{first_level}/{second_level}"
                second_level_counts[second_level_key] = second_level_counts.get(second_level_key, 0) + 1

        # Log first-level directory counts
        logging.info("First-level directory counts:")
        for dir_name, count in sorted(first_level_counts.items()):
            logging.info(f"  {dir_name}/: {count} files")

        # Log second-level directory counts
        logging.info("Second-level directory counts:")
        for dir_key, count in sorted(second_level_counts.items()):
            logging.info(f"  {dir_key}/: {count} files")

    if not dry_run:
        logging.info(f"Successfully moved {success_count} out of {total_files} files")

    return success_count, total_files

def main():
    parser = argparse.ArgumentParser(description='Organize crates from flat directory into hierarchical subdirectories')
    parser.add_argument('--source-dir', default='E:\\crates-mirror', help='Source directory containing crate files')
    parser.add_argument('--log-path', default='E:\\crates-organize-log.txt', help='Path to log file')
    parser.add_argument('--threads', type=int, default=4, help='Number of worker threads')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no files will be moved)')

    args = parser.parse_args()

    logger = setup_logging(args.log_path)

    logger.info(f"Starting organization of crates in {args.source_dir}")

    if not os.path.exists(args.source_dir):
        logger.error(f"Source directory {args.source_dir} does not exist")
        return 1

    success_count, total_files = organize_files(
        args.source_dir, 
        max_workers=args.threads,
        dry_run=args.dry_run
    )

    if args.dry_run:
        logger.info(f"DRY RUN COMPLETE: Would have organized {total_files} files")
    else:
        logger.info(f"Organization complete: {success_count}/{total_files} files successfully organized")

    return 0

if __name__ == "__main__":
    exit(main())
