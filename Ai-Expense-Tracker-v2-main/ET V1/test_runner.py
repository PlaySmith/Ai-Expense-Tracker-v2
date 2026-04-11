#!/usr/bin/env python3
"""
SmartSpend AI - Automated Test Runner
=====================================

Comprehensive testing script for the entire application stack.
Tests backend API, OCR service, database operations, frontend build,
and integration between components.

Usage:
    python test_runner.py [options]

Options:
    --backend-only    Test only backend
    --frontend-only   Test only frontend
    --integration     Run integration tests only
    --verbose         Enable verbose logging
    --quick           Quick test (skip heavy operations)
"""

import os
import sys
import time
import json
import logging
import subprocess
import requests
import tempfile
import shutil
import signal
import socket
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Test configuration
@dataclass
class TestConfig:
    """Test configuration settings"""
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    backend_port: int = 8000
    frontend_port: int = 5173
    test_timeout: int = 30
    verbose: bool = False
    quick_mode: bool = False
    backend_only: bool = False
    frontend_only: bool = False
    integration_only: bool = False

@dataclass
class TestResult:
    """Individual test result"""
    name: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'ERROR'
    duration: float
    message: str = ""
    details: Dict = None
    fix_suggestion: str = ""
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class TestSuite:
    """Test suite with results tracking"""
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def add_result(self, result: TestResult):
        self.results.append(result)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == 'PASS')
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status in ['FAIL', 'ERROR'])
    
    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == 'SKIP')
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

class AutomatedTestRunner:
    """Main test runner class"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.suites: List[TestSuite] = []
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.test_data_dir = Path("test_data")
        self.logs_dir = Path("test_logs")
        self.reports_dir = Path("test_reports")
        
        # Create directories
        self.test_data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Test tracking
        self.created_expense_ids: List[int] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("test_runner")
        logger.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)
        
        # Clear existing handlers
        logger.handlers = []
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(detailed_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = self.logs_dir / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_section(self, title: str):
        """Log a section header"""
        self.logger.info("=" * 70)
        self.logger.info(f" {title}")
        self.logger.info("=" * 70)
    
    def log_subsection(self, title: str):
        """Log a subsection header"""
        self.logger.info("-" * 50)
        self.logger.info(f" {title}")
        self.logger.info("-" * 50)
    
    def run_test(self, name: str, test_func, *args, **kwargs) -> TestResult:
        """Run a single test and capture result"""
        start_time = time.time()
        try:
            test_func(*args, **kwargs)
            duration = time.time() - start_time
            return TestResult(
                name=name,
                status='PASS',
                duration=duration,
                message="Test completed successfully"
            )
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            fix_suggestion = self._get_fix_suggestion(e)
            return TestResult(
                name=name,
                status='FAIL',
                duration=duration,
                message=error_msg,
                details={'error_type': type(e).__name__},
                fix_suggestion=fix_suggestion
            )
    
    def _get_fix_suggestion(self, error: Exception) -> str:
        """Get fix suggestion based on error type"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        suggestions = {
            'ConnectionError': "Check if the server is running and accessible",
            'TesseractNotFoundError': "Install Tesseract OCR: Windows - download from GitHub, macOS - brew install tesseract, Linux - sudo apt-get install tesseract-ocr",
            'ModuleNotFoundError': f"Install missing module: pip install {str(error).split()[-1]}",
            'FileNotFoundError': "Check if the file exists and path is correct",
            'PermissionError': "Check file/directory permissions",
            'OSError': "Check system resources and disk space",
            'RuntimeError': "Restart the application and try again",
        }
        
        # Check for specific error messages
        if 'tesseract' in error_msg:
            return suggestions.get('TesseractNotFoundError', "Check Tesseract installation")
        elif 'connection' in error_msg or 'refused' in error_msg:
            return suggestions.get('ConnectionError', "Check server status")
        elif 'module' in error_msg or 'import' in error_msg:
            return suggestions.get('ModuleNotFoundError', "Install required dependencies")
        
        return suggestions.get(error_type, "Check logs for details and retry")
    
    # ==================== ENVIRONMENT TESTS ====================
    
    def test_environment(self) -> TestSuite:
        """Test environment setup"""
        suite = TestSuite("Environment Validation")
        suite.start_time = time.time()
        
        self.log_section("ENVIRONMENT VALIDATION")
        
        # Test Python version
        result = self.run_test(
            "Python Version Check",
            self._check_python_version
        )
        suite.add_result(result)
        self.logger.info(f"{'✓' if result.status == 'PASS' else '✗'} {result.name}: {result.status}")
        
        # Test Node.js
        result = self.run_test(
            "Node.js Installation",
            self._check_nodejs
        )
        suite.add_result(result)
        self.logger.info(f"{'✓' if result.status == 'PASS' else '✗'} {result.name}: {result.status}")
        
        # Test Tesseract
        result = self.run_test(
            "Tesseract OCR Installation",
            self._check_tesseract
        )
        suite.add_result(result)
        self.logger.info(f"{'✓' if result.status == 'PASS' else '✗'} {result.name}: {result.status}")
        
        # Test directory structure
        result = self.run_test(
            "Directory Structure",
            self._check_directory_structure
        )
        suite.add_result(result)
        self.logger.info(f"{'✓' if result.status == 'PASS' else '✗'} {result.name}: {result.status}")
        
        suite.end_time = time.time()
        return suite
    
    def _check_python_version(self):
        """Check Python version"""
        version = sys.version_info
        if version < (3, 8):
            raise RuntimeError(f"Python 3.8+ required, found {version.major}.{version.minor}")
        self.logger.debug(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    def _check_nodejs(self):
        """Check Node.js installation"""
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError("Node.js not found")
            version = result.stdout.strip()
            self.logger.debug(f"Node.js version: {version}")
        except FileNotFoundError:
            raise RuntimeError("Node.js not installed or not in PATH")
    
    def _check_tesseract(self):
        """Check Tesseract OCR installation"""
        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            self.logger.debug(f"Tesseract version: {version}")
        except Exception as e:
            raise RuntimeError(f"Tesseract not properly installed: {str(e)}")
    
    def _check_directory_structure(self):
        """Check required directories exist"""
        required_dirs = ['Backend', 'Frontend', 'Backend/app', 'Frontend/src']
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                raise FileNotFoundError(f"Required directory not found: {dir_name}")
    
    # ==================== BACKEND TESTS ====================
    
    def test_backend(self) -> TestSuite:
        """Test backend API"""
        suite = TestSuite("Backend API Tests")
        suite.start_time = time.time()
        
        self.log_section("BACKEND API TESTS")
        
        # Start backend server
        if not self._start_backend():
            suite.add_result(TestResult(
                name="Backend Server Startup",
                status='FAIL',
                duration=0,
                message="Failed to start backend server",
                fix_suggestion="Check Backend/app/main.py and dependencies"
            ))
            suite.end_time = time.time()
            return suite
        
        try:
            # Wait for server to be ready
            time.sleep(2)
            
            # Test health endpoint
            result = self.run_test("Health Check", self._test_health_endpoint)
            suite.add_result(result)
            self.logger.info(f"{'✓' if result.status == 'PASS' else '✗'} {result.name}: {result.status}")
            
            # Test API endpoints
            tests = [
                ("Get All Expenses", self._test_get_expenses),
                ("Get Expense Stats", self._test_get_stats),
                ("Upload Receipt", self._test_upload_receipt),
                ("Get Single Expense", self._test_get_expense),
                ("Update Expense", self._test_update_expense),
                ("Delete Expense", self._test_delete_expense),
            ]
            
            for test_name, test_func in tests:
                result = self.run_test(test_name, test_func)
                suite.add_result(result)
                self.logger.info(f"{'✓' if result.status == 'PASS' else '✗'} {result.name}: {result.status}")
                if result.status != 'PASS' and result.fix_suggestion:
                    self.logger.info(f"  Suggestion: {result.fix_suggestion}")
            
        finally:
            self._stop_backend()
            suite.end_time = time.time()
        
        return suite
    
    def _start_backend(self) -> bool:
        """Start backend server"""
        self.log_subsection("Starting Backend Server")
        try:
            # Check if port is already in use
            if self._is_port_in_use(self.config.backend_port):
                self.logger.warning(f"Port {self.config.backend_port} already in use, attempting to use existing server")
                return True
            
            # Start backend
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path('Backend').absolute())
            
            self.backend_process = subprocess.Popen(
                [sys.executable, '-m', 'app.main'],
                cwd='Backend',
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Wait for server to start
            for i in range(10):
                time.sleep(1)
                if self._is_port_in_use(self.config.backend_port):
                    self.logger.info("Backend server started successfully")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start backend: {str(e)}")
            return False
    
    def _stop_backend(self):
