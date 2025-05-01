import connect_to_db as cdb # 使用你定义的模块
import psycopg2           # 导入 psycopg2 以便捕获其错误
import sys                # 用于打印错误到 stderr

def query_mate_by_name (mate_name):
    """
    根据姓名查询 note 表中的记录。

    Args:
        mate_name (str): 要查询的姓名。

    Returns:
        list | None: 包含查询结果行的元组列表。
                      如果发生数据库错误则返回 None。
                      如果查询成功但未找到匹配记录，则返回空列表 []。
    """
    data = None  # 初始化为 None，表示尚未成功获取或出错
    conn = None  # 初始化 conn
    db_params = {} # 初始化 db_params

    try:
        # 1. 连接数据库并检查连接是否成功
        conn, db_params = cdb.connect_db()
        if conn is None:
            print(f"数据库连接失败，无法为 '{mate_name}' 执行查询。", file=sys.stderr)
            return None # 连接失败，直接返回 None

        # 2. 使用 'with' 管理游标
        with conn.cursor() as cur:
            # 3. 执行参数化查询
            sql = "SELECT * FROM note WHERE name = %s;"
            cur.execute(sql, (mate_name,))

            # 4. 获取所有结果 (如果担心内存，可考虑迭代或 fetchmany)
            data = cur.fetchall()
            # 此时，如果没找到匹配项，data 会是一个空列表 []

    except psycopg2.Error as e:
        # 5. 捕获数据库操作相关的错误
        print(f"为 '{mate_name}' 查询数据库时出错: {e}", file=sys.stderr)
        # 让 data 保持为 None (或者你可以选择返回空列表或其他指示错误的值)
        data = None
    except Exception as e:
        # 捕获其他意外错误
        print(f"为 '{mate_name}' 查询时发生意外错误: {e}", file=sys.stderr)
        data = None
    finally:
        # 6. 确保在 finally 块中关闭连接
        if conn: # 只有当 conn 确实被成功创建后才尝试关闭
            cdb.disconnect_db(conn, db_params)

    # 7. 返回获取到的数据 (可能为 [] 或 None)
    return data
