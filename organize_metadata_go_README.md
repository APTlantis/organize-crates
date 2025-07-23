# Organize Metadata (Go Version)

This is a Go implementation of the organize_metadata.py script, designed to be significantly faster and more efficient when processing large numbers of files.

## Purpose

The crates.io-index repository contains metadata for all crates published on crates.io. This metadata includes information such as:
- Version information
- Dependencies
- Features
- Whether the crate has been yanked
- Checksums

By default, this metadata is stored in a separate directory structure from the actual crate files. This tool moves the metadata to be alongside the crate files, making it easier to access and use the metadata in conjunction with the crates.

## Performance Improvements

The Go version offers several significant performance improvements over the Python version:

1. **Pre-indexing of crate files**: Instead of searching the entire mirror directory for each crate version, the Go version builds an index of all crate files at startup, which makes lookups much faster.

2. **Efficient parallelism**: The Go version uses goroutines for parallel processing, which are more lightweight than Python threads and can better utilize multiple CPU cores.

3. **Default thread count**: The Go version defaults to using all available CPU cores, which maximizes performance on multi-core systems.

4. **Regular progress updates**: The Go version provides progress updates both by count (every 1000 files) and by time (every second), giving better visibility into the processing status.

5. **More efficient file operations**: Go's file operations are generally more efficient than Python's, especially for large numbers of files.

## Prerequisites

- Go 1.16 or higher (for building the executable)
- Windows operating system (for the batch file)

## Usage

The easiest way to use the Organize Metadata Go script is with the provided batch script:

```bash
organize_metadata_go.bat [options]
```

Alternatively, you can build and run the Go executable directly:

```bash
go build -o organize_metadata.exe organize_metadata.go
organize_metadata.exe [options]
```

### Options

- `--index-dir <path>`: Directory containing the crates.io index (default: E:\crates.io-index)
- `--mirror-dir <path>`: Directory containing the mirrored crates (default: E:\crates-mirror)
- `--log-path <path>`: Path to log file (default: E:\metadata-organize-log.txt)
- `--threads <number>`: Number of worker threads (default: number of CPU cores)
- `--dry-run`: Run in dry-run mode (no files will be created)

### Examples

#### Basic Usage

```bash
organize_metadata_go.bat
```

This will organize metadata files from the default index directory (E:\crates.io-index) to be alongside their corresponding crate files in the default mirror directory (E:\crates-mirror).

#### Custom Directories

```bash
organize_metadata_go.bat --index-dir "D:\my-index" --mirror-dir "D:\my-crates"
```

#### Dry Run Mode

```bash
organize_metadata_go.bat --dry-run
```

This will simulate the organization process without actually creating any files, which is useful for testing.

#### Custom Thread Count

```bash
organize_metadata_go.bat --threads 16
```

This will use 16 worker threads for parallel processing, which can speed up the organization process on systems with more CPU cores.

## Output

The script creates metadata files alongside their corresponding crate files in the mirror directory. Each metadata file contains the JSON metadata for a specific version of a crate.

The script also generates a log file with detailed information about the organization process, including:
- Number of metadata files processed
- Number of versions processed
- Number of metadata files successfully created
- Any errors encountered during the process
- Total processing time

## Notes

- The script only creates metadata files for crates that exist in the mirror directory. If a crate in the index doesn't have a corresponding crate file in the mirror directory, no metadata file will be created for it.
- The script uses the crate name and version to find the corresponding crate file, so it's important that the crate files follow the standard naming convention: `{crate-name}-{version}.crate`.
- The script processes metadata files in parallel using multiple worker threads, which can significantly speed up the organization process.
- The dry-run mode is useful for testing the script without actually creating any files.
- The Go version is particularly well-suited for processing large numbers of files (1.8 million+) due to its performance optimizations.