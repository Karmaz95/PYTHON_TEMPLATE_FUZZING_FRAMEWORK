import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from fuzzer import Fuzzer, PayloadGenerator

def main():
    tcp_fuzzer = str(Path(__file__).parent.parent / "bin" / "fuzzer_template")
    
    fuzzer = Fuzzer(
        target="127.0.0.1:1234",
        template_binary=tcp_fuzzer
    )
    
    generator = PayloadGenerator()
    print("Starting buffer overflow fuzzing...")
    fuzzer.fuzz_with_policy("buffer_overflow", generator, max_size=1024)

if __name__ == "__main__":
    main()
