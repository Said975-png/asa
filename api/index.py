import json
from tgbot.main import tgbot

async def handler(request):
    update = json.loads(request.body.decode('utf-8'))
    await tgbot.update_bot(update)
    return {'statusCode': 200, 'body': 'ok'}
