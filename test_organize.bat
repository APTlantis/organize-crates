@echo off
setlocal enabledelayedexpansion

echo Testing organize_crates.py...

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
echo Unknown option: %~1
exit /b 1

:end_parse_args

REM Run the Python script
if defined DRY_RUN (
    python organize_crates.py --source-dir "%SOURCE_DIR%" --log-path "%LOG_PATH%" --threads %THREADS% --dry-run
) else (
    python organize_crates.py --source-dir "%SOURCE_DIR%" --log-path "%LOG_PATH%" --threads %THREADS%
)

echo Done.
endlocal
