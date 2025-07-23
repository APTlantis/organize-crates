# Organize Metadata

This tool organizes metadata files from the crates.io-index repository to be alongside their corresponding crate files in the mirror directory.

## Purpose

The crates.io-index repository contains metadata for all crates published on crates.io. This metadata includes information such as:
- Version information
- Dependencies
- Features
- Whether the crate has been yanked
- Checksums

By default, this metadata is stored in a separate directory structure from the actual crate files. This tool moves the metadata to be alongside the crate files, making it easier to access and use the metadata in conjunction with the crates.

## How It Works

The script:
1. Recursively scans the crates.io-index directory to find all metadata files
2. For each metadata file, extracts the crate name and processes each version
3. For each version, finds the corresponding crate file in the mirror directory
4. Creates a metadata JSON file alongside the crate file

The metadata files are named `{crate-name}-{version}.metadata.json` and are placed in the same directory as their corresponding crate files.

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - tqdm (for progress bar)

## Usage

The easiest way to use the Organize Metadata script is with the provided batch script:

```bash
organize_metadata.bat [options]
```

Alternatively, you can run the Python script directly:

```bash
python organize_metadata.py [options]
```

### Options

- `--index-dir <path>`: Directory containing the crates.io index (default: E:\crates.io-index)
- `--mirror-dir <path>`: Directory containing the mirrored crates (default: E:\crates-mirror)
- `--log-path <path>`: Path to log file (default: E:\metadata-organize-log.txt)
- `--threads <number>`: Number of worker threads (default: 4)
- `--dry-run`: Run in dry-run mode (no files will be created)

### Examples

#### Basic Usage

```bash
organize_metadata.bat
```

This will organize metadata files from the default index directory (E:\crates.io-index) to be alongside their corresponding crate files in the default mirror directory (E:\crates-mirror).

#### Custom Directories

```bash
organize_metadata.bat --index-dir "D:\my-index" --mirror-dir "D:\my-crates"
```

#### Dry Run Mode

```bash
organize_metadata.bat --dry-run
```

This will simulate the organization process without actually creating any files, which is useful for testing.

#### Custom Thread Count

```bash
organize_metadata.bat --threads 8
```

This will use 8 worker threads for parallel processing, which can speed up the organization process on systems with more CPU cores.

## Output

The script creates metadata files alongside their corresponding crate files in the mirror directory. Each metadata file contains the JSON metadata for a specific version of a crate.

The script also generates a log file with detailed information about the organization process, including:
- Number of metadata files processed
- Number of versions processed
- Number of metadata files successfully created
- Any errors encountered during the process

## Notes

- The script only creates metadata files for crates that exist in the mirror directory. If a crate in the index doesn't have a corresponding crate file in the mirror directory, no metadata file will be created for it.
- The script uses the crate name and version to find the corresponding crate file, so it's important that the crate files follow the standard naming convention: `{crate-name}-{version}.crate`.
- The script processes metadata files in parallel using multiple worker threads, which can significantly speed up the organization process.
- The dry-run mode is useful for testing the script without actually creating any files.
