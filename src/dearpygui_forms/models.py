from typing import Any, Literal
from pydantic import BaseModel


class PropertySchema:
    def __init__(self, schema: dict[str, Any]) -> None:
        self.title: str | None = schema.get("title", None)
        self.type: str | None = schema.get("type", None)
        self.anyOf: list[dict[str, Any]] = schema.get("anyOf", [])
        self.properties: dict[str, dict[str, Any]] = schema.get("properties", {})
        self.default = schema.get("default", None)

    def __repr__(self) -> str:
        return f"PropertySchema(title={self.title}, type={self.type}, anyOf={self.anyOf}, properties={self.properties}, default={self.default})"
