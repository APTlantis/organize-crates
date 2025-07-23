# Organize Crates

This script organizes Rust crates from a flat directory structure into a hierarchical directory structure with two levels of subdirectories.

## Purpose

When mirroring crates.io, all crate files (approximately 1.5 million) are downloaded to a single flat directory. This script reorganizes these files into a hierarchical structure:

1. First-level directories (A-Z, 0-9, OTHER) based on the first character of each filename
2. Second-level directories (AA-AD, AE-AH, etc.) based on the first two characters of each filename

This organization significantly reduces the number of files in each directory, making file browsing and management much more efficient.

## Features

- Organizes files into a hierarchical directory structure:
  - First-level directories (A-Z, 0-9, OTHER) based on the first character
  - Second-level directories (AA-AD, AE-AH, etc.) based on the first two characters
- Intelligent grouping of second-level directories to balance file distribution
- Multi-threaded file moving for efficiency
- Dry-run mode for testing without actually moving files
- Comprehensive logging with counts for each directory level
- Progress bar to track file movement
- Error handling to catch and log any issues

## Usage

```bash
python organize_crates.py [options]
```

### Options

- `--source-dir`: Directory containing the crate files (default: "E:\crates-mirror")
- `--log-path`: Path to log file (default: "E:\crates-organize-log.txt")
- `--threads`: Number of worker threads (default: 4)
- `--dry-run`: Run in dry-run mode (no files will be moved)

## Examples

### Dry Run

To see what would happen without actually moving any files:

```bash
python organize_crates.py --dry-run
```

This will show how many files would be moved to each directory without actually moving them.

### Organize Files with Default Settings

To organize files using the default settings:

```bash
python organize_crates.py
```

This will organize all files from E:\crates-mirror into alphabetical subdirectories.

### Customize Thread Count

To use more threads for faster processing:

```bash
python organize_crates.py --threads 8
```

### Specify a Different Source Directory

To organize files from a different directory:

```bash
python organize_crates.py --source-dir "D:\my-crates-mirror"
```

## Directory Structure

After running the script, the source directory will have the following hierarchical structure:

```
source-dir/
├── A/
│   ├── AA-AD/
│   │   ├── aardvark-1.0.0.crate
│   │   ├── abstract-0.1.2.crate
│   │   └── ...
│   ├── AE-AH/
│   │   ├── aerial-2.0.0.crate
│   │   ├── affix-1.0.3.crate
│   │   └── ...
│   ├── AI-AL/
│   │   └── ...
│   └── ...
├── B/
│   ├── BA-BD/
│   │   ├── babylon-0.3.0.crate
│   │   ├── backup-1.0.0.crate
│   │   └── ...
│   ├── BE-BH/
│   │   └── ...
│   └── ...
...
├── Z/
│   ├── ZA-ZD/
│   │   └── ...
│   └── ...
├── 0-9/
│   ├── 0-2/
│   │   ├── 1password-0.2.1.crate
│   │   ├── 2d-graphics-0.1.0.crate
│   │   └── ...
│   ├── 3-5/
│   │   └── ...
│   └── 6-9/
│       └── ...
└── OTHER/
    └── OTHER/
        ├── _special-crate-1.0.0.crate
        └── ...
```

This hierarchical structure significantly reduces the number of files in each directory, making file browsing and management much more efficient.

## Requirements

- Python 3.6 or higher
- tqdm (Python package for progress bars)

## Notes

- The script only moves files, not directories.
- Files are categorized based on the first two characters of their filename:
  - First-level directory is determined by the first character (A-Z, 0-9, OTHER)
  - Second-level directory is determined by the first two characters, grouped into ranges (AA-AD, AE-AH, etc.)
- For files with only one character, they are placed in the appropriate first group of the first-level directory
- The script automatically creates all necessary subdirectories if they don't exist
- A comprehensive log file is created to track the progress and any errors
- The dry run mode provides detailed counts for both first-level and second-level directories
