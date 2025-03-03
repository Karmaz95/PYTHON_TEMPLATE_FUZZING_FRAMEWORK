from multiprocessing import Process
from typing import Optional, List, Dict, Any, NamedTuple
import time
from pathlib import Path
from fuzzer import *

class Target(NamedTuple):
    """Represents a target to fuzz."""
    host: str
    port: int
    in_size: Optional[int] = None
    out_size: Optional[int] = None

class FuzzerRunner:
    """Manages multiple fuzzing processes for a single target."""

    def __init__(self, target: Target):
        self.target = target
        self.processes: List[Process] = []

    def start(self) -> None:
        """Starts parallel fuzzing processes for all configured policies."""
        target_str = f"{self.target.host}:{self.target.port}"
        for policy_name in POLICIES_FOR_RUNNER:
            process = Process(
                target=self._run_fuzzing_process,
                name=f"fuzzer_{target_str}_{policy_name}",
                kwargs={
                    "target": target_str,
                    "policy_name": policy_name,
                    "policy_args": {"max_size": self.target.in_size} if self.target.in_size else {}
                }
            )
            process.start()
            self.processes.append(process)
            time.sleep(0.5)

    @staticmethod
    def _run_fuzzing_process(target: str, policy_name: str, policy_args: Dict[str, Any]) -> None:
        """Executes a single fuzzing process."""
        print(f"START: {get_timestamp()} - {target} - {policy_name}")
        try:
            fuzzer = Fuzzer(target=target)
            fuzzer.fuzz_with_policy(policy_name, PayloadGenerator(), debug=DEBUG_MODE, **policy_args)
            print(f"END: {get_timestamp()} - {target} - {policy_name}")
        except Exception as e:
            print(f"ERROR: {get_timestamp()} - {target} - {policy_name}: {e}")

    def stop(self) -> None:
        """Stops all running fuzzing processes."""
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
        self.processes.clear()

class FuzzManager:
    """Orchestrates multiple FuzzerRunners for comprehensive testing."""

    def __init__(self, targets: List[Target]):
        self.runners = [FuzzerRunner(target) for target in targets]

    def fuzz_all(self) -> None:
        """Starts fuzzing all configured targets in parallel."""
        for runner in self.runners:
            target = runner.target
            print(f"Starting fuzzer at {get_timestamp()} for {target.host}:{target.port} "
                  f"with buffer sizes: in_size={target.in_size}, out_size={target.out_size}")
            runner.start()

        try:
            while any(p.is_alive() for runner in self.runners for p in runner.processes):
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()
            print("\nStopped all fuzzing processes")

    def stop_all(self) -> None:
        """Stops all running fuzzing processes."""
        for runner in self.runners:
            runner.stop()

def main():
    """Entry point for the fuzzer runner.
    Discovers and executes fuzzing for all configured targets.
    """
    targets = [
        Target(host="localhost", port=8000, in_size=1024, out_size=2048),
        Target(host="localhost", port=8001, in_size=512, out_size=1024),
        # Add more targets as needed
    ]
    print(f"Found {len(targets)} targets to fuzz")
    
    for target in targets:
        print(f"\nInitializing fuzzing for {target.host}:{target.port}")
        FuzzManager([target]).fuzz_all()

if __name__ == "__main__":
    main()
