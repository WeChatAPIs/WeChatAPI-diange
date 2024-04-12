import json
import os

from dotenv import load_dotenv

MUSIC_BASE_PATH = os.environ.get('MUSIC_BASE_PATH')
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

SEND_MUSIC_TEMPLATE = """
<appmsg appid=\"wx8dd6ecd81906fd84\" sdkver=\"0\">\n\t\t
    <title>{songName}</title>\n\t\t
    <des>{artName}</des>\n\t\t
    <type>3</type>\n\t\t
    <url>{url}</url>\n\t\t
    <lowurl>{url}</lowurl>\n\t\t
    <dataurl>{mp3url}</dataurl>\n\t\t
    <lowdataurl>{mp3url}</lowdataurl>\n\t\t
    <songalbumurl>{img}</songalbumurl>\n\t\t
    <songlyric>[00:00:00]惊喜</songlyric>\n\t\t
    <appattach>\n\t\t\t
        <cdnthumbaeskey />\n\t\t\t
        <aeskey />\n\t\t
    </appattach>\n\t
</appmsg>
"""
