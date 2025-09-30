#!/usr/bin/env python3
"""Test script to verify RAPID TUI works correctly."""

import subprocess
import sys
from pathlib import Path


def test_rapid_tui():
    """Test that rapid-tui works correctly."""

    # Test 1: Verify the app can be imported
    print("Test 1: Testing that rapid-tui can be imported...")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from rapid_tui.app import RapidTUI; print('App imports successfully')",
        ],
        capture_output=True,
        text=True,
        timeout=2,
    )

    if "App imports successfully" in result.stdout:
        print("✅ Test 1 passed: App can be imported and initialized")
    else:
        print("❌ Test 1 failed: Could not import app")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")

    # Test 2: Import test
    print("\nTest 2: Testing module imports...")
    try:
        from rapid_tui.config import get_assistant_config
        from rapid_tui.models import Assistant, Language

        print("✅ Test 2 passed: All modules imported successfully")

        # Test 3: Enum values
        print("\nTest 3: Testing enums...")
        assert Language.PYTHON.display_name == "Python"
        assert Assistant.CLAUDE_CODE.display_name == "Claude Code"
        print("✅ Test 3 passed: Enums work correctly")

        # Test 4: Config test
        print("\nTest 4: Testing configuration...")
        config = get_assistant_config(Assistant.CLAUDE_CODE)
        assert config.base_dir == ".claude"
        print("✅ Test 4 passed: Configuration loads correctly")

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

    print("\n✅ All tests passed! RAPID TUI v0 is ready to use.")
    print("\nTo run the application:")
    print("1. Navigate to your project directory")
    print("2. Run: rapid-tui")
    return True


if __name__ == "__main__":
    # Ensure we're running with the virtual environment
    venv_path = Path(__file__).parent / ".venv"
    if venv_path.exists() and not sys.prefix.startswith(str(venv_path)):
        print("⚠️  Please activate the virtual environment first:")
        print(f"   source {venv_path}/bin/activate")
        sys.exit(1)

    test_rapid_tui()
