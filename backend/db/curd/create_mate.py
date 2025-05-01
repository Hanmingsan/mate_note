import os
import psycopg2
import sys
import connect_to_db as cdb

def create_mate(name,
                comment,
                tel = None,
                wechat_id = None,
                qq_id = None,
                personal_motto = None,
                photo_url = None
                ):
    try:
        conn, db_params = cdb.connect_db()
        if conn is None:
            print("未连接到数据库,不能添加数据 :(")
            return(False)

        with conn.cursor() as cur:
            sql = "INSERT INTO note (name, tel, wechat_id, qq_id, personal_motto, comment_on_me, photo_url) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            data = (name, tel, wechat_id, qq_id, personal_motto, comment, photo_url)
            cur.execute(sql,data)
        conn.commit()
        return True
    except psycopg2.IntegrityError as e:
        # 捕获违反约束（如 UNIQUE 或 NOT NULL）的错误
        print(f"插入失败：违反数据库约束 (Name='{name}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback() # 出错时回滚事务
            print("事务已回滚。")
        return False
    except psycopg2.Error as e:
        # 捕获其他数据库相关的错误
        print(f"插入记录时数据库出错 (Name='{name}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback()
            print("事务已回滚。")
        return False
    except Exception as e:
        # 捕获意料之外的 Python 错误
        print(f"插入记录时发生意外错误 (Name='{name}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback() # 如果连接存在也尝试回滚
            print("事务已回滚。")
        return False
    finally:
        if conn:
            cdb.disconnect_db(conn, db_params)

