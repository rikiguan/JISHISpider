import logging
import logging.handlers

logger = logging.getLogger(__name__)

formatter = logging.Formatter('[%(asctime)s][%(funcName)s][%(threadName)s] - %(levelname)s - %(message)s')
# 创建日志记录器
logger.setLevel(logging.DEBUG)  # 设置日志级别
# 创建控制台处理器并设置日志格式
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
# 创建文件处理器并设置日志格式
file_handler = logging.handlers.TimedRotatingFileHandler('log/app.log', when='midnight', interval=1, backupCount=7, encoding='utf-8')
file_handler.setFormatter(formatter)
# 添加处理器到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

#---------------- dismissed ---------------------
def printlog(tag,info):
    print(f'[{tag}]:{info}')

def genTextColor(color,text):
    if color =='g':
        return '\033[32m'+text+'\033[30m'
    elif color =='r':
        return '\033[31m'+text+'\033[30m'



