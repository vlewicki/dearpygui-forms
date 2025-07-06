from typing import Any, Literal
from pydantic import BaseModel


class Property:
    def __init__(self, schema: dict[str, Any]) -> None:
        self.title: str = schema.get("title", "Noname")
        self.type = schema.get("type", None)
        if self.type is None:
            self.anyOf = schema.get("anyOf", [])
        self.properties: dict = schema.get("properties", {})
        self.default = schema.get("default", None)
