import json
import random
import openai
from aiogram import types
from app.moduls import generate_response, profile
from app.update_keys import get_unused_key
from data.config import bot
from data.db_app import add_user, reg_user, get_flag, new_chat, get_user_history, update_user_history, \
    add_response_to_history, calculate_remaining_tokens
from nav.keyboard import inline_markup_reg, menu_keyboard, menu_profile, inline_submit_preview, inline_tp, menu_ai

STATE = ''

options = [
    "🤔 Осторожно, работает умная машина...",
    "⏳ Подождите, я тут кручусь и думаю...",
    "🌟 Работаю над вашим запросом, скоро все будет!",
    "🧠 Мозговой штурм в процессе, немного терпения!"
]


async def start_cmd(message: types.Message):
    username = message.from_user.username
    await message.answer(f'Привет, {username}!\nДля пользования ботом, подпишитесь на наш новостной канал и вы получите'
                         f'10000 бесплатных токенов для текстовых ответов.', reply_markup=inline_markup_reg)


async def in_to_db(call: types.CallbackQuery):
    user_id = call.from_user.id
    flag = await get_flag(user_id)
    await calculate_remaining_tokens(user_id)
    if flag == 0 or flag is None:
        flag = 1
        tokens = 10000
        username = call.from_user.username
        await calculate_remaining_tokens(user_id)
        await add_user(user_id, username, tokens, flag)
    await call.message.answer('Типа подписался...', reply_markup=menu_keyboard)
    # elif flag == 3:
    #     await call.answer(f'У вас действует месячная подписка. Отправьте мне ваш вопрос, '
    #                          f'и я постараюсь ответить.', reply_markup=menu_keyboard)
    # elif flag == 4:
    #     await call.answer(f'У вас действует подписка на 6 месяцев. '
    #                          f'Отправьте мне ваш вопрос, и я постараюсь ответить.',
    #                          reply_markup=menu_keyboard)
    # elif flag == 5:
    #     await message.answer(f'У вас действует годовая подписка. Отправьте мне ваш вопрос, и я постараюсь ответить.',
    #                          reply_markup=menu_keyboard)
    # elif remaining_tokens is not None and remaining_tokens != 0:
    #     if flag == 2:
    #         await message.answer(f'Бесплатных токенов осталось {remaining_tokens}. Оформите подписку и '
    #                              f'получите больше функционала на выгодных для Вас условиях.',
    #                              reply_markup=inline_submit_preview)
    #     else:
    #         await message.answer(f'Бесплатных токенов осталось {remaining_tokens}. Зарегистрируйтесь и '
    #                              f'оформите подписку и получите больше функционала на выгодных для Вас условиях.',
    #                              reply_markup=inline_markup_reg)
    # else:
    #     if flag > 1:
    #         await call.answer(
    #             'ВНИМАНИЕ: Бесплатные токены закончились. Оформите подписку и '
    #             'получите больше функционала на выгодных для Вас условиях.',
    #             reply_markup=inline_submit_preview)
    #     else:
    #         await call.answer(
    #             'ВНИМАНИЕ: Бесплатные токены закончились.  и оформите подписку и '
    #             'получите больше функционала на выгодных для Вас условиях.',
    #             reply_markup=inline_markup_reg)


# ======================================================================================================================
#                                            РЕГИСТРАЦИЯ
# ======================================================================================================================
async def registration(call: types.CallbackQuery):
    user_id = call.from_user.id
    flag = await get_flag(user_id)
    if flag > 1:
        await call.message.answer('Вы уже зарегистрированы.\nИнформация доступна по кнопке "📊 Профиль"',
                                  reply_markup=menu_keyboard)
    else:
        registration_date = call.message.date.strftime('%Y-%m-%d %H:%M:%S')
        flag = 2
        await reg_user(registration_date, flag, user_id)
        await call.message.answer("Регистрация успешна!", reply_markup=menu_keyboard)
        await call.message.answer("Можете оформить подписку для расширения функционала.",
                                  reply_markup=inline_submit_preview)


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


async def dally_2(call: types.CallbackQuery):
    global STATE
    STATE = 'dally2'
    await call.message.answer('Ок! Дальше я на ваши сообщения буду отвечать изображениями 👩‍🎨')


async def dally_3(call: types.CallbackQuery):
    await call.message.answer('Данный раздел находится в разработке, но скоро будет доступен...')


async def bot_dialog(call: types.CallbackQuery):
    global STATE
    STATE = ''
    await call.message.answer('Понял! Возвращаемся к обычному общению ')


async def send_image(message):
    api_key = get_unused_key()
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
        if flag > 1:
            await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.", reply_markup=menu_keyboard)
        else:
            await message.answer("Новый чат создан! Теперь вы можете начать новый диалог.")
    # ==================================================================================================================
    #                                             Любой запрос к боту
    # ==================================================================================================================
    else:
        if flag > 0 and r_tokens > 0:
            user_question = message.text
            print(f"User question: {user_question}")
            if STATE == 'dally2':
                await send_image(message)
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
