import importlib
import os
from utils.logger import logger
# 获取当前目录路径
current_dir = os.path.dirname(__file__)

# 遍历当前目录下的所有.py文件
for filename in os.listdir(current_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        # 去掉 .py 后缀得到模块名
        module_name = filename[:-3]
        # 动态导入模块
        logger.info(f'导入模块.{module_name}')
        importlib.import_module(f".{module_name}", package=__name__)
