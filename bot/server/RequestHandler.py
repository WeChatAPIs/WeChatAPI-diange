import asyncio
import logging
import random
import threading
import time

from bot.config import config_loader
from bot.config.config_loader import WechatConfig_requestUrl
from bot.data import DbWaitVerifyFriend
from bot.infrastructure.wexin import WechatUtils, MsgProcessorNativeApi, ContactNativeApi, SendMsgNativeApi
from bot.service.WechatCallbackMsgService import WechatCallbackMsgService

log = logging.getLogger(__name__)


class RequestHandler:
    def __init__(self):
        self.wechatService = WechatCallbackMsgService()
        # 开启一个线程，异步通过好友验证加好友
        thread_verify_friend = threading.Thread(target=self.handle_verify_friend)
        thread_verify_friend.start()

    def handle_weixin_callback(self, user_input):
        self.wechatService.handle_wechat_message(user_input)

    def poll_weixin_api(self, wechat_pull_url):
        # 循环调用微信API,获取消息
        while config_loader.App_Run_Status:
            try:
                response_data = WechatUtils.pull_message(wechat_pull_url)
                if response_data is not None:
                    # self.wechatService.handle_wechat_message(response_data)
                    asyncio.run(self.wechatService.handle_wechat_message(response_data))
            except Exception as e:
                log.error(f"Exception during API call: {e}")
            time.sleep(5)

    def init_weixin_callbackUrl(self, httpUrl):
        # 给所有微信设置回调地址
        for wxid in WechatConfig_requestUrl:
            MsgProcessorNativeApi.add_http_processor(wxid, httpUrl)

    def handle_verify_friend(self):
        autoWechat = []
        for key in config_loader.WechatConfig_enable_auto_verify:
            if config_loader.WechatConfig_enable_auto_verify[key]:
                autoWechat.append(key)
        while config_loader.App_Run_Status:
            # 休眠一会儿，避免频繁通过好友，这里只是示例噢，因为我的流量不大不需要过于复杂的算法处理以躲避被风控
            time.sleep(random.randint(10, 15))
            # 查询需要通过好友验证的列表
            data = DbWaitVerifyFriend.select_wait_verify_friend(autoWechat)
            # log.info("handle verify friend,size:" + str(len(data)))
            for item in data:
                id, wechatId, encryptUserName, ticket = item[0], item[1], item[2], item[3]
                # 通过好友验证
                ContactNativeApi.accept_friend(wechatId, encryptUserName, ticket)
                # 从好友列表中删除这一条待通过数据
                DbWaitVerifyFriend.delete_wait_verify_friend(id)
                log.info(f"accept friend {wechatId} {id}")
            for replaceItem in data:
                wechatId, content, wxid = replaceItem[1], replaceItem[4], replaceItem[5]
                # 这里通过好友后可以发送一段欢迎语，例如：你好，加我有什么事！
                # 当然你可以通过配置的方式来设置这段欢迎语，然后替换掉这里的文本内容，这里我就先固定了
                SendMsgNativeApi.send_text_message_base(wechatId, wxid,
                                                        "你好，加我有什么事？\n需要我为你做什么？\n\n报酬是多少？")
