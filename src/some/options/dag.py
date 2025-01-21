from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Callable, Set, Any, Optional, Dict

from some.types import T, Status, Error, UnwrapOr, FnType


@dataclass
class Node:
    id: str
    computation: Callable[[], T]
    dependencies: Set[str] = field(default_factory=set)
    value: Any = None
    error: Optional[Exception] = None
    state: Status = Status.PENDING
    name: Optional[str] = None

    def __repr__(self):
        return f"Node(id={self.id}, state={self.state}, value={self.value}, error={self.error}, dependencies={self.dependencies})"


class DAG:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def get_execution_order(self) -> list[str]:
        """Returns nodes in topological order."""
        visited = set()
        temp_mark = set()
        order = []

        def visit(node_id: str):
            if node_id in temp_mark:
                raise ValueError("Cyclic dependency detected!")
            if node_id not in visited:
                temp_mark.add(node_id)
                node = self.nodes[node_id]
                for dep in node.dependencies:
                    visit(dep)
                temp_mark.remove(node_id)
                visited.add(node_id)
                order.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                visit(node_id)

        return order

    def execute(self) -> Dict[str, Any]:
        """Executes the DAG in topological order."""
        results = {}
        for node_id in self.get_execution_order():
            node = self.nodes[node_id]
            try:
                node.value = node.computation()
                node.state = Status.OK
                results[node_id] = node.value
            except Exception as e:
                node.error = e
                node.state = Status.ERROR
                results[node_id] = Error(e)

        return results

    def __repr__(self):
        return f"DAG(nodes={self.nodes})"


# Global DAG instance
_global_dag = DAG()


class LazyDAGSome(UnwrapOr[T]):
    def __init__(
        self,
        computation: Callable[[], T],
        dependencies: Set[LazyDAGSome] = None,
        name: str = None,
    ):
        self.id = str(uuid.uuid4())
        self.dependencies = dependencies or set()
        self._computation = computation
        self._state = Status.PENDING
        self._value: Optional[T] = None
        self._error: Optional[Exception] = None

        # Create node and add to DAG
        node = Node(
            id=self.id,
            computation=self._wrapped_computation(),
            dependencies={dep.id for dep in self.dependencies},
            name=name,
        )
        _global_dag.add_node(node)

    def _wrapped_computation(self) -> Callable[[], T]:
        """Wraps the computation to handle dependency results."""

        def wrapped():
            return self._computation()

        return wrapped

    def unwrap(self):
        node = _global_dag.nodes[self.id]
        if node.state == Status.PENDING:
            try:
                _global_dag.execute()
            except Exception as e:
                raise e
        if node.state == Status.OK:
            return node.value
        if node.state == Status.ERROR:
            raise node.error

    def unwrap_or(self, default: T) -> T | Error:
        node = _global_dag.nodes[self.id]
        if node.state == Status.PENDING:
            try:
                _global_dag.execute()
            except Exception as e:
                raise default

        if node.state == Status.OK:
            return node.value
        elif node.state == Status.ERROR:
            return default

    def map(self, fn: Callable[[T], Any]) -> LazyDAGSome:
        def new_computation():
            result = self.unwrap()
            return fn(result)

        return LazyDAGSome(new_computation, dependencies={self})

    def __repr__(self):
        node = _global_dag.nodes[self.id]
        status_str = node.state.value.lower().capitalize()
        name_str = f":{node.name}" if node.name else ""

        if node.state == Status.PENDING:
            return f"LazyDAGSome{status_str}{name_str}(<pending>)"
        elif node.state == Status.OK:
            return f"LazyDAGSome{status_str}{name_str}({node.value})"
        else:
            return f"LazyDAGSome{status_str}{name_str}({node.error})"


LazyDAGSomeFnType = Callable[..., LazyDAGSome[T]]
