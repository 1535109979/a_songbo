from peewee import *

# 连接 SQLite 数据库
db = SqliteDatabase('my_database.db')
db.connect()

# with db:
#     query = db.execute_sql('SELECT * FROM users;')
#     for row in query.fetchall():
#         print(row)


class User(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    age = IntegerField()

    class Meta:
        database = db  # 指定该 Model 使用的数据库
        table_name = 'users'  # 指定数据表名称


# 创建数据表
# User.create_table()

# 向数据表中插入数据
# user = User(name='Ttm', age=26)
# user.save()


# 检索要修改的数据
# user = User.get(User.name == 'Ttm')
# 删除数据
# if user:
#     user.delete_instance()
# # 修改数据
# user.age = 30
# # 保存更改
# user.save()

# 查询所有用户
users = User.select()
for user in users:
    print(user.name, user.age)

# 根据条件查询用户
# users = User.select().where(User.age > 18)
# for user in users:
#     print(user.name, user.age)



