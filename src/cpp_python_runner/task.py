from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Task:
    """One run of the executable: one instance file with one parameter file and one repetition."""

    instance_file: str
    instances_folder: Path
    parameter_file: str
    parameter_folder: Path
    repetition: int

    @property
    def label(self) -> str:
        return f"{self.instance_file} with {self.parameter_file} (rep {self.repetition})"

    def to_dict(self) -> dict:
        return {"instance": self.instance_file,
                "parameters": self.parameter_file,
                "rep": self.repetition}
