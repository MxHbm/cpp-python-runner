import copy
import itertools
import json
from pathlib import Path


def deep_update(target: dict, source: dict) -> dict:
    """Merges source into target (in place), nested dicts are merged instead of replaced."""
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_update(target[key], value)
        else:
            target[key] = value
    return target


def expand_parameter_grid(parameter_study: dict) -> list[dict]:
    """Returns one nested dict per combination of the list values (any nesting depth).

    >>> expand_parameter_grid({"a": {"x": [1, 2]}, "b": [3]})
    [{'a': {'x': 1}, 'b': 3}, {'a': {'x': 2}, 'b': 3}]
    """

    def leaves(node, path=()):
        for key, value in node.items():
            if isinstance(value, dict):
                yield from leaves(value, path + (key,))
            else:
                if not isinstance(value, (list, tuple)):
                    raise TypeError(f"Value of {'/'.join(path + (key,))} must be a list, got {value!r}")
                yield path + (key,), value

    leaf_list = list(leaves(parameter_study))
    if not leaf_list:
        return [{}]  # no study: run the base parameter file once

    paths, values = zip(*leaf_list)
    combinations = []
    for combo in itertools.product(*values):
        combination = {}
        for path, value in zip(paths, combo):
            target = combination
            for key in path[:-1]:
                target = target.setdefault(key, {})
            target[path[-1]] = value
        combinations.append(combination)
    return combinations


def write_parameter_files(parameter_study: dict, base_parameter_file: Path, target_folder: Path) -> list[str]:
    """Writes one file Parameters_<n>.json per combination into target_folder and returns the file names."""

    with open(base_parameter_file, "r") as f:
        base = json.load(f)

    target_folder.mkdir(parents=True, exist_ok=True)
    file_names = []
    for counter, combination in enumerate(expand_parameter_grid(parameter_study)):
        data = deep_update(copy.deepcopy(base), combination)
        file_name = f"Parameters_{counter}.json"
        with open(target_folder / file_name, "w") as f:
            json.dump(data, f, indent=4)
        file_names.append(file_name)
    return file_names
