// =========================================================
// Script Name: organize_metadata.go
// Description: Organizes Rust crate metadata files and links them to actual crate files
// Author: APTlantis Team
// Creation Date: 2025-05-31
// Last Modified: 2025-05-31
//
// Dependencies:
// - None (standard library only)
//
// Usage:
//   go run organize_metadata.go [options]
//
// Options:
//   -index string    Directory containing metadata index files (default "./index")
//   -mirror string   Directory containing mirrored crate files (default "./mirror")
//   -workers int     Number of parallel workers (default 4)
//   -dry-run         Dry run (don't actually modify files)
//   -log string      Path to log file (default "organize_metadata.log")
// =========================================================

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

// MetadataEntry represents a single entry in a metadata file
type MetadataEntry map[string]interface{}

// FileIndex is a map of filename to full path
type FileIndex map[string]string

// Logger for both file and console output
type Logger struct {
	fileLogger    *log.Logger
	consoleLogger *log.Logger
}

// NewLogger creates a new dual logger
func NewLogger(logPath string) (*Logger, error) {
	// Create log file
	logFile, err := os.Create(logPath)
	if err != nil {
		return nil, fmt.Errorf("failed to create log file: %v", err)
	}

	// Create loggers
	fileLogger := log.New(logFile, "", log.LstdFlags)
	consoleLogger := log.New(os.Stdout, "", log.LstdFlags)

	return &Logger{
		fileLogger:    fileLogger,
		consoleLogger: consoleLogger,
	}, nil
}

// Info logs an info message to both file and console
func (l *Logger) Info(format string, v ...interface{}) {
	msg := fmt.Sprintf(format, v...)
	l.fileLogger.Printf("INFO - %s", msg)
	l.consoleLogger.Printf("INFO - %s", msg)
}

// Warning logs a warning message to both file and console
func (l *Logger) Warning(format string, v ...interface{}) {
	msg := fmt.Sprintf(format, v...)
	l.fileLogger.Printf("WARNING - %s", msg)
	l.consoleLogger.Printf("WARNING - %s", msg)
}

// Error logs an error message to both file and console
func (l *Logger) Error(format string, v ...interface{}) {
	msg := fmt.Sprintf(format, v...)
	l.fileLogger.Printf("ERROR - %s", msg)
	l.consoleLogger.Printf("ERROR - %s", msg)
}

// BuildCrateFileIndex builds an index of all crate files in the mirror directory
func BuildCrateFileIndex(mirrorDir string, logger *Logger) (FileIndex, error) {
	logger.Info("Building crate file index from %s...", mirrorDir)
	startTime := time.Now()

	index := make(FileIndex)

	err := filepath.Walk(mirrorDir, func(path string, info fs.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories
		if info.IsDir() {
			return nil
		}

		// Only index .crate files
		if strings.HasSuffix(info.Name(), ".crate") {
			index[info.Name()] = path
		}

		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("error walking mirror directory: %v", err)
	}

	logger.Info("Built index of %d crate files in %v", len(index), time.Since(startTime))
	return index, nil
}

// ProcessMetadataFile processes a single metadata file
func ProcessMetadataFile(metadataFilePath string, crateIndex FileIndex, mirrorDir string, dryRun bool, logger *Logger) (int, int) {
	// Skip .git directory and config.json
	baseName := filepath.Base(metadataFilePath)
	if baseName == ".git" || baseName == "config.json" {
		return 0, 0
	}

	// Get crate name from the filename
	crateName := baseName

	// Read the metadata file
	content, err := ioutil.ReadFile(metadataFilePath)
	if err != nil {
		logger.Error("Failed to read metadata file %s: %v", metadataFilePath, err)
		return 0, 0
	}

	// Split content into lines
	lines := strings.Split(string(content), "\n")

	successCount := 0
	totalCount := 0

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// Quick check if the line looks like JSON
		if !strings.HasPrefix(line, "{") || !strings.HasSuffix(line, "}") {
			continue
		}

		// Parse the JSON
		var metadata MetadataEntry
		if err := json.Unmarshal([]byte(line), &metadata); err != nil {
			logger.Error("Error parsing JSON in %s: %v", metadataFilePath, err)
			continue
		}

		// Get version
		version, ok := metadata["vers"].(string)
		if !ok || version == "" {
			continue
		}

		totalCount++

		// Find the corresponding crate file
		expectedFilename := fmt.Sprintf("%s-%s.crate", crateName, version)
		crateFilePath, exists := crateIndex[expectedFilename]

		if !exists {
			logger.Warning("Could not find crate file for %s-%s", crateName, version)
			continue
		}

		// Create metadata file path next to the crate file
		crateDir := filepath.Dir(crateFilePath)
		metadataOutputPath := filepath.Join(crateDir, fmt.Sprintf("%s-%s.metadata.json", crateName, version))

		// Write metadata to file
		if !dryRun {
			// Marshal with indentation for readability
			metadataJSON, err := json.MarshalIndent(metadata, "", "  ")
			if err != nil {
				logger.Error("Error marshaling JSON for %s-%s: %v", crateName, version, err)
				continue
			}

			if err := ioutil.WriteFile(metadataOutputPath, metadataJSON, 0644); err != nil {
				logger.Error("Error writing metadata file for %s-%s: %v", crateName, version, err)
				continue
			}

			successCount++
		} else {
			// In dry-run mode, just count
			successCount++
		}
	}

	return successCount, totalCount
}

// FindMetadataFiles finds all metadata files in the index directory
func FindMetadataFiles(indexDir string, logger *Logger) ([]string, error) {
	logger.Info("Finding metadata files in %s...", indexDir)
	startTime := time.Now()

	var metadataFiles []string

	err := filepath.Walk(indexDir, func(path string, info fs.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories
		if info.IsDir() {
			// Skip common directories that might contain non-metadata files
			if strings.Contains(path, ".git") ||
				strings.Contains(path, ".venv") ||
				strings.Contains(path, "site-packages") ||
				strings.Contains(path, "pip") ||
				strings.Contains(path, "python") ||
				strings.Contains(path, "__pycache__") {
				return filepath.SkipDir
			}
			return nil
		}

		// Skip config.json and common non-metadata file types
		if info.Name() == "config.json" {
			return nil
		}

		// Skip Python files and other non-metadata files
		if strings.HasSuffix(info.Name(), ".py") ||
			strings.HasSuffix(info.Name(), ".pyc") ||
			strings.HasSuffix(info.Name(), ".pyd") ||
			strings.HasSuffix(info.Name(), ".dll") ||
			strings.HasSuffix(info.Name(), ".exe") ||
			strings.HasSuffix(info.Name(), ".bat") ||
			strings.HasSuffix(info.Name(), ".sh") ||
			strings.HasSuffix(info.Name(), ".md") ||
			strings.HasSuffix(info.Name(), ".txt") ||
			strings.HasSuffix(info.Name(), ".html") {
			return nil
		}

		metadataFiles = append(metadataFiles, path)
		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("error walking index directory: %v", err)
	}

	logger.Info("Found %d metadata files in %v", len(metadataFiles), time.Since(startTime))
	return metadataFiles, nil
}

// Worker represents a worker that processes metadata files
type Worker struct {
	id            int
	metadataFiles chan string
	crateIndex    FileIndex
	mirrorDir     string
	dryRun        bool
	wg            *sync.WaitGroup
	logger        *Logger
	results       chan [2]int
}

// NewWorker creates a new worker
func NewWorker(id int, metadataFiles chan string, crateIndex FileIndex, mirrorDir string, dryRun bool, wg *sync.WaitGroup, logger *Logger, results chan [2]int) *Worker {
	return &Worker{
		id:            id,
		metadataFiles: metadataFiles,
		crateIndex:    crateIndex,
		mirrorDir:     mirrorDir,
		dryRun:        dryRun,
		wg:            wg,
		logger:        logger,
		results:       results,
	}
}

// Start starts the worker
func (w *Worker) Start() {
	defer w.wg.Done()

	for metadataFile := range w.metadataFiles {
		success, total := ProcessMetadataFile(metadataFile, w.crateIndex, w.mirrorDir, w.dryRun, w.logger)
		w.results <- [2]int{success, total}
	}
}

// OrganizeMetadata organizes metadata files from index directory to be alongside crate files
func OrganizeMetadata(indexDir, mirrorDir string, numWorkers int, dryRun bool, logger *Logger) (int, int, error) {
	// Build index of crate files
	crateIndex, err := BuildCrateFileIndex(mirrorDir, logger)
	if err != nil {
		return 0, 0, fmt.Errorf("failed to build crate file index: %v", err)
	}

	// Find all metadata files
	metadataFiles, err := FindMetadataFiles(indexDir, logger)
	if err != nil {
		return 0, 0, fmt.Errorf("failed to find metadata files: %v", err)
	}

	totalFiles := len(metadataFiles)
	logger.Info("Processing %d metadata files...", totalFiles)

	if dryRun {
		logger.Info("DRY RUN: No files will be created")
	}

	// Create channel for metadata files
	metadataFileChan := make(chan string, totalFiles)

	// Create channel for results
	resultsChan := make(chan [2]int, totalFiles)

	// Create wait group for workers
	var wg sync.WaitGroup

	// Start workers
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		worker := NewWorker(i, metadataFileChan, crateIndex, mirrorDir, dryRun, &wg, logger, resultsChan)
		go worker.Start()
	}

	// Send metadata files to workers
	for _, file := range metadataFiles {
		metadataFileChan <- file
	}
	close(metadataFileChan)

	// Create a goroutine to close the results channel when all workers are done
	go func() {
		wg.Wait()
		close(resultsChan)
	}()

	// Collect results
	successCount := 0
	totalVersions := 0
	processed := 0

	// Create a ticker for progress updates
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	// Create a done channel that will be closed when all results are collected
	done := make(chan struct{})

	// Start a goroutine to collect results
	go func() {
		for result := range resultsChan {
			successCount += result[0]
			totalVersions += result[1]
			processed++

			// Print progress every 1000 files
			if processed%1000 == 0 {
				logger.Info("Progress: %d/%d files processed (%.2f%%)", processed, totalFiles, float64(processed)/float64(totalFiles)*100)
			}
		}
		close(done)
	}()

	// Wait for all results to be collected or print progress every second
	for {
		select {
		case <-done:
			return successCount, totalVersions, nil
		case <-ticker.C:
			logger.Info("Progress: %d/%d files processed (%.2f%%)", processed, totalFiles, float64(processed)/float64(totalFiles)*100)
		}
	}
}

func main() {
	// Parse command line arguments
	indexDir := flag.String("index-dir", "E:\\crates.io-index", "Directory containing the crates.io index")
	mirrorDir := flag.String("mirror-dir", "E:\\crates-mirror", "Directory containing the mirrored crates")
	logPath := flag.String("log-path", "E:\\metadata-organize-log.txt", "Path to log file")
	threads := flag.Int("threads", runtime.NumCPU(), "Number of worker threads")
	dryRun := flag.Bool("dry-run", false, "Dry run mode (no files will be created)")

	flag.Parse()

	// Create logger
	logger, err := NewLogger(*logPath)
	if err != nil {
		fmt.Printf("Failed to create logger: %v\n", err)
		os.Exit(1)
	}

	logger.Info("Starting organization of metadata from %s to %s", *indexDir, *mirrorDir)

	// Check if directories exist
	if _, err := os.Stat(*indexDir); os.IsNotExist(err) {
		logger.Error("Index directory %s does not exist", *indexDir)
		os.Exit(1)
	}

	if _, err := os.Stat(*mirrorDir); os.IsNotExist(err) {
		logger.Error("Mirror directory %s does not exist", *mirrorDir)
		os.Exit(1)
	}

	// Record start time
	startTime := time.Now()

	// Organize metadata
	successCount, totalVersions, err := OrganizeMetadata(*indexDir, *mirrorDir, *threads, *dryRun, logger)
	if err != nil {
		logger.Error("Failed to organize metadata: %v", err)
		os.Exit(1)
	}

	// Record end time
	endTime := time.Now()
	duration := endTime.Sub(startTime)

	// Log results
	if *dryRun {
		logger.Info("DRY RUN COMPLETE: Would have organized %d out of %d version metadata files in %v", successCount, totalVersions, duration)
	} else {
		logger.Info("Organization complete: %d out of %d version metadata files successfully organized in %v", successCount, totalVersions, duration)
	}

	os.Exit(0)
}
