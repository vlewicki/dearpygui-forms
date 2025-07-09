import datetime
import decimal
from pprint import pprint
import dearpygui.dearpygui as dpg

import dearpygui.dearpygui as dpg
from loguru import logger
from pydantic import BaseModel, Field

from dearpygui import demo
import pydantic
from dearpygui_forms import DPGForm


class Tool(BaseModel):
    name: str = Field(title="Tool name", min_length=1)
    price: float = Field(title="Price", ge=0)
    quantity: int = Field(title="Quantity", ge=0)

class User(BaseModel):
    name: str = Field(title="User name", min_length=1)
    birthday: datetime.date = datetime.date(2000, 1, 1)
    wakeup: datetime.time = datetime.time(8, 0)
    next_departure: datetime.datetime = datetime.datetime.now()
    fingers_on_the_hand: int = 5
    weight: float = 60.0
    pi: decimal.Decimal = decimal.Decimal('3.1415')
    male: bool = True
    tool: Tool | int
    best_friend: 'User' = Field(title='Best friend')
    zero: None
    # friends: list['User']


class UserForm(DPGForm, model=User):
    pass

class ToolForm(DPGForm, model=Tool):
    pass


def main():
    with dpg.font_registry():
        default_font = dpg.add_font('data/fonts/Roboto-Regular.ttf', 22) # install manualy
        dpg.bind_font(default_font)

    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_Escape, callback=dpg.stop_dearpygui)

    with dpg.viewport_menu_bar():
        with dpg.menu(label='Window'):
            dpg.add_menu_item(label='Fullscreen', callback=dpg.toggle_viewport_fullscreen, check=True)
            dpg.add_menu_item(label='Quit', shortcut='Esc', callback=dpg.stop_dearpygui)
        with dpg.menu(label='Debug'):
            dpg.add_menu_item(label='Debug', callback=dpg.show_debug)
            dpg.add_menu_item(label='Item registry', callback=dpg.show_item_registry)
            dpg.add_menu_item(label='Metrics', callback=dpg.show_metrics)
            dpg.add_menu_item(label='Font manager', callback=dpg.show_font_manager)
            dpg.add_separator(label='Other')
            dpg.add_menu_item(label='DearPyGUI demo', callback=demo.show_demo)
            dpg.add_menu_item(label='Imgui demo', callback=dpg.show_imgui_demo)
            dpg.add_menu_item(label='Implot demo', callback=dpg.show_implot_demo)
            dpg.add_menu_item(label='About', callback=dpg.show_about)

    with dpg.window(label="Template", width=641, height=480):
        UserForm(lambda x: logger.success(x)).add()
        tf = ToolForm(lambda x: logger.success(x))
        tf.add()
        t = Tool(name='Tool', price=100.55, quantity=22)
        tf.fill_form(t)



if __name__ == '__main__':
    dpg.create_context()
    dpg.create_viewport()
    dpg.configure_app(docking=True, docking_space=True, load_init_file='dpg.ini', auto_save_init_file=True)
    main()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
