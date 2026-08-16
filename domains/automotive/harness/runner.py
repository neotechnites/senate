"""Tool execution harness for Automotive Chassis Engineering Domain Pod."""
import subprocess
from pathlib import Path
from typing import List, Union

POD_ROOT = Path(__file__).resolve().parent.parent

def run_domain_tool(command: Union[str, List[str]]) -> subprocess.CompletedProcess:
    """Run a domain tool within the isolated pod root."""
    return subprocess.run(command, cwd=str(POD_ROOT), capture_output=True, text=True)
