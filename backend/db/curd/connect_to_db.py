import os
import psycopg2
import sys
from dotenv import load_dotenv

def connect_db():
    """尝试连接数据库并返回连接对象和连接参数。"""
    load_dotenv()
    db_params = {
        'dbname': os.environ.get('DB_NAME', 'my_app_db'),
        'user': os.environ.get('DB_USER', 'my_app_user'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432')
    }

    if not db_params['password']:
        print("错误：环境变量 DB_PASSWORD 未设置。", file=sys.stderr)
        return None, None # 返回 None 表示失败

    conn = None
    try:
        conn = psycopg2.connect(**db_params)
        print(f"成功连接到数据库 '{db_params['dbname']}' 在 {db_params['host']}:{db_params['port']}")
        # 你可以选择在这里做一些初始检查，比如 SELECT version()
        # 但主要目的是返回连接对象
        return conn, db_params # <--- 返回连接对象和参数字典

    except psycopg2.Error as e:
        print(f"数据库连接失败: {e}", file=sys.stderr)
        return None, None # 连接失败也返回 None
    except Exception as e:
        print(f"连接时发生意外错误: {e}", file=sys.stderr)
        return None, None

# 使用我们之前改进的 disconnect_db 版本
def disconnect_db(conn, db_params):
    """安全地关闭提供的 PostgreSQL 连接对象。"""

    if db_params is None:
        db_params = {}

    # 从字典中获取参数，如果键不存在则使用默认值 "N/A"
    db_name = db_params.get('dbname', 'N/A')
    db_host = db_params.get('host', 'N/A')
    db_port = db_params.get('port', 'N/A')

    if conn is None:
        print("无需断开连接：提供的连接对象是 None。")
        return
    if not hasattr(conn, 'closed'):
         print("错误：提供的对象似乎不是有效的 psycopg2 连接对象。")
         return
    try:
        if conn.closed == 0:
            conn.close()
            print(f"数据库连接已关闭 (来自 '{db_name}' 在 {db_host}:{db_port})。")
        else:
            print(f"无需断开连接：连接已经关闭 (来自 '{db_name}' 在 {db_host}:{db_port})。")
    except psycopg2.Error as e:
        print(f"关闭数据库连接时出错: {e}", file=sys.stderr)
    except Exception as e:
        print(f"断开连接时发生意外错误: {e}", file=sys.stderr)
