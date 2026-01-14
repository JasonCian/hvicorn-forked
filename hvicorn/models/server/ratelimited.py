"""RateLimited 模块 - 速率限制包

包含 RateLimitedPackage 模型，表示触发速率限制的警告。
"""

from pydantic import BaseModel
from typing import Literal


class RateLimitedPackage(BaseModel):
    """速率限制包模型
    
    当操作频率过快触发服务器的速率限制时，会收到此包。
    这是 warn 命令的一个特殊子类型，通过匹配特定的警告文本识别。
    
    属性:
        cmd: 命令类型，始终为 "warn"
        type: 速率限制类型
            - CHANNEL_RL: 频道加入频率限制
            - COLOR_RL: 颜色更改频率限制
            - CHANGENICK_RL: 昵称更改频率限制
            - MESSAGE_RL: 消息发送频率限制
            - GLOBAL_RL: 全局频率限制或被封禁
        text: 警告文本内容
        
    注意:
        此模型是在 json_to_object 中通过匹配 warn 包的 text 字段
        与 RL_MAPPING 字典生成的，将文本警告转换为结构化的类型。
        
        当收到速率限制时，应该减慢对应操作的频率。
    """
    cmd: Literal["warn"]
    type: Literal["CHANNEL_RL", "COLOR_RL", "CHANGENICK_RL", "MESSAGE_RL", "GLOBAL_RL"]
    text: str
