import openai
from handlers.comands import *
from data.data_base import cursor


def generate_response(prompt):
    system_message = {"role": "system", "content": "You are a helpful assistant"}
    user_message = {"role": "user", "content": prompt}

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[system_message, user_message],
        temperature=0.8,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    token_input = len(response)
    print(token_input)
    response_texts = response['choices'][0]['message']['content'].strip()
    token_output = len(response_texts)
    print(token_output)

    return response_texts


def calculate_remaining_tokens(user_id):
    # Замените "your_table_name" на фактическое имя вашей таблицы в базе данных
    cursor.execute('SELECT tokens, tokens_used FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        tokens, tokens_used = user_data
        remaining_tokens = tokens - tokens_used
        return remaining_tokens
    else:
        # Если пользователя с указанным user_id нет в базе данных
        return None
