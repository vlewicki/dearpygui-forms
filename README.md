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
