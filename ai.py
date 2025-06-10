import openai

def ask_chatgpt(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # или "gpt-4o-mini", если у вас есть доступ
        messages=messages
    )
    return response["choices"][0]["message"]["content"]