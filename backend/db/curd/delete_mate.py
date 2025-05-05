import os
import psycopg2
import sys
import db.curd.connect_to_db as cdb

def delete_mate_by_name (name:str):
    try:
        conn, db_params = cdb.connect_db()
        if conn is None:
            print("未连接到数据库, 不能添加数据 :(")
            return False # 直接返回 False
        with conn.cursor() as cur:
            sql = "DELETE FROM note WHERE name = %s;"
            sql_arg = (name,)
            cur.execute(sql, sql_arg)
        conn.commit()
        print(f"已经成功删除mate{name}")
        success = True
    except psycopg2.IntegrityError as e:
        print(f"插入失败：违反数据库约束 (Name='{name}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback()
            print("事务已回滚。")
        # success 保持 False
    except psycopg2.Error as e:
        print(f"插入记录时数据库出错 (Name='{name}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback()
            print("事务已回滚。")
        # success 保持 False
    except Exception as e:
        print(f"插入记录时发生意外错误 (Name='{name}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback()
            print("事务已回滚。")
        # success 保持 False
    finally:
        # --- 修正 3: 在 finally 中也检查 conn ---
        if conn:
            # 确保 db_params 是在连接成功时获取到的字典
            cdb.disconnect_db(conn, db_params if db_params else {}) # 传递 params
        else:
             print("连接未建立，无需断开。") # 可选的提示

    return success
