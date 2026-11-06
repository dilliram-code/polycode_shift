"""
PolyShift - Security and Sandboxed Execution Subsystem
"""
import os
import re
import shutil
import subprocess
import tempfile
import time
from typing import Dict, Any, Optional

from app.core.config import settings

# Dangerous patterns to guard against in executed code
DANGEROUS_PATTERNS = [
    r"os\.system\(",
    r"subprocess\.Popen\(",
    r"__import__\(['\"]os['\"]\)\.system",
    r"child_process",
    r"require\(['\"]child_process['\"]\)",
    r"system\(",
    r"execve\(",
    r"fork\(\)",
    r"std::process::Command",
    r"Command::new\(",
    r"remove\(",
    r"unlink\(",
    r"rmdir\(",
]

def check_code_safety(code: str, language: str) -> tuple[bool, Optional[str]]:
    """Inspects code for obviously hazardous system-level operations."""
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            return False, f"Execution blocked: Potential hazardous system-level invocation detected ({pattern})."
    return True, None

def check_compiler_availability(language: str) -> tuple[bool, str]:
    """Checks if the required compiler or interpreter is installed on the host."""
    lang = language.lower()
    if lang == "python":
        py = shutil.which("python3") or shutil.which("python")
        if py:
            return True, py
        return False, "Python interpreter not found."
    elif lang in ("javascript", "js"):
        node = shutil.which("node")
        if node:
            return True, node
        return False, "Node.js runtime not found."
    elif lang in ("cpp", "c++"):
        cpp = shutil.which("g++") or shutil.which("clang++")
        if cpp:
            return True, cpp
        return False, "C++ compiler (g++ / clang++) not found."
    elif lang == "rust":
        rustc = shutil.which("rustc")
        if rustc:
            return True, rustc
        return False, "Rust compiler (rustc) is not installed on this host."
    return False, f"Unsupported execution language: {language}"

def run_sandboxed_code(code: str, language: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """
    Executes code in an isolated temporary directory with a timeout and resource safeguards.
    Returns:
        {
            "success": bool,
            "stdout": str,
            "stderr": str,
            "exit_code": int,
            "execution_time_ms": float,
            "validation_status": str,
            "error": Optional[str]
        }
    """
    if len(code.encode("utf-8")) > settings.MAX_CODE_SIZE_BYTES:
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "execution_time_ms": 0.0,
            "validation_status": "error",
            "error": "Code exceeds maximum size limit (1 MB)."
        }

    is_safe, safety_error = check_code_safety(code, language)
    if not is_safe:
        return {
            "success": False,
            "stdout": "",
            "stderr": safety_error or "Security violation",
            "exit_code": 126,
            "execution_time_ms": 0.0,
            "validation_status": "security_block",
            "error": safety_error
        }

    lang = language.lower()
    is_avail, compiler_path = check_compiler_availability(lang)
    if not is_avail:
        return {
            "success": False,
            "stdout": "",
            "stderr": compiler_path,
            "exit_code": 127,
            "execution_time_ms": 0.0,
            "validation_status": "runtime_missing",
            "error": compiler_path
        }

    timeout_val = timeout or settings.EXECUTION_TIMEOUT_SECONDS
    temp_dir = tempfile.mkdtemp(prefix="polyshift_sandbox_")

    start_time = time.perf_counter()
    stdout_text = ""
    stderr_text = ""
    exit_code = 0
    validation_status = "success"
    err_msg = None

    try:
        if lang == "python":
            file_path = os.path.join(temp_dir, "script.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = [compiler_path, file_path]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_val,
                cwd=temp_dir
            )
            stdout_text = proc.stdout
            stderr_text = proc.stderr
            exit_code = proc.returncode

        elif lang in ("javascript", "js"):
            file_path = os.path.join(temp_dir, "script.js")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = [compiler_path, file_path]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_val,
                cwd=temp_dir
            )
            stdout_text = proc.stdout
            stderr_text = proc.stderr
            exit_code = proc.returncode

        elif lang in ("cpp", "c++"):
            source_file = os.path.join(temp_dir, "main.cpp")
            binary_file = os.path.join(temp_dir, "main_bin")
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Compile step
            compile_cmd = [compiler_path, "-std=c++17", "-O2", source_file, "-o", binary_file]
            comp_proc = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=temp_dir
            )
            if comp_proc.returncode != 0:
                exit_code = comp_proc.returncode
                stderr_text = f"Compilation Error:\n{comp_proc.stderr}"
                validation_status = "compilation_error"
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": stderr_text[:settings.MAX_OUTPUT_BYTES],
                    "exit_code": exit_code,
                    "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2),
                    "validation_status": validation_status,
                    "error": "C++ compilation failed."
                }
            
            # Execute step
            proc = subprocess.run(
                [binary_file],
                capture_output=True,
                text=True,
                timeout=timeout_val,
                cwd=temp_dir
            )
            stdout_text = proc.stdout
            stderr_text = proc.stderr
            exit_code = proc.returncode

        elif lang == "rust":
            source_file = os.path.join(temp_dir, "main.rs")
            binary_file = os.path.join(temp_dir, "main_bin")
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)

            compile_cmd = [compiler_path, source_file, "-o", binary_file]
            comp_proc = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                cwd=temp_dir
            )
            if comp_proc.returncode != 0:
                exit_code = comp_proc.returncode
                stderr_text = f"Rust Compilation Error:\n{comp_proc.stderr}"
                validation_status = "compilation_error"
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": stderr_text[:settings.MAX_OUTPUT_BYTES],
                    "exit_code": exit_code,
                    "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2),
                    "validation_status": validation_status,
                    "error": "Rust compilation failed."
                }

            proc = subprocess.run(
                [binary_file],
                capture_output=True,
                text=True,
                timeout=timeout_val,
                cwd=temp_dir
            )
            stdout_text = proc.stdout
            stderr_text = proc.stderr
            exit_code = proc.returncode

        if exit_code != 0:
            validation_status = "runtime_error"
        else:
            validation_status = "success"

    except subprocess.TimeoutExpired:
        exit_code = 124
        validation_status = "timeout"
        stderr_text = f"Execution timed out after {timeout_val} seconds."
        err_msg = stderr_text
    except Exception as e:
        exit_code = 1
        validation_status = "error"
        stderr_text = str(e)
        err_msg = str(e)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return {
        "success": exit_code == 0,
        "stdout": stdout_text[:settings.MAX_OUTPUT_BYTES],
        "stderr": stderr_text[:settings.MAX_OUTPUT_BYTES],
        "exit_code": exit_code,
        "execution_time_ms": elapsed_ms,
        "validation_status": validation_status,
        "error": err_msg
    }
