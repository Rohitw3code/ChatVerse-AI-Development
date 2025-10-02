# node_registry.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Literal, List

NodeType = Literal["starter", "planner", "supervisor", "agent", "tool"]


@dataclass
class NodeSpec:
    name: str
    type: NodeType
    run: Callable
    prompt: Optional[str] = None

    def doc(self, func_type: str = "agent") -> str:
        """Get the node's docstring (used as prompt info)."""
        if func_type == "supervisor":
            return (self.run.__doc__ + " (Tool) " or "").strip()
        else:
            return getattr(self.run, "description", "").strip()


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: Dict[str, NodeSpec] = {}

    def add(
            self,
            name: str,
            run: Callable,
            type: NodeType,
            prompt: str = "") -> None:
        if name in self._nodes:
            raise ValueError(f"Node '{name}' is already registered.")
        self._nodes[name] = NodeSpec(
            name=name, type=type, run=run, prompt=prompt)

    def get(self, name: str) -> Optional[NodeSpec]:
        return self._nodes.get(name)

    def get_type(self, name: str) -> Optional[NodeType]:
        spec = self.get(name)
        return spec.type if spec else None

    def all(self) -> List[NodeSpec]:
        return list(self._nodes.values())

    def members(self) -> List[str]:
        return [s.name for s in self._nodes.values()]

    def tools(self) -> dict[str, Callable]:
        """Return only registered tool nodes as {name: run_fn}."""
        return {spec.name: spec.run for spec in self._nodes.values()}

    def runs(self) -> List[Callable]:
        """Return the `run` function for all registered nodes."""
        return [spec.run for spec in self._nodes.values()]

    def prompt_block(self, func_type: str = "agent") -> str:
        # Build a prompt listing from docstrings only
        lines = []
        for s in self._nodes.values():
            # if s.type == "supervisor":
            doc = s.prompt
            # else:
            #     doc = s.doc(func_type.lower()) or "(no description)"
            lines.append(f"- {s.name} [{s.type}]: {doc}")
        return "\n".join(lines)
