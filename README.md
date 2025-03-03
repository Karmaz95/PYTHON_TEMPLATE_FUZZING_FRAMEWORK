# Python Fuzzer Framework

Fast, flexible black-box fuzzing framework. Write a template binary that handles your protocol/target and use built-in policies to fuzz it.

## Installation

```bash
# Compile TCP fuzzer template
clang++ tcp_fuzzer_template.cpp -o bin/fuzzer_template

# Install radamsa for mutation-based fuzzing
brew install radamsa
```

## Usage Examples

### 1. Simple TCP Fuzzing
```python
from fuzzer import Fuzzer, PayloadGenerator

# Single target fuzzing
fuzzer = Fuzzer(
    target="127.0.0.1:5000",
    template_binary="./bin/fuzzer_template"
)

generator = PayloadGenerator(max_size=1024)
fuzzer.fuzz_with_policy("buffer_overflow", generator)
```

### 2. Parallel Multi-Target Fuzzing
```python
from fuzzer_runner import FuzzManager, Target

# Define multiple targets
targets = [
    Target("127.0.0.1", 5000, in_size=1024),    # Test up to 1KB payloads
    Target("127.0.0.1", 8080, in_size=2048),    # Test up to 2KB payloads
    Target("127.0.0.1", 9000, in_size=4096),    # Test up to 4KB payloads
]

# Start parallel fuzzing
FuzzManager(targets).fuzz_all()
```

## Writing Fuzzer Templates

Templates must implement this minimal interface:
```bash
--target <identifier>   # Target string (e.g., "host:port")
--payload <data>        # String payload
--file <path>           # File payload (alternative to --payload)
```

Example template:
```cpp
int main(int argc, char *argv[]) {
    // Parse arguments
    // Connect to target
    // Send payload
    // Exit immediately
}
```

## Available Fuzzing Policies

1. **buffer_overflow**
   - Incrementally increasing payload size
   - `max_size`: Maximum payload size to test

2. **wordlist**
   - Test using dictionary entries
   - `wordlist_path`: Path to wordlist file

3. **files**
   - Use existing files as payloads
   - `files_dir`: Directory with test files

4. **radamsa**
   - Smart mutations using radamsa
   - `pattern_file`: Base pattern for mutations

## Directory Structure
```
.
├── bin/                    # Compiled fuzzer templates
├── payloads/              # Payload templates
│   ├── single_A.txt       # Radamsa pattern
│   ├── test_files/        # Test files
│   └── wordlist.txt       # Dictionary
└── payload_history/       # Generated payloads
```

## Best Practices

### Infrastructure
* Use tmux/screen for persistent sessions
* Keep payload history for crash reproduction
* Monitor target behavior

### Crash Handling
1. Payload history is preserved in `payload_history/`
2. DO NOT run cleaner.py until crash is documented
3. Use payload files for crash reproduction

## Configuration

Edit `config.py` to customize:
* Payload sizes and limits
* File paths
* Debug mode
* Fuzzing policies

## Tips

* Start with small payload sizes
* Test one port at a time initially
* Use parallel fuzzing for thorough testing
* Monitor system resources
* Keep logs for crash analysis