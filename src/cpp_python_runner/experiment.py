from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from . import defaults
from .task import Task

# Builds the command line for one task: (task, output_folder) -> argument list, first element is the exe
CommandBuilder = Callable[[Task, Path], list[str]]


@dataclass(frozen=True)
class Experiment:
    """Everything needed for one parameter study.

    parameter_study
        Nested dict whose leaves are lists, e.g. {"algorithm_config": {"setup": [0, 300]}}.
        Every combination of the list values is written into its own parameter file.
    base_parameter_file
        JSON file the combinations are merged into.
    instance_files
        File names of the instances (inside instances_folder) every parameter file is run with.
    build_command
        Turns a task into the command line of the executable (see CommandBuilder).
    temp_parameter_folder
        Parent folder for the generated parameter files. A unique subfolder is created per run and
        deleted afterwards; None uses the system temp folder.
    cwd
        Working directory of the exe processes; None uses the current working directory.
    """

    name: str
    parameter_study: dict
    base_parameter_file: Path
    instances_folder: Path
    instance_files: Sequence[str]
    output_folder: Path
    build_command: CommandBuilder
    temp_parameter_folder: Path | None = None
    cwd: Path | None = None
    repetitions: int = defaults.REPETITIONS
    number_processes: int = defaults.NUMBER_PROCESSES
    shuffle_tasks: bool = defaults.SHUFFLE_TASKS
    shuffle_seed: int | None = defaults.SHUFFLE_SEED
