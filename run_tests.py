import subprocess
import sys
import os


def run_tests():
    """Run all tests with different configurations"""

    # Set test environment
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test_db"

    commands = [
        # Run unit tests
        ["pytest", "tests/unit/", "-v", "--tb=short"],
    ]

    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {cmd[1]} passed")
            else:
                print(f"❌ {cmd[1]} failed")
                print(result.stdout)
                print(result.stderr)
        except Exception as e:
            print(f"Error running {cmd}: {e}")


if __name__ == "__main__":
    run_tests()