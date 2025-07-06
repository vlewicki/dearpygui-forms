"""
Dearpygui extention for autogeneration forms powered by pydantic.
"""
import decimal
from typing import Any, Type
from pprint import pformat


import dearpygui.dearpygui as dpg
from loguru import logger
import pydantic


from .dpg_form import DPGForm

def parse_property_type(property_schema: dict[str, Any]) -> str:
    property_type = property_schema.get("type", None)
    if property_type is None:
        any_of = property_schema.get("anyOf", None)
        if any_of is None:
            raise ValueError(f"Property type not detected. {property_schema}")

        # Text input field preferred for Decimal type than float input field
        if 'string' in map(lambda x: x.get("type"), any_of):
            property_type = 'string'
        else:
            property_type =  any_of[0].get("type", None)

        if property_type is None:
            raise ValueError(f"Property type not detected. {property_schema}")
    return property_type

class DPGFormLegacy:
    """
    Base class for dearpygui forms.
    Sublasses must define `__pydantic_model__` with some Pydantic model type.

    # Example:
    ```python
    import dearpygui.dearpygui as dpg
    from pydantic import BaseModel
    from dearpygui_forms import DPGForm

    class User(BaseModel):
        name: str
        age: int

    class UserForm(DPGForm):
        __pydantic_model__ = User

    dpg.create_context()
    dpg.create_viewport()
    with dpg.window(label="User Form"):
        user_form = UserForm(callback=lambda x: print(x))
        user_form.add()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
    ```
    """
    __pydantic_model__: Type[pydantic.BaseModel]

    def __init__(self, callback):
        """
        Initializes the UserForm instance.

        Args:
            callback (Callable): The callback function to be called with a validated pydantic model.
        """
        self.callback = callback
        logger.debug(self.__pydantic_model__)
        self.model_schema = self.__pydantic_model__.model_json_schema()
        logger.debug(pformat(self.model_schema))

    def add(self):
        """Adds form as child_window dearpygui element."""
        schema = self.model_schema
        with dpg.child_window(label=schema["title"]):
            for property_name, property_schema in schema["properties"].items():
                property_type = parse_property_type(property_schema)
                default_value = property_schema.get("default")
                if property_type == "string":
                    schema["properties"][property_name]["dpg_form_id"] = \
                    dpg.add_input_text(label=property_schema["title"], default_value=default_value or '')
                elif property_type == "integer":
                    schema["properties"][property_name]["dpg_form_id"] = \
                    dpg.add_input_int(label=property_schema["title"], default_value=default_value or 0)
                elif property_type == "number":
                    schema["properties"][property_name]["dpg_form_id"] = \
                    dpg.add_input_float(label=property_schema["title"], default_value=float(default_value or 0))
                elif property_type == "boolean":
                    schema["properties"][property_name]["dpg_form_id"] = \
                    dpg.add_checkbox(label=property_schema["title"], default_value=default_value or False)
                elif property_type == "array":
                    schema["properties"][property_name]["dpg_form_id"] = \
                    dpg.add_input_text(label=property_schema["title"])
                elif property_type == "object":
                    schema["properties"][property_name]["dpg_form_id"] = \
                    dpg.add_input_text(label=property_schema["title"])
                else:
                    raise ValueError(f"Unsupported type: {property_type}")

            dpg.add_button(label="Submit", callback=self.submit)

        logger.debug(pformat(self.model_schema))

    def submit(self):
        try:
            data = self._handle_data()
        except pydantic.ValidationError as e:
            with dpg.window(label="Validation error", modal=True):
                dpg.add_text(str(e))
        else:
            self.callback(data)

    def _handle_data(self):
        json_data = {}
        for property_name, property_schema in self.model_schema["properties"].items():
            form_id = property_schema["dpg_form_id"]
            if form_id is not None:
                json_data[property_name] = dpg.get_value(form_id)
            else:
                raise ValueError(f"Missing form ID for property: {property_name}")

        return self.__pydantic_model__(**json_data)
