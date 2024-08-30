from feishu.server import message_api_client
from datetime import datetime


def daySummaryTemplate(open_id, allPost, dayPost, img, Workerlist, APIlist):
    message_api_client._authorize_tenant_access_token()
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y年%m月%d日")
    data = {
        'time': formatted_date,
        'allPost': allPost,
        'dayPost': dayPost,
        'img': message_api_client.upload_image(img),
        'Worker': [{'name': str(name), 'work': str(work)} for name, work in Workerlist.items()],
        'API': [{'name': str(name), 'num': str(num)} for name, num in APIlist.items()]
    }
    message_api_client.send_interactiveTemplate_with_open_id(open_id, 'AAqCRc3c33RB6', data)
