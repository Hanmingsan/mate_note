import db.curd.connect_to_db as cdb
import psycopg2
import sys

def update_mate_by_name(name_to_update: str, update_fields: dict):
    """
    使用 SQL UPDATE 语句和字典更新 note 表中指定 name 的记录。

    Args:
        name_to_update (str): 要更新记录的 name (用于 WHERE 子句)。
        update_fields (dict): 一个字典，键是数据库表的列名 (str)，值是对应列的新数据。
                              例如: {'tel': '111222333', 'comment_on_me': 'New comment'}
                              只有字典中提供的键值对会被用于更新。

    Returns:
        bool: True 如果更新成功并提交 (影响至少一行),
              False 如果发生错误、未找到记录或没有提供有效更新字段。
    """
    conn = None
    db_params = {}
    success = False

    # --- 定义允许通过此函数更新的列名 ---
    # --- !!! 非常重要：排除主键、用于 WHERE 的列 (name) 以及不想允许更新的任何其他列 !!! ---
    # --- 你应该根据你的实际表结构和业务逻辑调整这个集合 ---
    allowed_columns_to_update = {
        "tel", "wechat_id", "qq_id", "personal_motto", "comment_on_me", "photo_url"
    }

    # --- 根据传入的字典动态构建 SET 子句和参数列表 ---
    set_clauses = []  # 存放 "column_name = %s" 部分
    parameters = []   # 存放对应的值

    for column, value in update_fields.items():
        if column in allowed_columns_to_update:
            set_clauses.append(f"{column} = %s") # 安全地构建 "col = %s"
            parameters.append(value) # 添加值到参数列表
        else:
            # 忽略不允许更新的列名或无效的列名，并给出警告
            print(f"警告：跳过不允许更新或无效的列 '{column}'。", file=sys.stderr)

    # 如果过滤后没有有效的字段需要更新 (例如，传入空字典或只包含无效列名)
    if not set_clauses:
        print(f"没有提供有效的更新字段用于 name='{name_to_update}'。")
        return False # 没有执行更新，返回 False

    # 将用于 WHERE 子句的 name_to_update 添加到参数列表的末尾
    parameters.append(name_to_update)

    # 构建完整的 SQL UPDATE 语句
    # 使用 ', '.join() 将 set_clauses 列表中的字符串用逗号加空格连接起来
    sql_update = f"UPDATE note SET {', '.join(set_clauses)} WHERE name = %s;"
    # 示例生成的 SQL 可能像: "UPDATE note SET tel = %s, comment_on_me = %s WHERE name = %s;"

    # (可选) 打印将要执行的 SQL 和参数，用于调试
    # print(f"Executing SQL: {sql_update}")
    # print(f"With parameters: {parameters}")

    try:
        conn, db_params = cdb.connect_db()
        if conn is None:
            return False # 连接失败

        with conn.cursor() as cur:
            cur.execute(sql_update, parameters) # 执行 UPDATE
            rowcount = cur.rowcount # 获取受影响的行数

            if rowcount == 0:
                # 未找到匹配记录，或者提供的值与数据库中的原始值相同
                print(f"更新操作未影响任何行。可能未找到 name 为 '{name_to_update}' 的记录，或者提供的值与原值相同。")
                success = False # 标记为失败，因为没有实际更新发生
            else:
                print(f"成功更新了 {rowcount} 条 name 为 '{name_to_update}' 的记录。")
                conn.commit() # 提交事务
                success = True

    except psycopg2.Error as e:
        print(f"数据库更新操作失败 (Name='{name_to_update}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback() # 回滚事务
        success = False # 确保返回 False
    except Exception as e:
        print(f"更新时发生意外错误 (Name='{name_to_update}'): {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        success = False # 确保返回 False
    finally:
        if conn:
            cdb.disconnect_db(conn, db_params) # 关闭连接

    return success



