import json
import sys
from pathlib import Path

from cpp_python_runner import Experiment, expand_parameter_grid, run_experiment, write_parameter_files


def test_expand_parameter_grid_nested():
    grid = expand_parameter_grid({"a": {"x": [1, 2], "y": ["u"]}, "b": [3, 4]})
    assert len(grid) == 4
    assert {"a": {"x": 2, "y": "u"}, "b": 4} in grid


def test_expand_parameter_grid_empty_runs_base_once():
    assert expand_parameter_grid({}) == [{}]


def test_write_parameter_files_uses_one_combination_per_file(tmp_path):
    base = tmp_path / "base.json"
    base.write_text(json.dumps({"algorithm_config": {"setup": 0, "max_lots": 1, "keep": True}}))

    files = write_parameter_files({"algorithm_config": {"setup": [0, 300]}}, base, tmp_path / "out")

    contents = [json.loads((tmp_path / "out" / f).read_text()) for f in files]
    assert [c["algorithm_config"]["setup"] for c in contents] == [0, 300]
    assert all(c["algorithm_config"]["keep"] is True for c in contents)  # nested keys are merged, not replaced


def _fake_exe_command(task, output_folder):
    """Uses the Python interpreter as 'exe': creates one run folder per task."""
    run_folder = Path(output_folder) / f"{Path(task.instance_file).stem}_{Path(task.parameter_file).stem}_{task.repetition}"
    script = ("import sys, pathlib; p = pathlib.Path(sys.argv[1]); p.mkdir(); "
              "(p / 'Parameters.json').write_text(pathlib.Path(sys.argv[2]).read_text())")
    return [sys.executable, "-c", script, run_folder, task.parameter_folder / task.parameter_file]


def test_run_experiment_end_to_end(tmp_path):
    base = tmp_path / "base.json"
    base.write_text(json.dumps({"setup": 0}))

    experiment = Experiment(name="test",
                            parameter_study={"setup": [0, 300]},
                            base_parameter_file=base,
                            instances_folder=tmp_path,
                            instance_files=["inst_1.json", "inst_2.json"],
                            output_folder=tmp_path / "output",
                            build_command=_fake_exe_command,
                            temp_parameter_folder=tmp_path / "temp",
                            repetitions=2,
                            number_processes=2)

    result = run_experiment(experiment)

    assert result.n_tasks == result.n_success == 2 * 2 * 2
    assert not result.failed_tasks
    assert len(result.new_run_folders) == 8
    assert list((tmp_path / "temp").iterdir()) == []  # temporary parameter files are removed
