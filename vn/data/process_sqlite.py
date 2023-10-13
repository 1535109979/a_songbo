import os

from peewee import *


class SqliteDatabaseManage:
    def __init__(self):
        self.root_fp = os.path.join(os.path.expanduser('~'))
        self.data_fp = self.root_fp + '/byt_pub/a_songbo/vn/data/'

    def get_connect(self, db_name=''):
        db_fp = self.data_fp + 'options_data.db'
        db = SqliteDatabase(db_fp)
        db.connect()
        return db


class Options(Model):
    id = AutoField(primary_key=True)
    instrument = CharField()
    imp = FloatField()
    timestamp = FloatField()

    class Meta:
        database = SqliteDatabaseManage().get_connect()
        table_name = 'options_imp'  # 指定数据表名称


class Minprice(Model):
    id = AutoField(primary_key=True)
    instrument = CharField()
    price = FloatField()
    timestamp = FloatField()

    class Meta:
        database = SqliteDatabaseManage().get_connect()
        table_name = 'min_price'  # 指定数据表名称


class HistoryPrice(Model):
    id = AutoField(primary_key=True)
    instrument = CharField()
    price = FloatField()
    timestamp = FloatField()

    class Meta:
        database = SqliteDatabaseManage().get_connect()
        table_name = 'history_price'  # 指定数据表名称


def save_min_price():
    data = {
        'rb2310': {'price': 1233, 'timestamp': 123453423},
        'rb2311': {'price': 1244, 'timestamp': 123123453423},
            }

    save_list = []
    for instrument, value in data.items():
        save_list.append({
            'instrument': instrument,
            'price': value['price'],
            'timestamp': value['timestamp'],
        })
    with SqliteDatabaseManage().get_connect().atomic():
        Minprice.insert_many(save_list).execute()


def drop_table():
    with Minprice._meta.database:
        if Minprice.table_exists():
            Minprice.drop_table()


def select_last_data():
    from peewee import fn

    query = Minprice.select(Minprice.instrument, Minprice.price,
                           fn.MAX(Minprice.timestamp).alias('max_timestamp')).group_by(
        Minprice.instrument)
    saved_min_price = {row.instrument: {'price': row.price, 'timestamp': row.max_timestamp} for row in query}
    print(saved_min_price)


if __name__ == '__main__':
    # HistoryPrice.create_table()
    # quit()
    # drop_table()
    # quit()

    # save_min_price()
    # quit()

    # select_last_data()
    # quit()

    # HistoryPrice.delete().execute()
    # quit()

    # users = Options.select()
    # for user in users:
    #     print(user.instrument, user.imp, user.timestamp)

    users = Minprice.select()
    for user in users:
        # print(user)
        print(user.instrument, user.price, user.timestamp,)
        # if user.instrument == 'ru2311C13250':
        #     user.delete_instance()
        #     user.save()



