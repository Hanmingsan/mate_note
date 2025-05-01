# UPDATE note SET QQ_id = %s WHERE name = %s;
# UPDATE note SET wechat_id = %s WHERE name = %s;
import connect_to_db as cdb # 使用你定义的模块
import select_mate as sm
import psycopg2 
import sys

def update_by_name (name:str, tel, wechat_id, qq_id, personal_motto, comment_on_me, photo_url):
    data = None
    conn = None
    db_params = {}

    queried = sm.query_mate_by_name(name)
    
    if queried = None:
        print('数据库查询失败,正在退出 :( ...')
        return None

    data = {
            'id' = queried[0][0],
            'name' = queried[0][1],
            'tel' = queried[0][2],
            'wechat_id' =queried[0][3],
            'qq_id' = queried[0][4],
            'personal_motto' = [0][5],
            'comment_on_me' = [0][6],
            'photo_url' = [0][7],
            }
    

