from pprint import pformat
from typing import Any, Type
import copy

import pydantic
import dearpygui.dearpygui as dpg
from loguru import logger


from .models import PropertySchema
from .widgets import *
from . import exceptions


def extract_defs(schema: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """split schema on root models schema and $defs"""
    schema = copy.deepcopy(schema)
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

    def __init__(self, callback):
        model_schema, models_defs = extract_defs(self._Model.model_json_schema())
        self._model_widget = generate_widget(model_schema, models_defs)
        self._callback = callback

    def add(self):
        self._model_widget.add()
        dpg.add_button(label="Submit", callback=self._on_submit)

    def fill_form(self, data_model: pydantic.BaseModel):
        self._model_widget.set_value(data_model.model_dump())

    def _on_submit(self):
        try:
            data = self._Model(**self._model_widget.get_value())
        except pydantic.ValidationError as e:
            with dpg.window(modal=True, label="Validation Error"):
                dpg.add_text(f"Validation error: {e}")
        except exceptions.DearpyguiFormsError as e:
            with dpg.window(modal=True, label="Form Error"):
                dpg.add_text(f"Form error: {e}")
        else:
            self._callback(data)

    def get_form_data(self):
        return self._Model(**self._model_widget.get_value())
