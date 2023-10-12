from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# 建立数据库连接
engine = create_engine('mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/md?charset=utf8mb4')

# 创建对象基类
Base = declarative_base()


# 定义数据表模型类
class User(Base):
    __tablename__ = 'asongbo'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age})>"


# # 创建数据表
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
#
# # 插入数据
# user1 = User(name='Alice', age=25)
# user2 = User(name='Bob', age=30)
# session.add_all([user1, user2])
# session.commit()

# 查询数据
users = session.query(User).filter_by(age=25)
for user in users:
    print(user)

# # 更新数据
# user1.age = 26
# session.commit()
#
# # 删除数据
# session.delete(user2)
# session.commit()

# 关闭会话
session.close()
