from bot.infrastructure.wexin import WechatUtils, OtherNativeApi


class MsgProcessorNativeApi:
    """
    消息处理原生接口
    """
    pass


# 获取消息处理器列表
def get_msg_processor_list(wechat_id):
    """
    获取消息处理器列表
    :param wechat_id: 微信id
    :return: 消息处理器列表
    """
    resdata = WechatUtils._post_wx_request(wechat_id, {
        "type": 1003,
    })
    return resdata["data"]


# 判断是否已经存在这种类型处理器
def checkProcessorList(wechat_id, protocol, url=None):
    """
    判断是否已经存在这种类型处理器
    :param wechat_id: 微信id
    :param param: 处理器类型
    :return: 消息处理器列表
    """
    processor_list = get_msg_processor_list(wechat_id)
    for processor in processor_list:
        if url:
            if processor["url"] == url:
                return True
        if processor["protocol"] == protocol:
            return True
    return False


# 添加Http处理器

def add_http_processor(wechat_id, url):
    """
    添加Http处理器
    :param wechat_id: 微信id
    :param url: http地址
    :param mandatory: 是否强制添加，如果为False，则已经存在Http处理器时，不会再次添加
    :return: 是否成功
    """
    req = {
        "type": 1001,
        "protocol": 2,
        "url": url
    }
    processor_list = get_msg_processor_list(wechat_id)
    for processor in processor_list:
        if processor["pcotocol"] == req["protocol"] and "url" in processor and processor["url"] == url:
            return True
    resdata = WechatUtils._post_wx_request(wechat_id, req)
    return resdata["status"] == 0


