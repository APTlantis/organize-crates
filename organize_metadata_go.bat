@echo off
setlocal enabledelayedexpansion

REM Organize Metadata Batch Script (Go Version)
REM This script runs the organize_metadata Go executable with the provided arguments

echo Organize Metadata (Go Version) - Moving metadata files from crates.io-index to be alongside their crate files
echo.

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"

REM Default values
set "INDEX_DIR=E:\crates.io-index"
set "MIRROR_DIR=E:\crates-mirror"
set "LOG_PATH=E:\metadata-organize-log.txt"
set "THREADS=%NUMBER_OF_PROCESSORS%"
set "DRY_RUN="

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="--index-dir" (
    set "INDEX_DIR=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--mirror-dir" (
    set "MIRROR_DIR=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--log-path" (
    set "LOG_PATH=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--threads" (
    set "THREADS=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--dry-run" (
    set "DRY_RUN=--dry-run"
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    echo Usage: organize_metadata_go.bat [options]
    echo.
    echo Options:
    echo   --index-dir ^<path^>    Directory containing the crates.io index (default: E:\crates.io-index)
    echo   --mirror-dir ^<path^>   Directory containing the mirrored crates (default: E:\crates-mirror)
    echo   --log-path ^<path^>     Path to log file (default: E:\metadata-organize-log.txt)
    echo   --threads ^<number^>    Number of worker threads (default: number of CPU cores)
    echo   --dry-run              Run in dry-run mode (no files will be created)
    echo   --help                 Show this help message
    exit /b 0
)
echo Unknown option: %~1
exit /b 1

:end_parse_args

REM Display the configuration
echo Configuration:
echo   Index Directory: %INDEX_DIR%
echo   Mirror Directory: %MIRROR_DIR%
echo   Log Path: %LOG_PATH%
echo   Threads: %THREADS%
if defined DRY_RUN (
    echo   Mode: Dry Run ^(no files will be created^)
) else (
    echo   Mode: Normal ^(files will be created^)
)
echo.

REM Confirm before proceeding in normal mode
if not defined DRY_RUN (
    echo WARNING: This will create metadata files alongside crate files in the mirror directory.
    echo          Each metadata file will be named {crate-name}-{version}.metadata.json.
    echo.
    set /p "CONFIRM=Are you sure you want to proceed? (y/n): "
    if /i not "!CONFIRM!"=="y" (
        echo Operation cancelled.
        exit /b 0
    )
    echo.
)

REM Check if the Go executable exists
if not exist "%SCRIPT_DIR%organize_metadata.exe" (
    echo Building Go executable...
    cd "%SCRIPT_DIR%"
    go build -o organize_metadata.exe organize_metadata.go
    if errorlevel 1 (
        echo Failed to build Go executable.
        exit /b 1
    )
    echo Go executable built successfully.
    echo.
)

REM Run the Go executable
echo Running organize_metadata.exe...
if defined DRY_RUN (
    "%SCRIPT_DIR%organize_metadata.exe" --index-dir "%INDEX_DIR%" --mirror-dir "%MIRROR_DIR%" --log-path "%LOG_PATH%" --threads %THREADS% --dry-run
) else (
    "%SCRIPT_DIR%organize_metadata.exe" --index-dir "%INDEX_DIR%" --mirror-dir "%MIRROR_DIR%" --log-path "%LOG_PATH%" --threads %THREADS%
)

REM Check if the executable ran successfully
if errorlevel 1 (
    echo.
    echo Error: organize_metadata.exe exited with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo Organization complete. See log file for details: %LOG_PATH%

endlocal
exit /b 0