"""Run a command line executable for a grid of parameter files x instances in parallel."""

from .exe_runner import ExeRunner
from .experiment import CommandBuilder, Experiment
from .parameter_files import deep_update, expand_parameter_grid, write_parameter_files
from .runner import ExperimentResult, build_tasks, run_experiment
from .scheduler import run_tasks
from .task import Task

__version__ = "0.1.0"

__all__ = [
    "CommandBuilder", "ExeRunner", "Experiment", "ExperimentResult", "Task",
    "build_tasks", "deep_update", "expand_parameter_grid", "run_experiment",
    "run_tasks", "write_parameter_files",
]
