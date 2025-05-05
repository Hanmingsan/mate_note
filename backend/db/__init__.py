# 导入 curd 子包中的 create_mate 模块，并将其别名设为 cm
from .curd import create_mate as cm
# 导入 delete_mate 模块，别名为 dm
from .curd import delete_mate as dm
# 导入 select_mate 模块，别名为 sm
from .curd import select_mate as sm
# 导入 update_mate 模块，别名为 um
from .curd import update_mate as um

from .curd import connect_to_db as cdb
