from pathlib import Path
import subprocess
import threading

from .task import Task


class ExeRunner:
    """Runs the exe for one task. Remembers the running exe processes, so they can be killed on Ctrl+C."""

    def __init__(self, build_command, output_folder: Path, cwd: Path | None = None):
        self.build_command = build_command
        self.output_folder = output_folder
        self._cwd = cwd
        self._lock = threading.Lock()
        self._running = set()
        self._stopped = False
        # On Windows, start every exe in its own process group: Ctrl+C then only reaches Python,
        # which stops the scheduling first and then kills the running exe processes itself.
        self._creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    def run(self, task: Task) -> bool:
        # Argument list instead of one string with shell=True: no extra cmd.exe in between,
        # no quoting problems, and kill() hits the exe itself
        command = [str(part) for part in self.build_command(task, self.output_folder)]

        # Check and start under the lock, so no new exe can start after stop() has run
        with self._lock:
            if self._stopped:
                return False
            process = subprocess.Popen(command, cwd=self._cwd,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, errors="replace",
                                       creationflags=self._creation_flags)
            self._running.add(process)

        try:
            # Blocks this thread only; the GIL is released while waiting for the exe
            stdout, stderr = process.communicate()
        finally:
            with self._lock:
                self._running.discard(process)

        if process.returncode != 0:
            if not self._stopped:
                print(f"Failed: {task.label}, exit code {process.returncode}")
                output = (stderr or stdout or "").strip()
                if output:
                    print(output[-2000:])  # last part of the exe output
            return False
        return True

    def stop(self):
        with self._lock:
            self._stopped = True
            for process in self._running:
                process.kill()
