from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage


import datetime
import random

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

import requests
from bs4 import BeautifulSoup

def cambridge(word):
    url = 'https://dictionary.cambridge.org/dictionary/english-chinese-traditional/'+word
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers = {'User-Agent': user_agent}
    web_request = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_request.text, "html.parser")
    entries = soup.find_all("div", class_="entry-body__el")
    rr = ""
    for entry in entries:
        rr += entry.find('div',class_="posgram").text + '\n'
        i=1
        ddefs = entry.find_all("div", class_="def-body")
        i=1
        for ddef in ddefs:
            tran = ddef.find('span')
            rr += str(i) +'.'+tran.text+"\n"
            i+=1
    rr += "\n出處:" + url
    return rr


def getInvoice():
    url = "https://invoice.etax.nat.gov.tw"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers = {'User-Agent': user_agent}
    html = requests.get(url, headers=headers)
    # html = requests.get(url)
    html.encoding ='uft-8'
    soup = BeautifulSoup(html.text, 'html.parser')

    period = soup.find("a", class_="etw-on")
    rr = period.text+"\n"

    nums = soup.find_all("p", class_="etw-tbiggest")
    rr += "特別獎：" + nums[0].text + "\n"
    rr += "特獎：" + nums[1].text + "\n"
    rr += "頭獎：" + nums[2].text.strip() +" "+ nums[3].text.strip() +" "+ nums[4].text.strip()

    return rr

# def getCamDict(word):
#     """"擷取"""
#     url = "https://dictionary.cambridge.org/dictionary/english-chinese-traditional/" + word
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0'}
#     html = requests.get(url, headers=headers)
#     soup = BeautifulSoup(html.text, 'html.parser')
#     
#     nn = soup.find_all('div',class_='pos-body')
#     rr = ""
#     for n in nn:
#         rr += n.find('div',class_='def-body').find('span').text + '\n'
#     return rr

def getOilPrice():
    """擷取今日油價"""
    url = "https://www.npcgas.com.tw/home/Oil_today"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    html = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(html.text, 'html.parser')
    soup.encoding = 'utf-8'
    
    nn = soup.find_all('div',class_='oil-box')
    
    mm  = '九二無鉛:' + nn[0].find('span',class_='f-bold').text + '元\n'
    mm += '九五無鉛:' + nn[1].find('span',class_='f-bold').text + '元\n'
    mm += '九八無鉛:' + nn[2].find('span',class_='f-bold').text + '元\n'
    mm += '超級柴油:' + nn[3].find('span',class_='f-bold').text + '元\n'

    return mm 

def getNews(num=10):
    """"擷取中央社新聞"""
    url = "https://www.cna.com.tw/list/aall.aspx"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    html = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(html.text, 'html.parser')
    soup.encoding = 'utf-8'
    
    allnews = soup.find(id="jsMainList")
    nn = allnews.find_all('li')
    
    mm = ""
    for n in nn[:num]:
        mm += n.find('div',class_='date').text +' '
        mm += n.find('h2').text +'\n'
        mm += 'https://www.cna.com.tw/' + n.find('a').get('href') +'\n'
        mm += '-'*30+'\n'
    return mm


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

                msg = event.message.text

                if msg=='hello' or msg=='hi':
                    # 回傳貼圖
                    line_bot_api.reply_message(
                        event.reply_token,
                        StickerSendMessage(package_id=789, sticker_id=10856)
                    )

                elif msg.startswith('/'):
                    
                    sms = cambridge( msg[1:] )
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=sms)
                    )
                    
                elif msg== 'guess':
                    num = random.randint(1,10)
                    msg = f"{num}"
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )

                elif msg=='最新消息' or msg=='今日新聞':
                    sms = getNews(6)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=sms)
                    )

                elif msg=='油價' or msg=='今日油價':
                    sms = getOilPrice()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=sms)
                    )

                elif msg=='求籤' or msg=='抽籤':
                    num = random.randint(1,100)
                    img = f"https://www.lungshan.org.tw/fortune_sticks/images/{num:03d}.jpg"

                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(original_content_url=img,
                        preview_image_url=img)
                    )

                elif msg=='今天誰最帥':
                    names = ['陳柏宇','林冠宇','蔡永詮','黃聖明','吳建樺','雷廷宇','劉承杰','方俊翰','謝政勳']
                    msg = '今天最帥的是:'+random.choice(names)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )

                elif msg=='今天誰最美':
                    names = ['王佩蓉','陳玟卉','施芷庭','吳佳錦','洪芝蓉','黃婕茹']
                    msg = '今天最美的是:'+random.choice(names)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )

                elif msg.startswith('今天誰'):
                    names = ['陳柏宇','林冠宇','蔡永詮','黃聖明','吳建樺','雷廷宇','劉承杰','方俊翰','謝政勳','王佩蓉','陳玟卉','施芷庭','吳佳錦','洪芝蓉','黃婕茹']
                    msg = msg.replace('誰','')+'的是:'+random.choice(names)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )
                    
                elif msg=='統一發票':
                    msg = getInvoice()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )

                elif msg=='who are you':
                    msg = 'I am your good friend~!'
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )

                else:
                    tdnow = datetime.datetime.now()
                    msg = tdnow.strftime("%Y/%m/%d, %H:%M:%S") + '\n' + event.message.text
                    # 回傳收到的文字訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=msg)
                    )


                # imgurl = "https://i.imgur.com/TthOEGC.jpg"

                

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
