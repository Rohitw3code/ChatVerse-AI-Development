from dataclasses import dataclass, asdict
from typing import Any, Dict, Union, Optional


@dataclass
class ToolOutput:
    output: Optional[Union[str, Dict[str, Any]]] = None
    type: str = "tool"
    show: bool = False

    def __post_init__(self):
        if self.output is None:  # Case 1: Nothing passed
            self.output = {"content": "No output"}
        elif isinstance(self.output, str):  # Case 2: String passed
            self.output = {"content": self.output}
        elif isinstance(self.output, dict):  # Case 3: Dict passed
            pass  # leave as-is
        else:
            print("out : ", self.output)
            raise TypeError("output must be str, dict, or None")

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        return asdict(self)
