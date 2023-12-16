import openai

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


