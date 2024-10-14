from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from peewee import SqliteDatabase, Model, AutoField, FloatField, DateTimeField

app = Flask(__name__)

# 定义数据库连接
db = SqliteDatabase('/Users/edy/byt_pub/song_binance_client/database/bian_f_data.db')


class AccountValue(Model):
    id = AutoField(primary_key=True)
    balance = FloatField()
    update_time = DateTimeField()

    class Meta:
        database = db
        table_name = 'account_value'


@app.route('/')
def index():
    users = AccountValue.select()
    return render_template('index.html', users=users)


@app.route('/add', methods=['POST'])
def add_user():
    balance = request.form['balance']
    AccountValue(
        balance=balance,
        update_time=datetime.now(),
    ).save()

    return redirect(url_for('index'))


@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    AccountValue.delete().where(AccountValue.id == user_id).execute()
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_user():
    id = request.form['db_id']
    balance = request.form['balance']

    account = AccountValue.get(AccountValue.id == id)
    account.balance = balance
    account.save()

    return redirect(url_for('index'))


if __name__ == '__main__':
    # AccountValue.create_table()

    db.connect()
    app.run(debug=True)
