# cpp-python-runner

Runs a command line executable (e.g. a C++ optimisation algorithm) for every combination of a
parameter grid x a list of instances x repetitions, with a fixed number of processes in parallel.

- Writes one JSON parameter file per grid combination (merged into a base parameter file).
- Keeps exactly `number_processes` exe processes busy, in a reproducible random order.
- Ctrl+C kills all running exe processes and deletes the output of the interrupted experiment.
- Failed runs are listed in `<output_folder>/../<name>_failed_tasks.json`.

## Installation

```bash
pip install -e path/to/cpp-python-runner          # development, changes apply immediately
pip install "cpp-python-runner @ git+https://github.com/MxHbm/cpp-python-runner.git@v0.1.0"
```

## Usage

The package knows nothing about your executable. You describe its command line with `build_command`:

```python
from pathlib import Path
from cpp_python_runner import Experiment, Task, run_experiment

EXE = Path("build/Release/bin/Release/AlgorithmApplication.exe")

def build_command(task: Task, output_folder: Path) -> list:
    return [EXE,
            "-i", task.instances_folder, "-f", task.instance_file,
            "-o", output_folder,
            "-c", task.parameter_folder, "-p", task.parameter_file,
            "-r", task.repetition]

experiment = Experiment(
    name="my_study",
    parameter_study={"algorithm_config": {"setup": [0, 300], "max_lots": [1, 10]}},
    base_parameter_file=Path("data/input/parameters/base.json"),
    instances_folder=Path("data/input/instances"),
    instance_files=["inst_1.json", "inst_2.json"],
    output_folder=Path("data/output/my_study"),
    build_command=build_command,
    repetitions=3,
    number_processes=8,
)

if __name__ == "__main__":
    result = run_experiment(experiment)
    print(result.n_success, "of", result.n_tasks, "runs successful")
```

`parameter_study` is a nested dict whose leaves are lists. Every combination becomes its own file
`Parameters_<n>.json`; an empty dict runs the base parameter file once. The parameter files are written into a
unique temporary folder (inside `temp_parameter_folder` if given) that is deleted after the experiment.

`run_experiment` returns an `ExperimentResult` with `n_tasks`, `n_success`, `failed_tasks` and
`new_run_folders` (only the folders created by this experiment). Post-processing of the results and
notifications are left to the caller.

## Tests

```bash
pip install -e ".[test]"
pytest
```
