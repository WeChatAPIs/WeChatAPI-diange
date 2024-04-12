import logging
import re

import requests

from bot.config.config_loader import SEND_MUSIC_TEMPLATE, MUSIC_BASE_PATH
from bot.infrastructure.chatgpt.OpenAIHelper import OpenAIHelper
from bot.infrastructure.wexin import SendMsgNativeApi

log = logging.getLogger(__name__)


class WechatMsgHandle:

    def __init__(self):
        self.chatgpt_client = OpenAIHelper()
        pass

    def handle_user_message(self, wechatId, msgId, fromWechatId, msgContent, msgXml, response_content_body):
        """
        接收到私聊消息
        :return:
        """
        # 如果开启聊天功能
        self.getMusicResponse(wechatId, fromWechatId, msgContent)
        return

    def handle_group_message(self, wechatId, msgId, fromWechatId, msgContent, msgXml, response_content_body):
        """
            接收到群消息
        """
        # 如果reversed1中atuserlist标签中包含自己的id，说明是@自己的消息
        send_content = msgContent.split(":\n")
        group_mes_send_user, msgContent = send_content[0], send_content[1]
        msgContent = re.sub(r'@[^\u2005]+', '', msgContent).strip()
        msgContent = re.sub(r'@[^\u2005]+ ', '', msgContent).strip()

        # 被@了
        if wechatId in msgXml:
            # 调用chatgpt回复
            self.getMusicResponse(wechatId, group_mes_send_user, msgContent, fromWechatId)

    def handle_group_image_message(self, wechatId, msgId, fromWechatId, msgContent, msgXml,
                                   response_content_body):
        """
        接收到群里的图片消息
        """
        send_content = msgContent.split(":\n")
        group_mes_send_user, msgContent = send_content[0], send_content[1]
        msgContent = re.sub(r'@[^\u2005]+ ', '', msgContent).strip()

    pass

    def getMusicResponse(self, wechatId, userId, msgContent, groupId=None):
        chatId = userId if not groupId else groupId + userId
        # 这里演示，就写死prompt了，大家别学我，变量要写到配置中，养成良好的编程习惯
        initPrompt = """帮我分析出以下几点：
1、是否有听歌的意向
2、给我一个符合语境的歌名

#输出案例#
{是/否}
{歌名}

#案例#
-输入：
听一首安静的歌吧
-输出：
是
漂洋过海来看你

- 输入：
有事没事听忐忑
-输出：
是
忐忑

-输入：
下班了，不知道该干嘛
-输出：
否
无
"""
        aiAnswer = self.chatgpt_client.get_chat_response(chat_id=chatId, query=msgContent,
                                                         prompt=initPrompt)
        # 从aiAnswer中解析出是否想听歌、歌名
        wantAndSong = aiAnswer.split("\n")
        if wantAndSong[0] == "否":
            # 不想听歌
            return

        # 想听歌
        songName = wantAndSong[1]
        songjson = requests.get(MUSIC_BASE_PATH + "/cloudsearch?limit=1&type=1&keywords=" + songName).json()
        songId = songjson["result"]["songs"][0]["id"]
        picUrl = songjson["result"]["songs"][0]["al"]['picUrl']
        artName = songjson["result"]["songs"][0]["ar"]['name']
        songjson = requests.get(MUSIC_BASE_PATH + "/song/url/v1?id=" + songId + "&level=exhigh").json()
        mp3Url = songjson["data"][0]['url']
        XML = SEND_MUSIC_TEMPLATE.replace("{url}", picUrl) \
            .replace("{mp3url}", mp3Url) \
            .replace("{img}", picUrl) \
            .replace("{songName}", songName) \
            .replace("{artName}", artName)

        SendMsgNativeApi.send_xml_message(wechatId, groupId if groupId else userId, XML)
        return

    def handle_channel_message(self, wechatId, msgId, fromWechatId, msgContent, msgXml, response_content_body,
                               xml_dict):
        """
            接收到视频号消息
        """
        groupId = None
        chatType = "deWaterMark"
        if "@chatroom" in fromWechatId:
            # 如果是群，则校验群是否配置了视频号无水印，如果配置了无水印则下载并回复
            groupId = fromWechatId
        # 不是群、或者配置了去水印，则下载视频并回复
        objectId = xml_dict["msg"]["appmsg"]["finderFeed"]["objectId"]
        objectNonceId = xml_dict["msg"]["appmsg"]["finderFeed"]["objectNonceId"]
        senderUserName = xml_dict["msg"]["fromusername"]

        finderUserName = xml_dict["msg"]["appmsg"]["finderFeed"]["username"]
        finderNickName = xml_dict["msg"]["appmsg"]["finderFeed"]["nickname"]
        finderDescription = xml_dict["msg"]["appmsg"]["finderFeed"]["desc"]
        pass
