#!/usr/bin/env python3
"""Simple setup script for the project."""

import subprocess
import sys


def run_command(cmd: str, description: str):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        sys.exit(1)


def main():
    """Main setup function."""
    print("🚀 Setting up Smart Order Intake System")

    # Check if uv is installed
    try:
        subprocess.run("uv --version", shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ uv is not installed. Please install it first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # Install dependencies
    run_command("uv sync", "Installing dependencies")

    # Install dev dependencies
    run_command("uv sync --extra dev", "Installing dev dependencies")

    # Format code
    run_command("uv run ruff format .", "Formatting code")

    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("   1. Copy env.example to .env and add your API keys")
    print("   2. Run: uv run streamlit run main.py")
    print("   3. Run tests: uv run pytest")


if __name__ == "__main__":
    main()
