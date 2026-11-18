from dataclasses import dataclass, field
from pathlib import Path
import json
import random
import shutil
import tempfile

from .exe_runner import ExeRunner
from .experiment import Experiment
from .parameter_files import write_parameter_files
from .scheduler import run_tasks
from .task import Task


@dataclass
class ExperimentResult:
    n_tasks: int
    n_success: int
    failed_tasks: list[Task] = field(default_factory=list)
    # Run folders created by this experiment (older entries of output_folder are not included)
    new_run_folders: set[Path] = field(default_factory=set)


def build_tasks(experiment: Experiment, parameter_files: list[str], parameter_folder: Path) -> list[Task]:
    """One task per parameter file x instance x repetition, shuffled if the experiment says so."""

    tasks = [Task(instance_file=instance_file,
                  instances_folder=experiment.instances_folder,
                  parameter_file=parameter_file,
                  parameter_folder=parameter_folder,
                  repetition=rep + 1)
             for parameter_file in parameter_files
             for instance_file in experiment.instance_files
             for rep in range(experiment.repetitions)]

    if experiment.shuffle_tasks:
        random.Random(experiment.shuffle_seed).shuffle(tasks)

    return tasks


def _remove(paths):
    for path in paths:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))


def run_experiment(experiment: Experiment) -> ExperimentResult:
    """Writes the parameter files, runs all tasks in parallel and returns the result.

    Raises RuntimeError if the number of new output folders does not match the successful runs.
    On Ctrl+C all running exe processes are killed, the output of this experiment is deleted and
    the KeyboardInterrupt is raised again.
    """

    print(f"Starting experiment {experiment.name}!")

    experiment.output_folder.mkdir(parents=True, exist_ok=True)

    # Remember existing run folders, so only the results of this experiment are counted and deleted
    existing_run_folders = set(experiment.output_folder.iterdir())
    if existing_run_folders:
        print(f"Warning: {experiment.output_folder} already contains {len(existing_run_folders)} entries from earlier runs!")

    # Own folder per run: deleting it afterwards can never hit files of the user or of a parallel run
    if experiment.temp_parameter_folder is not None:
        experiment.temp_parameter_folder.mkdir(parents=True, exist_ok=True)
    parameter_folder = Path(tempfile.mkdtemp(prefix=f"{experiment.name}_", dir=experiment.temp_parameter_folder))

    runner = ExeRunner(experiment.build_command, experiment.output_folder, experiment.cwd)

    try:
        parameter_files = write_parameter_files(experiment.parameter_study, experiment.base_parameter_file, parameter_folder)
        tasks = build_tasks(experiment, parameter_files, parameter_folder)
        print(f"{len(parameter_files)} parameter combinations, {len(tasks)} tasks, "
              f"{experiment.number_processes} running in parallel")

        n_success, failed_tasks = run_tasks(tasks, runner, experiment.number_processes)

        new_run_folders = set(experiment.output_folder.iterdir()) - existing_run_folders
        print(f"\nSuccessful runs: {n_success} of {len(tasks)}")
        print(f"New output folders created: {len(new_run_folders)}")

        if failed_tasks:
            failed_file = experiment.output_folder.parent / f"{experiment.name}_failed_tasks.json"
            with open(failed_file, "w") as f:
                json.dump([t.to_dict() for t in failed_tasks], f, indent=4)
            print(f"Warning: {len(failed_tasks)} runs failed, list saved to {failed_file}")

        if len(new_run_folders) != n_success:
            raise RuntimeError(f"Number of new output folders ({len(new_run_folders)}) and "
                               f"successful runs ({n_success}) is not equal!")

        return ExperimentResult(len(tasks), n_success, failed_tasks, new_run_folders)

    except KeyboardInterrupt:
        # run_tasks has already killed all exe processes, so nothing writes into the output folder anymore
        _remove(set(experiment.output_folder.iterdir()) - existing_run_folders)
        raise

    finally:
        _remove([parameter_folder])
