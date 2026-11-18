from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import time

from .exe_runner import ExeRunner
from .task import Task


def run_tasks(tasks: list[Task], runner: ExeRunner, number_processes: int) -> tuple[int, list[Task]]:
    """Keeps exactly number_processes exe processes busy until all tasks are done.
    Returns the number of successful runs and the list of failed tasks."""

    n_tasks = len(tasks)
    n_success = 0
    failed_tasks = []
    start_time = time.monotonic()

    with ThreadPoolExecutor(max_workers=number_processes) as pool:
        try:
            futures = {pool.submit(runner.run, task): task for task in tasks}
            pending = set(futures)

            while pending:
                # The timeout keeps the main thread responsive to Ctrl+C (also on Windows)
                done, pending = wait(pending, timeout=1.0, return_when=FIRST_COMPLETED)

                for future in done:
                    task = futures[future]
                    try:
                        success = future.result()
                    except Exception as e:  # e.g. exe not found
                        print(f"Error: {task.label}: {e!r}")
                        success = False

                    if success:
                        n_success += 1
                    else:
                        failed_tasks.append(task)

                    n_done = n_success + len(failed_tasks)
                    elapsed = time.monotonic() - start_time
                    print(f"[{n_done}/{n_tasks}] Finished: {task.label}, elapsed {elapsed/60:.1f} min")

        except KeyboardInterrupt:
            # Stop scheduling and kill the running exe processes BEFORE leaving the with block,
            # otherwise the pool would keep starting the remaining tasks
            print("Interrupted, stopping workers ...")
            runner.stop()
            pool.shutdown(wait=True, cancel_futures=True)
            raise

    return n_success, failed_tasks
