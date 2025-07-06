from pprint import pformat
from typing import Any, Type

import dearpygui.dearpygui as dpg
from loguru import logger


import loguru
import pydantic

from .models import Property


def derefesrence_property(schema: dict[str, Any], defs: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in schema:
        path = schema["$ref"].split("/")[-1]
        return defs[path]
    else:
        return schema


def extract_defs(schema: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """split schema on root models schema and $defs"""
    if "$defs" in schema:
        defs = schema["$defs"]
        del schema["$defs"]
        root_model_schema =  schema
    else:
        defs = {}
        root_model_schema = schema
    return root_model_schema, defs


class DPGForm:
    def __init_subclass__(cls, *, model: Type[pydantic.BaseModel]) -> None:
        cls._Model = model
        cls.__model_schema = model.model_json_schema()
        cls.__model_schema, cls.__models_defs = extract_defs(cls.__model_schema)

    def __init__(self, callback):
        with dpg.stage() as self._staging_container_id:
            self._generate_property_form(self.__model_schema, generate_objects=True)
            dpg.add_button(label="Submit", callback=lambda: callback(self.get_form_data()))

    def add(self):
        dpg.unstage(self._staging_container_id)

    def get_form_data(self):
        pass

    def _generate_property_form(self, schema: dict[str, Any], generate_objects=False, placeholder_id=None):
        if placeholder_id is not None:
            parent = dpg.get_item_parent(placeholder_id)
            if parent is None:
                raise RuntimeError("Placeholder parent not found")

            dpg.delete_item(placeholder_id)
            dpg.push_container_stack(parent)

        schema = derefesrence_property(schema, self.__models_defs)
        property = Property(schema)
        logger.info(schema)
        match property:
            case Property(type="object"):
                if generate_objects:
                    with dpg.child_window(label=property.title, auto_resize_y=True):
                        for child_property_name, child_property_schema in property.properties.items():
                            self._generate_property_form(child_property_schema)
                else:
                    placeholder = dpg.generate_uuid()
                    dpg.add_button(label=f"Add {property.title}",
                        tag=placeholder,
                        callback=lambda: self._generate_property_form(schema, generate_objects=True, placeholder_id=placeholder))
            case Property(type="string"):
                dpg.add_input_text(label=property.title)
            case Property(type="integer"):
                dpg.add_input_int(label=property.title)
            case Property(type="boolean"):
                dpg.add_checkbox(label=property.title)
            case Property(type="number"):
                dpg.add_input_float(label=property.title)
            case Property(anyOf=available_types):
                logger.info(f"Available types: {available_types}")
            case _:
                raise NotImplementedError(f"Unsupported schema: {schema}")

        if placeholder_id is not None:
            dpg.pop_container_stack()


def add_form(schema: dict[str, Any]):
    """Add form corresponding to schema as dpg child window
    # Example
    ```python
    import dearpygui.dearpygui as dpg
    from pydantic import BaseModel
    from dearpygui_forms import add_form

    class User(BaseModel):
        name: str
        age: int

    # DPG initialization ...

    with dpg.window():
        add_form(User.model_json_schema())

    # DPG running ...
    ```
    """
    logger.debug(pformat(schema))
