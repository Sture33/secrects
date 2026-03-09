from aiogram.fsm.state import StatesGroup, State

class AnonStates(StatesGroup):
    in_choose = State()
    only_text = State()
    with_media = State()
