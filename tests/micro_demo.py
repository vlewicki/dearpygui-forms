from pprint import pprint
import dearpygui.dearpygui as dpg
from pydantic import BaseModel, Field
from dearpygui_forms import DPGForm

class User(BaseModel):
    name: str = Field(default="John Doe", min_length=3)
    age: int = Field(ge=18)


class Storage(BaseModel):
    users: list[User] = []

class UserForm(DPGForm, model=User):
    pass


dpg.create_context()
dpg.create_viewport()

store = Storage()

with dpg.window(label="User Form"):
    user_form = UserForm(callback=lambda x: store.users.append(x))
    user_form.add()
    dpg.add_button(label="Print Users", callback=lambda: pprint(store.model_dump()))
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
