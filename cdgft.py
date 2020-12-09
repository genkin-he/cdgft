# -*- coding: utf-8
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime, timedelta
import execjs
import traceback
import os
import time


class House:
    def __init__(self):
        self.name = ""
        self.zone = ""
        self.zone_level = 0
        self.zone_section = ""
        self.location = ""
        self.status = ""
        self.usage = ""
        self.customized_price = []
        self.presell_date = ""
        self.tags = []
        self.date_with_status = ""
        self.detail_url = ""


DING_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxx"  # 配置钉钉webhook地址
KEYWORD = "Genkin:"  # 钉钉关键词白名单
HOST = "https://www.cdgoufangtong.com/"


def get_list():
    time.sleep(10)
    r = requests.get(HOST + 'latest_opening/?page=1')
    soup = BeautifulSoup(r.text, features='html.parser')
    scripts = soup.find_all(name="script")
    for script in scripts:
        if script.string is None:
            continue
        js_str = script.string.replace("window.__NUXT__=", "")
        result = execjs.compile("function test(){return " + js_str + "}")
        resp = result.call('test')
        for item in reversed(resp["data"][0]['list']['items']):
            try:
                deal_item(item)
            except:
                traceback.print_exc()
                print(item)


def notify(house):
    """推送消息到钉钉机器人
    """
    msg = f"**【{house.zone}】【{house.name}】**\n>\n"
    msg += f">**楼盘：** {house.name}\n>\n"
    msg += f">**标签：** {'|'.join(house.tags)}\n>\n"
    msg += f">**时间：** {house.date_with_status}\n>\n"
    msg += f">**价格：** {'|'.join(house.customized_price)}\n>\n"
    msg += f">**提醒：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n>\n"
    msg += f">**详情：** [点击查看详情]({house.detail_url})\n>\n"
    content = {"title": KEYWORD + "楼盘提示", "text": msg}
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    msg_type = "markdown"
    message = {
        "msgtype": msg_type,
        msg_type: content,
        "at": {
            "atMobiles": "17086898380",
            "isAtAll": False
        }
    }
    message_json = json.dumps(message)
    # 发送请求
    info = requests.post(url=DING_WEBHOOK, data=message_json, headers=header)
    # 打印返回
    print(info.text)


def can_notify(house):
    file_events = "house.json"
    if os.path.exists(file_events):
        events = json.load(open(file_events, 'r', encoding='utf-8'))
    else:
        events = dict()
    k = " | ".join(
        [house.zone, house.name, house.status, house.date_with_status])

    if k in events.keys():
        return False
    events[k] = ""
    json.dump(events, open(file_events, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    return True


def deal_item(item):
    house = House()
    house.name = item['name']
    house.zone = item['zone']
    house.zone_level = item.get('zone_level', 0)
    house.zone_section = item.get("zone_section", "")
    house.location = item.get('location', "")
    house.status = item.get('status', "")
    house.usage = item.get('usage', "")
    house.customized_price = item.get('customized_price', [])
    house.presell_date = item.get('presell_date', "")
    for tag in item.get('tags', []):
        house.tags.append(tag['name'])
    house.date_with_status = item.get('date_with_status', "")
    house.detail_url = HOST + "building/" + str(item['building_id'])
    if can_notify(house):
        notify(house)


get_list()
