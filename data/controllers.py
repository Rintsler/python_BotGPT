import json
import random
import openai
from aiogram import types
from app.moduls import generate_response, profile
from app.update_keys import get_unused_key
from data.config import bot, chat_id
from data.db_app import add_user, get_flag, new_chat, get_user_history, update_user_history, \
    add_response_to_history, calculate_remaining_tokens, set_state_ai, get_state_ai
from nav.keyboard import inline_markup_reg, menu_keyboard, menu_profile, inline_submit_preview, inline_tp, menu_ai

options = [
    "🤔 Осторожно, работает умная машина...",
    "⏳ Подождите, я тут кручусь и думаю...",
    "🌟 Работаю над вашим запросом, скоро все будет!",
    "🧠 Мозговой штурм в процессе, немного терпения!"
]


async def start_cmd(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(
        f'Привет, {user_name}!\nДля пользования ботом, подпишитесь на наш новостной канал и нажмите "Готово". '
        f'Вы получите 10000 бесплатных токенов для текстовых ответов.', reply_markup=inline_markup_reg)


async def submit(call: types.CallbackQuery):
    user_id = call.from_user.id
    flag = await get_flag(user_id)
    if flag == 3:
        await bot.edit_message_text(
            'У вас действует месячная подписка. Отправьте мне ваш вопрос, и я постараюсь ответить.',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_submit_preview
        )
        await call.answer(f'У вас действует месячная подписка. Отправьте мне ваш вопрос, '
                          f'и я постараюсь ответить.', reply_markup=menu_keyboard)
    elif flag == 4:
        await call.answer(f'У вас действует подписка на 6 месяцев. '
                          f'Отправьте мне ваш вопрос, и я постараюсь ответить.',
                          reply_markup=menu_keyboard)
    elif flag == 5:
        await call.answer(
            f'У вас действует годовая подписка. Отправьте мне ваш вопрос, и я постараюсь ответить.',
            reply_markup=menu_keyboard)
    else:
        await bot.edit_message_text("Выберите тип подписки:",
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=inline_submit_preview)


async def tp(call: types.CallbackQuery):
    await bot.edit_message_text(
        'Этот раздел еще в разработке...',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=inline_tp
    )


async def back_to_profile(call: types.CallbackQuery):
    user_id = call.from_user.id
    profile_text = await profile(user_id)
    await bot.edit_message_text(profile_text,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=menu_profile
                                )


async def check_sub(call: types.CallbackQuery):
    user_id = call.from_user.id
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(member)
    if member.status != 'left':
        r_t = await calculate_remaining_tokens(user_id)
        flag = await get_flag(user_id)
        if flag == 0 or flag is None:
            username = call.from_user.username
            flag = 1
            tokens = 10000
            registration_date = call.message.date.strftime('%Y-%m-%d %H:%M:%S')
            await add_user(user_id, username, registration_date, tokens, flag)
            await call.message.answer(
                f'Спасибо за подписку на наш канал! У вас 10000 бесплатных токенов для запросов.',
                reply_markup=menu_keyboard)
        else:
            await call.message.answer(
                f'Спасибо за подписку на наш канал! У вас {r_t} бесплатных токенов для запросов.',
                reply_markup=menu_keyboard)
    else:
        await call.answer('Для начала подпишись на наш канал')


async def dalle_2(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = 'dally2'
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Ок! Дальше я на ваши сообщения буду отвечать изображениями 👩‍🎨')


async def dalle_3(call: types.CallbackQuery):
    await call.message.answer('Данный раздел находится в разработке, но скоро будет доступен...')


async def bot_dialog(call: types.CallbackQuery):
    user_id = call.from_user.id
    state_ai = ''
    await set_state_ai(user_id, state_ai)
    await call.message.answer('Понял! Возвращаемся к обычному общению.')


async def send_image(message):
    api_key = await get_unused_key()
    print(api_key)
    response = openai.Image.create(
        api_key=api_key,
        prompt=message.text,
        n=1,
        size="1024x1024",
    )
    await message.answer_photo(response["data"][0]["url"])


# ======================================================================================================================
#                                             Любой запрос
# ======================================================================================================================
async def echo(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    flag = await get_flag(user_id)
    r_tokens = await calculate_remaining_tokens(user_id)
    print(r_tokens)
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(member)
    if member.status != 'left':
        # ==================================================================================================================
        #                                             Профиль
        # ==================================================================================================================
        if text in ['📊 Профиль']:
            profile_text = await profile(user_id)
            await message.answer(profile_text, reply_markup=menu_profile)
        # ==================================================================================================================
        #                                             Нейросеть
        # ==================================================================================================================
        elif text in ['🧠 Нейросеть']:
            await message.answer('Теперь можете переключить нейросеть для ваших дальнейших запросов к боту',
                                 reply_markup=menu_ai)
        # ==================================================================================================================
        #                                             Создать чат
        # ==================================================================================================================
        elif text in ['👥 Создать чат']:
            await new_chat(user_id)
            await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.", reply_markup=menu_keyboard)
        # ==================================================================================================================
        #                                             Любой запрос к боту
        # ==================================================================================================================
        else:
            if flag > 0 and r_tokens > 0:
                user_question = message.text
                print(f"User question: {user_question}")
                state_ai = await get_state_ai(user_id)
                if state_ai == 'dalle2':
                    # Отправляем анимацию перед запросом к OpenAI GPT
                    processing_message = await message.answer(random.choice(options))
                    await send_image(message)
                    # Удаляем сообщение с анимацией перед отправкой ответа
                    await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)
                    return
                # Отправляем анимацию перед запросом к OpenAI GPT
                processing_message = await message.answer(random.choice(options))

                # Получаем текущую историю пользователя
                chat_history, response_history = await get_user_history(user_id)

                chat_history = json.loads(chat_history) if chat_history else []
                response_history = json.loads(response_history) if response_history else []

                # Добавляем новое сообщение к истории
                chat_history.append({"role": "user", "content": user_question})

                # Обновляем историю в базе данных
                await update_user_history(user_id, chat_history, response_history)

                # Имитация анимации перед запросом к OpenAI GPT завершена

                response = await generate_response(user_id, chat_history, message)
                print(f"OpenAI response: {response}")

                # Удаляем сообщение с анимацией перед отправкой ответа
                await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

                # Добавляем ответ к истории ответов
                response_history.append({"role": "assistant", "content": response})

                await add_response_to_history(user_id, response_history)

                await message.answer(response, reply_markup=menu_keyboard)

                await calculate_remaining_tokens(user_id)
            elif flag > 1:
                await message.answer("Ваши бесплатные токены на нуле, "
                                     "ждите понедельника или оформите подписку.", reply_markup=inline_submit_preview)
            else:
                await message.answer("Ваши бесплатные токены на нуле, "
                                     "ждите понедельника или зарегистрируйтесь и оформите подписку.",
                                     reply_markup=inline_markup_reg)
    else:
        await message.answer("Для использования бота подпишите на наш канал",
                             reply_markup=inline_markup_reg)
