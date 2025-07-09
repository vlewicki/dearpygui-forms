import copy
from typing import Any

import dearpygui.dearpygui as dpg
from loguru import logger


from .models import PropertySchema


@logger.catch
def dereference_property(schema: dict[str, Any], defs: dict[str, Any]):
    if "$ref" in schema:
        path = schema["$ref"].split("/")[-1]
        new_schema = copy.deepcopy(defs[path])
        new_schema.update(copy.deepcopy(schema))
        del new_schema["$ref"]
    else:
        new_schema = copy.deepcopy(schema)
    return new_schema


class Widget:
    def __init__(self, schema: PropertySchema, defs: dict, **kwargs):
        self.schema = schema
        self._defs = defs
        self._kwargs = kwargs
        with dpg.stage() as self._staging_container_id:
            self._ui()

        if schema.default:
            self.set_value(schema.default)

    def _ui(self):
        dpg.add_text(f"Property {self.schema.title}, type: {self.schema.type}")

    def add(self):
        dpg.unstage(self._staging_container_id)

    def set_value(self, value: Any):
        pass

    def get_value(self) -> Any:
        pass



class ObjectWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._properties = {}
        super().__init__(schema, defs, **kwargs)

    def _ui(self):
        for property_name, property in self.schema.properties.items():
            property_widget = generate_widget(property, self._defs, generate_object=False)
            property_widget.add()
            self._properties[property_name] = property_widget

    def get_value(self) -> dict[str, Any]:
        return {property_name: property_widget.get_value() for property_name, property_widget in self._properties.items()}

    def set_value(self, value: dict[str, Any]):
        for property_name, property_widget in self._properties.items():
            property_widget.set_value(value.get(property_name))


class ArrayWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        super().__init__(schema, defs, **kwargs)


class MultiTypeWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._type_switcher_id = dpg.generate_uuid()
        self._widget: Widget | None = None
        self._widgets = [generate_widget(type_schema, defs) for type_schema in schema.anyOf]
        super().__init__(schema, defs, **kwargs)
        logger.debug(defs)


    def _ui(self):
        dpg.add_text(self.schema.title)
        with dpg.group(indent=10):
            dpg.add_combo(label="Type", tag=self._type_switcher_id, items=tuple(x.schema.title or x.schema.type for x in self._widgets), callback=self.switch_value_type)


    def switch_value_type(self, new_type):
        logger.debug(f"Switching to type {dpg.get_value(self._type_switcher_id)}")


    def get_value(self):
        if self._widget:
            return self._widget.get_value()
        else:
            return None

    def set_value(self, value):
        dpg.set_value(self._type_switcher_id, value)


class StringWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._input_id = dpg.generate_uuid()
        super().__init__(schema, defs, **kwargs)

    def _ui(self):
        dpg.add_input_text(label=self.schema.title, tag=self._input_id)

    def get_value(self):
        return dpg.get_value(self._input_id)

    def set_value(self, value):
        dpg.set_value(self._input_id, value)


class IntegerWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._input_id = dpg.generate_uuid()
        super().__init__(schema, defs, **kwargs)

    def _ui(self):
        dpg.add_input_int(label=self.schema.title, tag=self._input_id)

    def get_value(self):
        return dpg.get_value(self._input_id)

    def set_value(self, value):
        dpg.set_value(self._input_id, value)


class NumberWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._input_id = dpg.generate_uuid()
        super().__init__(schema, defs, **kwargs)

    def _ui(self):
        dpg.add_input_float(label=self.schema.title, tag=self._input_id)

    def get_value(self):
        return dpg.get_value(self._input_id)

    def set_value(self, value):
        dpg.set_value(self._input_id, value)


class BooleanWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._checkbox_id = dpg.generate_uuid()
        super().__init__(schema, defs, **kwargs)

    def _ui(self):
       dpg.add_checkbox(label=self.schema.title, tag=self._checkbox_id)

    def get_value(self):
        return dpg.get_value(self._checkbox_id)

    def set_value(self, value: bool):
        dpg.set_value(self._checkbox_id, value)

class NoneWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._none_id = dpg.generate_uuid()
        super().__init__(schema, defs, **kwargs)

    def _ui(self):
        dpg.add_input_text(default_value='<None>', label=self.schema.title, tag=self._none_id, enabled=False)

    def get_value(self):
        return None

    def set_value(self, value):
        pass


class ExternalWidget(Widget):
    def __init__(self, schema, defs, **kwargs):
        self._external_id = dpg.generate_uuid()
        super().__init__(schema, defs, **kwargs)

    def _ui(self):
        dpg.add_button(label=self.schema.title, tag=self._external_id, enabled=False)

    def get_value(self):
        return None

    def set_value(self, value):
        pass


def generate_widget(json_schema: dict[str, Any],  defs: dict[str, Any], generate_object: bool = True, **kwargs) -> Widget:
    schema = PropertySchema(dereference_property(json_schema, defs))
    match schema:
        case PropertySchema(type='object'):
            if generate_object:
                return ObjectWidget(schema, defs, **kwargs)
            else:
                raise NotImplementedError("ExternalWidget is not implemented yet")
                return ExternalWidget(schema, defs, **kwargs)
        case PropertySchema(type='array'):
            raise NotImplementedError("ArrayWidget is not implemented yet")
            return ArrayWidget(schema, defs, **kwargs)
        case PropertySchema(type='string'):
            return StringWidget(schema, defs, **kwargs)
        case PropertySchema(type='integer'):
            return IntegerWidget(schema, defs, **kwargs)
        case PropertySchema(type='number'):
            return NumberWidget(schema, defs, **kwargs)
        case PropertySchema(type='boolean'):
            return BooleanWidget(schema, defs, **kwargs)
        case PropertySchema(type='null'):
            return NoneWidget(schema, defs, **kwargs)
        case PropertySchema(anyOf=types) if len(types) > 0:
            raise NotImplementedError("MultiTypeWidget is not implemented yet")
            # return MultiTypeWidget(schema, defs, **kwargs)
        case _:
            raise ValueError(f"Unsupported schema: {schema}")
