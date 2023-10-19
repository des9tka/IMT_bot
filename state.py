from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class BotState(StatesGroup):
    sett_up = State()
    message_id = State()
    session_name = State
    command_name = State()
    language = State()
    voice_assistant = State()
    image = State()
    additional = State()


async def state_setup(state: FSMContext):
    await state.set_state(BotState)
    await state.update_data(set_up=True)
    await state.update_data(message_id=None)
    await state.update_data(session_name=None)
    await state.update_data(command_name='No_command')
    await state.update_data(language='ru-RU')
    await state.update_data(voice_assistant='OFF')
    await state.update_data(subject=None) # extra information about subject
    await state.update_data(additional=None) # additional statement for lifting information
