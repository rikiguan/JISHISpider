from feishu.server import message_api_client
from datetime import datetime


def daySummaryTemplate(open_id, allPost, dayPost, img, Workerlist, APIlist,allUser):
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y年%m月%d日")
    data = {
        'time': formatted_date,
        'allPost': allPost,
        'dayPost': dayPost,
        'allUser': allUser,
        'img': message_api_client.upload_image(img),
        'Worker': [{'name': str(name), 'work': str(work)} for name, work in Workerlist.items()],
        'API': [{'name': str(name), 'num': str(num)} for name, num in APIlist.items()]
    }
    message_api_client.send_interactiveTemplate_with_open_id(open_id, 'AAqCWX5d4Jqfl', data)

def informText(open_id, msg):
    if not msg:
        msg = '空'
    message_api_client.send_text_with_open_id(open_id,msg)
