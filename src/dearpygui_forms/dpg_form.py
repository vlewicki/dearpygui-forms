from pprint import pformat
from typing import Any, Type
import copy

import dearpygui.dearpygui as dpg
from loguru import logger


import loguru
import pydantic

from .models import PropertySchema


def dereference_property(schema: dict[str, Any], defs: dict[str, Any]):
    new_schema = {}
    if "$ref" in schema:
        path = schema["$ref"].split("/")[-1]
        logger.debug(f"Deref {schema}")

        new_schema = copy.deepcopy(defs[path])
    new_schema.update(schema)
    new_schema["$ref"]

    return new_schema


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


def _generate_property_form(schema: dict[str, Any], defs: dict[str, Any], generate_objects: bool = False):
    dereference_property(schema, defs)
    property = Property(schema)
    match property:
        case Property(type="object"):
            if generate_objects:
                loguru.logger.info(f"Generating form for object: {pformat(schema)}")
                with dpg.child_window(label=property.title, auto_resize_y=True):
                    for child_property_name, child_property_schema in property.properties.items():
                        _generate_property_form(child_property_schema, defs)
            else:
                widget = AttachModelWidget(copy.deepcopy(schema), defs)
                widget.add()
                schema["dpg_form_widget"] = widget.get_id()
        case Property(type="string"):
            schema["dpg_form_widget_id"] = dpg.add_input_text(label=property.title)
        case Property(type="integer"):
            schema["dpg_form_widget_id"] = dpg.add_input_int(label=property.title)
        case Property(type="boolean"):
            schema["dpg_form_widget_id"] = dpg.add_checkbox(label=property.title)
        case Property(type="number"):
            schema["dpg_form_widget_id"] = dpg.add_input_float(label=property.title)
        case Property(anyOf=available_types):
            logger.info(f"Available types: {available_types}")
        case _:
            raise NotImplementedError(f"Unsupported schema: {schema}")


@logger.catch
def _collect_schema_values(schema: dict[str, Any]):
    data = {}
    for property_name, property in schema["properties"].items():
        if property["type"] == "object":
            data[property_name] = dpg.get_item_user_data(property["dpg_form_widget"])
        else:
            data[property_name] = dpg.get_value(property["dpg_form_widget_id"])
    return data

class DPGSubform:
    def __init__(self, schema: dict[str, Any], defs: dict[str, Any], callback):
        self._schema = schema
        self._defs = defs
        with dpg.window(show=False) as self._window:
            logger.debug(f"Initializing form {self._schema}")
            _generate_property_form(self._schema, self._defs, generate_objects=True)
            dpg.add_button(label="Submit", callback=lambda: callback(self.get_form_data()))
            logger.debug(f"Form initialized {self._schema}")

    def get_form_data(self):
        return _collect_schema_values(self._schema)

    def show(self):
        dpg.show_item(self._window)



class AttachModelWidget:
    def __init__(self, schema: dict[str, Any], defs: dict[str, Any]):
        self._widget_id = dpg.generate_uuid()
        self._schema = schema
        self._defs = defs
        self._subform: DPGSubform | None = None
        with dpg.stage() as self._staging_container_id:
            dpg.add_button(tag=self._widget_id, label=f"+ {schema['title']}", callback=self.show_subform)
            dpg.set_item_user_data(self._widget_id, None)

    def add(self):
        dpg.unstage(self._staging_container_id)

    def get_id(self):
        return self._widget_id

    def show_subform(self):
        if self._subform is None:
            self._subform = DPGSubform(self._schema, self._defs, callback=lambda x: dpg.set_item_user_data(self._widget_id, x))
        self._subform.show()

class DPGForm:
    def __init_subclass__(cls, *, model: Type[pydantic.BaseModel]) -> None:
        cls._Model = model

    def __init__(self, callback):
        self.__model_schema = self._Model.model_json_schema()
        self.__model_schema, self.__models_defs = extract_defs(self.__model_schema)
        logger.debug(f"Initializing form {self.__model_schema}")
        with dpg.stage() as self._staging_container_id:
            _generate_property_form(self.__model_schema, self.__models_defs, generate_objects=True)
            dpg.add_button(label="Submit", callback=lambda: callback(self.get_form_data()))
        logger.debug(f"Form initialized {self.__model_schema}")

    def add(self):
        dpg.unstage(self._staging_container_id)

    def get_form_data(self):
        self._Model(**_collect_schema_values(self.__model_schema))


class Property:
    def __init__(self, schema, defs):
        self._schema = PropertySchema(schema)
        self._defs = defs

    def fill(self, value):
        pass

    def add(self):
        dpg.add_text(f"Property {self._schema.title}")
