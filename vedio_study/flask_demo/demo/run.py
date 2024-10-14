from flask import Flask, render_template, abort
import os

app = Flask(__name__)


@app.route('/<filename>')
def show_template(filename):
    template_dir = os.path.join(app.root_path, 'templates')
    for template_file in os.listdir(template_dir):
        if filename == template_file.split('.')[0] and template_file.endswith('.html'):
            return render_template(template_file)
    abort(404)  # 如果没有找到对应的模板文件，返回404错误


@app.route('/')
def home():
    # 获取 templates 目录下的所有文件
    template_files = [f for f in os.listdir('templates') if f.endswith('.html')]
    # 创建链接列表
    links = [{'filename': f, 'link': f'/{f[:-5]}'} for f in template_files]  # 假设URL与文件名相同，只是没有.html扩展名
    return render_template('index.html', links=links)


if __name__ == '__main__':
    app.run(port=4000, debug=True)
