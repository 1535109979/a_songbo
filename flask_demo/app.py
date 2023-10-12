from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        response_text = get_response(input_text)
        return '''
            <p><b>你说：</b>{}</p>
            <p><b>我回答：</b>{}</p>
            <form method="post">
                <input type="text" name="input_text">
                <button type="submit">再聊一次</button>
            </form>
        '''.format(input_text, response_text)
    else:
        return '''
            <form method="post">
                <input type="text" name="input_text">
                <button type="submit">开始聊天</button>
            </form>
        '''


def get_response(text):
    # 这里可以使用任何对话机器人的 API 或自己编写的算法来生成回答
    # 下面是一个简单的示例
    if text == '你好':
        return '你好呀！'
    elif text.endswith('吗？'):
        return text[:-2] + '！'
    else:
        return '我不知道该怎么回答。'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)











