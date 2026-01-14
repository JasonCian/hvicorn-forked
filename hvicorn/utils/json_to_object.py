"""JSON 到对象转换工具

这个模块负责将从 hack.chat 服务器接收到的原始 JSON 数据
转换为强类型的 Pydantic 模型对象。

特别处理：
- info 命令的多种形式（改名、锁房、私聊、邀请等）
- 速率限制警告消息的识别
- 昵称验证
"""

from hvicorn.models.server import (
    ChatPackage,
    EmotePackage,
    InfoPackage,
    InvitePackage,
    OnlineAddPackage,
    OnlineRemovePackage,
    OnlineSetPackage,
    UpdateUserPackage,
    WarnPackage,
    WhisperPackage,
    UpdateMessagePackage,
    ChangeNickPackage,
    CaptchaPackage,
    LockroomPackage,
    WhisperSentPackage,
    UncatchedPackage,
    RateLimitedPackage,
)
from typing import Union, Dict, Literal
import string


def verifyNick(nick: str) -> bool:
    """验证昵称是否符合 hack.chat 的命名规则
    
    hack.chat 的昵称必须符合以下规则：
    1. 长度不超过 24 个字符
    2. 仅包含字母、数字和下划线（不允许空格、特殊字符等）
    
    Args:
        nick (str): 要验证的昵称
        
    Returns:
        bool: 昵称合法返回 True，否则返回 False
        
    示例:
        >>> verifyNick("Alice_123")
        True
        >>> verifyNick("Bob Smith")  # 包含空格
        False
        >>> verifyNick("a" * 25)  # 超过 24 个字符
        False
    """
    if len(nick) > 24:
        return False
    for char in nick:
        if char not in string.ascii_letters + string.digits + "_":
            return False
    return True


# 速率限制警告消息到类型的映射
# 用于将服务器返回的文本警告转换为结构化的类型标识
RL_MAPPING: Dict[
    str, Literal["CHANNEL_RL", "COLOR_RL", "CHANGENICK_RL", "MESSAGE_RL", "GLOBAL_RL"]
] = {
    "You are joining channels too fast. Wait a moment and try again.": "CHANNEL_RL",  # 频道加入频率限制
    "You are changing colors too fast. Wait a moment before trying again.": "COLOR_RL",  # 颜色更改频率限制
    "You are changing nicknames too fast. Wait a moment before trying again.": "CHANGENICK_RL",  # 昵称更改频率限制
    "You are sending too much text. Wait a moment and try again.\nPress the up arrow key to restore your last message.": "MESSAGE_RL",  # 消息发送频率限制
    "You are rate-limited or blocked.": "GLOBAL_RL",  # 全局频率限制或被封禁
}


def json_to_object(
    data: dict,
) -> Union[
    ChatPackage,
    EmotePackage,
    InfoPackage,
    InvitePackage,
    OnlineAddPackage,
    OnlineRemovePackage,
    OnlineSetPackage,
    UpdateUserPackage,
    WarnPackage,
    WhisperPackage,
    UpdateMessagePackage,
    ChangeNickPackage,
    CaptchaPackage,
    LockroomPackage,
    WhisperSentPackage,
    UncatchedPackage,
    RateLimitedPackage,
]:
    """将 JSON 数据转换为对应的 Pydantic 模型对象
    
    这是 hvicorn 框架的核心解析函数，负责将 hack.chat 服务器返回的
    原始 JSON 数据转换为强类型的 Python 对象。
    
    特别处理：
    1. **info 命令的多种形式**：
       - 改名事件：通过解析 "OldNick is now NewNick" 文本识别
       - 房间锁定：特定的警告文本
       - 私聊消息：type="whisper" 分为发出和接收
       - 邀请消息：type="invite"
    2. **速率限制警告**：从 warn 命令中识别特定的限制类型
    3. **数据转换**：如 emote 需要从 text 中提取 content
    
    Args:
        data (dict): 从 WebSocket 接收到的原始 JSON 数据
        
    Returns:
        Union[...]: 对应类型的 Pydantic 模型对象
        
    Raises:
        ValueError: 如果 JSON 数据中没有 `cmd` 字段
        
    注意:
        - 未识别的命令会返回 UncatchedPackage 对象，包含原始 JSON
        - 此函数会修改传入的 data 字典（添加或删除字段）
    """
    if not data.get("cmd"):
        raise ValueError("No `cmd` provided")
    
    command = data.get("cmd")
    
    # 处理聊天消息
    if command == "chat":
        return ChatPackage(**data)
    
    # 处理动作消息：从 text 中提取 content
    elif command == "emote":
        data["content"] = data["text"].split(" ", 1)[1]
        return EmotePackage(**data)
    # 处理 info 命令（最复杂，有多种子类型）
    elif command == "info":
        if not data.get("type"):
            # 没有 type 字段：可能是改名或房间锁定
            # 尝试识别改名事件："OldNick is now NewNick"
            if (
                data.get("text", "").count(" ") == 3  # 正好 4 个单词
                and data.get("text", "").split(" ", 1)[1].startswith("is now")  # 包含 "is now"
                and verifyNick(data.get("text", "").split()[0])  # 旧昵称合法
                and verifyNick(data.get("text", "").split()[3])  # 新昵称合法
            ):
                # 提取旧昵称和新昵称
                data["old_nick"] = data.get("text", "").split(" ")[0]
                data["new_nick"] = data.get("text", "").split(" ")[3]
                return ChangeNickPackage(**data)
            # 识别房间锁定事件
            elif (
                data.get("text", "")
                == "You have been denied access to that channel and have been moved somewhere else. Retry later or wait for a mod to move you."
            ):
                return LockroomPackage(cmd="info", time=data["time"])
            # 普通 info 消息
            return InfoPackage(**data)
        # 处理私聊类型的 info
        elif data.get("type") == "whisper":
            if data.get("text", "").startswith("You whispered to"):
                # 自己发出的私聊确认
                data["content"] = data["text"].split(": ", 1)[1]
                return WhisperSentPackage(**data)
            else:
                # 接收到的私聊
                data["userid_to"] = data["to"]  # 重命名字段
                del data["to"]
                data["content"] = data["text"].split(": ", 1)[1]  # 提取实际内容
                return WhisperPackage(**data)
        # 处理邀请类型的 info
        elif data.get("type") == "invite":
            # 重命名字段以符合 Pydantic 模型
            data["from_nick"] = data["from"]
            data["to_userid"] = data["to"]
            del data["from"]  # 删除原字段
            del data["to"]
            return InvitePackage(**data)
    # 处理在线用户列表设置（首次加入频道时）
    elif command == "onlineSet":
        return OnlineSetPackage(**data)
    # 处理新用户加入
    elif command == "onlineAdd":
        return OnlineAddPackage(**data)
    # 处理用户离开
    elif command == "onlineRemove":
        return OnlineRemovePackage(**data)
    # 处理用户信息更新
    elif command == "updateUser":
        return UpdateUserPackage(**data)
    # 处理消息编辑
    elif command == "updateMessage":
        return UpdateMessagePackage(**data)
    # 处理验证码请求
    elif command == "captcha":
        return CaptchaPackage(**data)
    # 处理警告消息
    elif command == "warn":
        # 检查是否为速率限制警告
        if data.get("text") in [
            "You are joining channels too fast. Wait a moment and try again.",
            "You are changing colors too fast. Wait a moment before trying again.",
            "You are sending invites too fast. Wait a moment before trying again.",
            "You are changing nicknames too fast. Wait a moment before trying again.",
            "You are sending too much text. Wait a moment and try again.\nPress the up arrow key to restore your last message.",
            "You are rate-limited or blocked.",
        ]:
            # 转换为结构化的速率限制包
            return RateLimitedPackage(
                cmd="warn",
                type=RL_MAPPING[data.get("text", "")],  # 映射到类型标识
                text=data.get("text", ""),
            )
        # 普通警告消息
        return WarnPackage(**data)
    # 未识别的命令：返回原始 JSON
    return UncatchedPackage(rawjson=data)
