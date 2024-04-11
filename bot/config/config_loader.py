import json
import os

from dotenv import load_dotenv


def loadWechatConfig():
    # 打开并读取 JSON 文件
    try:
        with open('./env_wechat.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        try:
            with open('../../../env_wechat.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as e:
            with open('../../env_wechat.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
    return data


def getWechatConfig(keyParam):
    # 初始化返回数组，用于返回结果
    wechat_config_map = {}
    wechatData = loadWechatConfig()
    # 循环获取所有的微信配置
    for key in wechatData:
        wechat_config = wechatData[key]
        try:
            if wechat_config["enable"]:
                wechat_config_map[key] = wechat_config[keyParam]
        except KeyError:
            continue
    return wechat_config_map

App_Run_Status = True

# 微信配置变量 请求地址变量
WechatConfig_requestUrl = getWechatConfig("requestUrl")
WechatConfig_enable_auto_verify = getWechatConfig("enableAddFriend")

#todo 发音乐的XML
SEND_MUSIC_TEMPLATE = """"""
