"""
Configuration Module
------------------
Contains all configuration constants for the fuzzer application.
Centralized location for paths, limits, and default values.
"""

DEBUG_MODE = True

#------------------------------------------------------------------------------
# Binary and Template Paths
#------------------------------------------------------------------------------
PATH_BINARIES = "./bin"                                      # Directory containing compiled binaries
PATH_RADAMSA = f"{PATH_BINARIES}/radamsa"                    # Path to radamsa mutation tool
PATH_FUZZER_TEMPLATE = f"{PATH_BINARIES}/fuzzer_template"    # Path to compiled fuzzer template

#------------------------------------------------------------------------------
# Payload and Test Files Paths
#------------------------------------------------------------------------------
PATH_PAYLOADS = "./payloads/"                                # Directory for payload templates
PATH_DEFAULT_FILE_PATTERN = f"{PATH_PAYLOADS}/single_A.txt"  # Pattern file used by radamsa for mutations
PATH_DEFAULT_WORDLIST = f"{PATH_PAYLOADS}/wordlist.txt"      # Wordlist for dictionary-based fuzzing
PATH_DEFAULT_FILES_DIR = f"{PATH_PAYLOADS}/test_files/"      # Directory containing test case files
PATH_PAYLOAD_HISTORY_LOG = "./payload_history/"              # Directory for saving generated payloads

#------------------------------------------------------------------------------
# Payload Generation Settings
#------------------------------------------------------------------------------
PAYLOAD_HISTORY_LIMIT = 50         # Maximum number of payloads to keep in history for each fuzzing session
PAYLOAD_DEFAULT_CHAR = "A"         # Default character for buffer overflow testing
PAYLOAD_DEFAULT_MAX_SIZE = 4096    # Maximum size limit for generated payloads (bytes) - ending size for buffer overflow
PAYLOAD_DEFAULT_MIN_SIZE = 0       # Starting size for buffer overflow payloads

#------------------------------------------------------------------------------
# Fuzzing Policies Configuration
#------------------------------------------------------------------------------
# List of policies that FuzzerRunner will execute in parallel
POLICIES_FOR_RUNNER = [
    "buffer_overflow",  # Tests buffer overflow vulnerabilities
    "wordlist",         # Tests using predefined patterns
    "files",            # Tests using sample files
    "radamsa"           # Test with radamsa mutations of the default pattern (PATH_DEFAULT_FILE_PATTERN) - WARNING: This policy run forever!
]