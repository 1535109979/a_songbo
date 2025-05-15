import pandas as pd
import sqlalchemy
from sqlalchemy import text,inspect


engine = sqlalchemy.create_engine('clickhouse://clickhouse:CK-clickhouse@49.235.94.80:8123/md')

df = pd.read_sql(text(sql), engine.connect())

from clickhouse_driver import Client

# ClickHouse 连接信息（使用 URL）
CLICKHOUSE_URL = "localhost"
CLICKHOUSE_PORT = 9000  # 默认端口
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = ""
CLICKHOUSE_DATABASE = "default"

# 连接 ClickHouse
client = Client(
    host=CLICKHOUSE_URL,
    port=CLICKHOUSE_PORT,
    user=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database=CLICKHOUSE_DATABASE
)

# 1️⃣ 创建表（如果不存在）
def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS test_table (
        id UInt32,
        name String,
        age UInt8
    ) ENGINE = MergeTree()
    ORDER BY id;
    """
    client.execute(query)
    print("✅ 表创建成功（如果不存在）")

# 2️⃣ 插入数据
def insert_data():
    data = [
        (1, 'Alice', 25),
        (2, 'Bob', 30),
        (3, 'Charlie', 22)
    ]
    query = "INSERT INTO test_table (id, name, age) VALUES"
    client.execute(query, data)
    print("✅ 数据插入成功")

# 3️⃣ 查询数据
def fetch_data():
    query = "SELECT * FROM test_table"
    result = client.execute(query)
    print("✅ 查询结果：")
    for row in result:
        print(row)

if __name__ == "__main__":
    create_table()
    insert_data()
    fetch_data()