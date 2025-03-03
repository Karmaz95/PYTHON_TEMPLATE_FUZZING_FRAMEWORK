"""
Example of parallel TCP fuzzing using the fuzzer runner.
This will fuzz multiple ports simultaneously using different policies.
"""

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from fuzzer_runner import FuzzManager, Target

def main():
    """Sets up and runs parallel fuzzing of multiple TCP ports."""
    targets = [
        Target("127.0.0.1", 5000, in_size=1024),    # Test up to 1KB payloads
        Target("127.0.0.1", 8080, in_size=2048),    # Test up to 2KB payloads
        Target("127.0.0.1", 9000, in_size=4096),    # Test up to 4KB payloads
    ]

    print("Starting parallel fuzzing of multiple TCP ports...")
    print(f"Targets to fuzz: {', '.join(f'{t.host}:{t.port}' for t in targets)}")
    print("Press Ctrl+C to stop")
    
    try:
        FuzzManager(targets).fuzz_all()
    except KeyboardInterrupt:
        print("\nStopping all fuzzing processes...")
        sys.exit(0)

if __name__ == "__main__":
    main()
