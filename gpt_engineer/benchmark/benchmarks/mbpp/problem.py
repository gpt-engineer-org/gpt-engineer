from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Problem:
    source_file: int
    task_id: str
    prompt: str
    code: str
    test_imports: str
    test_list: List[str]

    @property
    def starting_code(self) -> str:
        lines: List[str] = []

        for line in self.code.split("\n"):
            lines.append(line)

            if line.startswith("def "):
                lines.append("pass #  TODO: Implement method\n")
                break

        return "\n".join(lines)
