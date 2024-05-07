import openai
# openai.api_key = "NYqa2AJTRgWEtx9XMfnJrUGuppYmzzHpREu3RyqEQ3FTHyVEF34DjyPXdfNhVfw3"
openai.api_key = "sk-sM6veXRyVDuVzRYr44Dd8c3474Db4bBe9252BaB521Af13A7"
openai.api_base = "https://oneapi.infoagent.cn/v1"
# openai.api_base = "https://ai.api.moblin.net/api/openai/v1"
# openai.api_key = "fastgpt-Qh8RjFrBjIKQLQEIzcl3gimBOZb"
# openai.api_base = "https://fastgpt.infoagent.cn/api/v1"


def chat(msg):
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                # model='gpt-4',
                messages=[
                    # {"role": "system", "content": """
                    #
                    # """}, # 催眠～
                    # {"role": "user", "content": """
                    #  请翻译成中文：
                    # """},
                    {"role": "user", "content": f'{msg}'}
                ],
                temperature=0.3,
                stream=True
            )
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        print(chunk_message.get('content', ''), end='')

# def buildPic():
#     response = openai.Image.create(
#       prompt="蓝蓝的天上白云飘，白云下面马儿跑",
#       n=1,
#       size="1024x1024" # 512x512, 256x256
#     )
#     image_url = response['data'][0]['url']
#     print(image_url)


if __name__ == '__main__':
    chat('蓝蓝的天上白云飘')

