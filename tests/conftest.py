"""Pytest configuration file."""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Configure pytest
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
