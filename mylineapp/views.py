from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, StickerSendMessage, ImageSendMessage


import datetime

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def index(request):
    return HttpResponse("Hello Line Bot works~!")

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            # 若有訊息事件
            if isinstance(event, MessageEvent):

                tdnow = datetime.datetime.now()
                msg = tdnow.strftime("%Y/%m/%d, %H:%M:%S") + '\n' + event.message.text
                imgurl = "https://pgw.udn.com.tw/gw/photo.php?u=https://uc.udn.com.tw/photo/2024/03/08/1/29147449.jpg&x=0&y=0&sw=0&sh=0&sl=W&fw=800&exp=3600&w=930&nt=1"

                # 回傳收到的文字訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    [ TextSendMessage(text=msg),
                      StickerSendMessage(package_id=789, sticker_id=10856),
                      ImageSendMessage(original_content_url=imgurl,
                            preview_image_url=imgurl)
                    ]
                    )

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
