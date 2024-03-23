import json

from dataclasses import dataclass
from functools import cached_property
from typing import List


@dataclass(frozen=True)
class Problem:
    id: int
    question: str
    input_output: str
    starter_code: str

    @property
    def inputs(self) -> List[str]:
        return self._parsed_inputs_outputs["inputs"]

    @property
    def outputs(self) -> List[str]:
        return self._parsed_inputs_outputs["outputs"]

    @cached_property
    def _parsed_inputs_outputs(self):
        return json.loads(self.input_output.replace("\n", ""))
