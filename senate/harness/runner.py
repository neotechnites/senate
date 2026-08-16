"""Sandboxed subprocess runner for The Senate Tool Harness."""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from senate.harness.schema import ToolExecutionResult


class SandboxedRunner:
    def __init__(
        self,
        default_timeout_s: float = 60.0,
        allowed_root: Optional[Path] = None,
        env_whitelist: Optional[List[str]] = None,
    ):
        self.default_timeout_s = default_timeout_s
        self.allowed_root = allowed_root or Path(__file__).resolve().parents[2]
        self.env_whitelist = env_whitelist or [
            "PATH",
            "HOME",
            "USER",
            "SHELL",
            "PYTHONPATH",
            "VIRTUAL_ENV",
            "LANG",
            "LC_ALL",
        ]

    def _build_env(self, custom_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        env = {k: v for k, v in os.environ.items() if k in self.env_whitelist}
        if custom_env:
            env.update(custom_env)
        return env

    def run_command(
        self,
        command: Union[str, List[str]],
        cwd: Optional[Path] = None,
        timeout_s: Optional[float] = None,
        env: Optional[Dict[str, str]] = None,
        use_shell: bool = False,
    ) -> ToolExecutionResult:
        """Run a command synchronously with timeout, root validation, and env filtering."""
        timeout = timeout_s if timeout_s is not None else self.default_timeout_s
        work_dir = (Path(cwd) if cwd else self.allowed_root).resolve()
        
        # Enforce allowed_root strictly
        root_res = self.allowed_root.resolve()
        try:
            work_dir.relative_to(root_res)
        except ValueError:
            return ToolExecutionResult(
                command=str(command),
                exit_code=1,
                stdout="",
                stderr=f"Security Violation: Cwd '{work_dir}' is outside allowed root '{root_res}'.",
                duration_s=0.0,
                timed_out=False,
                metadata={"error": "path_outside_allowed_root"},
            )

        cmd_args: Union[str, List[str]]
        if isinstance(command, str):
            cmd_str = command
            if use_shell:
                cmd_args = command
            else:
                import shlex
                cmd_args = shlex.split(command)
        else:
            cmd_str = " ".join(command)
            cmd_args = command

        clean_env = self._build_env(env)
        start_ts = time.time()

        try:
            proc = subprocess.run(
                cmd_args,
                shell=use_shell,
                cwd=str(work_dir),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            duration = time.time() - start_ts
            return ToolExecutionResult(
                command=cmd_str,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_s=round(duration, 3),
                timed_out=False,
            )

        except subprocess.TimeoutExpired as te:
            duration = time.time() - start_ts
            return ToolExecutionResult(
                command=cmd_str,
                exit_code=-1,
                stdout=te.stdout.decode() if isinstance(te.stdout, bytes) else (te.stdout or ""),
                stderr=te.stderr.decode() if isinstance(te.stderr, bytes) else (te.stderr or "Command timed out."),
                duration_s=round(duration, 3),
                timed_out=True,
                metadata={"timeout_limit_s": timeout},
            )
        except Exception as e:
            duration = time.time() - start_ts
            return ToolExecutionResult(
                command=cmd_str,
                exit_code=1,
                stdout="",
                stderr=str(e),
                duration_s=round(duration, 3),
                timed_out=False,
                metadata={"exception": str(e)},
            )
