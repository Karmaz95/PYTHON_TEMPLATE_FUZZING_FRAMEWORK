import subprocess
from pathlib import Path
from collections import deque
from typing import Optional, Iterator, Callable
from config import *
from datetime import datetime

def get_timestamp() -> str:
    """Returns formatted current timestamp for logging."""
    return datetime.now().strftime('%Y_%m_%d %H:%M:%S')

def get_timestamp_nano() -> str:
    """Returns formatted current timestamp with nanoseconds for logging."""
    return datetime.now().strftime('%Y%m%d_%H%M%S_%f')

def file_based_policy(func):
    """Decorator to mark a function as file-based policy."""
    func.is_file_based = True
    return func

class PayloadGenerator:
    """Generates payloads for fuzzing based on various policies."""

    def __init__(self, max_size: int = PAYLOAD_DEFAULT_MAX_SIZE, default_char: str = PAYLOAD_DEFAULT_CHAR, current_size: int = PAYLOAD_DEFAULT_MIN_SIZE):
        """
        Initialize the PayloadGenerator.

        Args:
            max_size: Maximum size of generated payloads.
            default_char: Character to fill in the payloads.
            current_size: Initial size of payloads.
        """
        self.max_size = max_size
        self.default_char = default_char
        self.current_size = current_size
        self.temp_file = "temp_payload.bin"
        self.current_file = 0
        self.current_line = 0

    def buffer_overflow(self, *, max_size: Optional[int] = None, **policy_args) -> Optional[str]:
        """
        Generates payloads for buffer overflow testing.

        Args:
            max_size: Maximum size override for payload generation.
        
        Returns:
            Generated payload or None when complete.
        """
        if max_size is not None:
            self.max_size = max_size

        if self.current_size > self.max_size:
            return None

        payload = self.default_char * self.current_size
        self.current_size += 1
        return payload

    def wordlist(self, *, wordlist_path: str = PATH_DEFAULT_WORDLIST, **policy_args) -> Optional[str]:
        """
        Generates payloads using a wordlist.

        Args:
            wordlist_path: Path to the wordlist file.
        
        Returns:
            Next wordlist entry as payload or None when exhausted.
        """
        with open(wordlist_path, 'r') as f:
            lines = f.readlines()

        if self.current_line >= len(lines):
            return None

        payload = lines[self.current_line].strip()
        self.current_line += 1
        return payload

    @file_based_policy
    def radamsa(self, save_path: str, *, pattern_file: str = PATH_DEFAULT_FILE_PATTERN, **policy_args) -> str:
        """
        Generates payloads using Radamsa fuzzer.

        Args:
            save_path: Directory to save generated payload.
            pattern_file: Input pattern file for Radamsa.
        
        Returns:
            Path to the generated payload file.
        """
        payload_path = f"{save_path}/{self.temp_file}"
        subprocess.check_output([PATH_RADAMSA, pattern_file, "-o", payload_path, "-n", "1"])
        return payload_path

    @file_based_policy
    def files(self, save_path: str, *, files_dir: str = PATH_DEFAULT_FILES_DIR, **policy_args) -> Optional[str]:
        """
        Reuses existing files as payloads.

        Args:
            save_path: Directory to save temporary copies.
            files_dir: Directory containing test files.
        
        Returns:
            Path to the copied file or None when all files are processed.
        """
        files = sorted([f for f in Path(files_dir).iterdir() if f.is_file()])

        if self.current_file >= len(files):
            return None

        source_file = files[self.current_file]
        temp_path = f"{save_path}/{self.temp_file}"
        Path(temp_path).write_bytes(source_file.read_bytes())
        
        self.current_file += 1
        return temp_path

    def reset(self) -> None:
        """Resets the generator to its initial state."""
        self.current_size = PAYLOAD_DEFAULT_MIN_SIZE
        self.current_file = 0
        self.current_line = 0

class PayloadManager:
    """Manages payload saving and history."""

    def __init__(self):
        """
        Initializes the payload manager.

        Creates directories for session and tracks history.
        """
        self.base_dir = Path(PATH_PAYLOAD_HISTORY_LOG)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir = self.base_dir / f"fuzzing_session_{get_timestamp_nano()}"
        self.session_dir.mkdir()
        self.payload_history = deque(maxlen=PAYLOAD_HISTORY_LIMIT)
        self.counter = 0

    def save_payload(self, payload: Optional[str] = None, payload_path: Optional[str] = None) -> str:
        """
        Saves payload to session directory.

        Args:
            payload: Payload string to save.
            payload_path: Path to an existing payload file.
        
        Returns:
            Path to the saved payload.
        """
        if len(self.payload_history) >= PAYLOAD_HISTORY_LIMIT:
            oldest = self.payload_history.popleft()
            oldest.unlink()

        self.counter += 1
        new_path = self.session_dir / f"payload_{self.counter}.bin"

        if payload is not None:
            new_path.write_bytes(payload.encode())
        else:
            Path(payload_path).rename(new_path)

        self.payload_history.append(new_path)
        return str(new_path)

class Fuzzer:
    """Generic fuzzing orchestrator that works with any fuzzer template."""
    
    def __init__(self, target: str, template_binary: Optional[str] = None):
        """
        Initialize generic fuzzer.

        Args:
            target: Target identifier (whatever the template expects)
            template_binary: Path to the fuzzer template binary
        """
        self.target = target
        self.template_binary = template_binary or PATH_FUZZER_TEMPLATE
        self.manager = PayloadManager()

    def run_test_payload(self, payload: str) -> tuple[str, str]:
        """Run test with string payload."""
        cmd = [
            self.template_binary,
            "--target", self.target,
            "--payload", payload
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr

    def run_test_file(self, file_path: str) -> tuple[str, str]:
        """Run test with file payload."""
        cmd = [
            self.template_binary,
            "--target", self.target,
            "--file", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr

    def fuzz_with_policy(self, policy_name: str, generator: PayloadGenerator, debug: bool = DEBUG_MODE, **policy_args) -> None:
        """
        Executes the fuzzing process with a given policy.

        Args:
            policy_name: Name of the policy to apply.
            generator: Instance of PayloadGenerator.
            debug: If True, prints detailed output for each test.
            **policy_args: Arguments specific to the policy.
        """
        while True:
            policy_method = getattr(generator, policy_name)
            result = self._run_policy(policy_method, policy_args)
            if result is None:
                if debug:
                    print(f"Policy {policy_name} completed {get_timestamp()}")
                break

            save_path, stdout, stderr = result
            if debug:
                print(f"{self.target} - {get_timestamp()} - {save_path} - {stdout.strip()} - {stderr.strip()}")

    def _run_policy(self, policy_method: Callable, policy_args: dict) -> Optional[tuple[str, str, str]]:
        """
        Executes a single step of a fuzzing policy.

        Args:
            policy_method: The policy method to execute.
            policy_args: Arguments for the policy method.
        
        Returns:
            Tuple containing saved payload path, stdout, and stderr.
        """
        if getattr(policy_method, "is_file_based", False):
            temp_path = policy_method(save_path=str(self.manager.session_dir), **policy_args)
            if temp_path is None:
                return None

            save_path = self.manager.save_payload(payload_path=temp_path)
            stdout, stderr = self.run_test_file(save_path)
        else:
            payload = policy_method(**policy_args)
            if payload is None:
                return None

            save_path = self.manager.save_payload(payload=payload)
            stdout, stderr = self.run_test_payload(payload)

        return save_path, stdout, stderr

def main(): # Example usage
    tcp_fuzzer = PATH_FUZZER_TEMPLATE
    
    fuzzer = Fuzzer(
        target="127.0.0.1:1234",
        template_binary=tcp_fuzzer
    )
    
    generator = PayloadGenerator()
    print("Starting buffer overflow fuzzing...")
    fuzzer.fuzz_with_policy("buffer_overflow", generator, max_size=1024)

    # Example usage with explicit policy arguments
    fuzzer.fuzz_with_policy("buffer_overflow", generator)#, max_size=90)
    fuzzer.fuzz_with_policy("wordlist", generator, wordlist_path=PATH_DEFAULT_WORDLIST)
    fuzzer.fuzz_with_policy("files", generator, files_dir=PATH_DEFAULT_FILES_DIR)
    fuzzer.fuzz_with_policy("radamsa", generator, pattern_file=PATH_DEFAULT_FILE_PATTERN)

if __name__ == "__main__":
    main()