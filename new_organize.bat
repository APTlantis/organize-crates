@echo off
setlocal enabledelayedexpansion

echo Organize Crates - Moving crates from flat directory to hierarchical subdirectories
echo.

REM Default values
set "SOURCE_DIR=E:\\crates-mirror"
set "LOG_PATH=E:\\crates-organize-log.txt"
set "THREADS=4"
set "DRY_RUN="

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="--source-dir" (
    set "SOURCE_DIR=%~2"
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
    echo Usage: organize_crates.bat [options]
    echo.
    echo Options:
    echo   --source-dir ^<path^>   Directory containing crate files (default: E:\\crates-mirror)
    echo   --log-path ^<path^>     Path to log file (default: E:\\crates-organize-log.txt)
    echo   --threads ^<number^>    Number of worker threads (default: 4)
    echo   --dry-run              Run in dry-run mode (no files will be moved)
    echo   --help                 Show this help message
    exit /b 0
)
echo Unknown option: %~1
exit /b 1

:end_parse_args

REM Display the configuration
echo Configuration:
echo   Source Directory: %SOURCE_DIR%
echo   Log Path: %LOG_PATH%
echo   Threads: %THREADS%
if defined DRY_RUN (
    echo   Mode: Dry Run ^(no files will be moved^)
) else (
    echo   Mode: Normal ^(files will be moved^)
)
echo.

REM Confirm before proceeding in normal mode
if not defined DRY_RUN (
    echo WARNING: This will move files from the flat directory to hierarchical subdirectories.
    echo          Files will be organized into two levels of directories (e.g., A/AA-AD/).
    echo          This operation cannot be easily undone.
    echo.
    set /p "CONFIRM=Are you sure you want to proceed? (y/n): "
    if /i not "!CONFIRM!"=="y" (
        echo Operation cancelled.
        exit /b 0
    )
    echo.
)

REM Run the Python script
echo Running organize_crates.py...
if defined DRY_RUN (
    python organize_crates.py --source-dir "%SOURCE_DIR%" --log-path "%LOG_PATH%" --threads %THREADS% --dry-run
) else (
    python organize_crates.py --source-dir "%SOURCE_DIR%" --log-path "%LOG_PATH%" --threads %THREADS%
)

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo Error: organize_crates.py exited with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo.
echo Organization complete. See log file for details: %LOG_PATH%

endlocal
exit /b 0