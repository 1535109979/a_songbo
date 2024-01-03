from peewee import *

db = SqliteDatabase('./future_min_data.db')
db.connect()


class FutureMiData(Model):
    id = AutoField(primary_key=True)
    symbol = CharField()
    datetime = CharField()

    start_volume = FloatField()
    volume = FloatField()
    start_turnover = FloatField()
    turnover = FloatField()
    open_interest = FloatField()

    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()

    class Meta:
        database = db
        table_name = 'future_min_data'  # 指定数据表名称


if __name__ == '__main__':
    FutureMiData.create_table()
