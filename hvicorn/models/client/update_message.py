"""UpdateMessage 模块 - 更新消息请求

包含 UpdateMessageRequest 模型，用于表示编辑已发送消息的请求。
"""

from pydantic import BaseModel
from typing import Optional, Literal


class UpdateMessageRequest(BaseModel):
    """更新消息请求模型
    
    表示编辑已发送消息的请求。
    只有带 customId 的消息才能被编辑。
    
    属性:
        cmd: 命令类型，始终为 "updateMessage"
        customId: 要编辑的消息的唯一标识符
        mode: 编辑模式
            - "overwrite": 完全替换消息内容
            - "prepend": 在消息开头插入文本
            - "append": 在消息末尾追加文本
            - "complete": 标记消息为完成，之后不可再编辑
        text: 要编辑的文本内容（complete 模式下为 None）
    """
    cmd: Literal["updateMessage"] = "updateMessage"
    customId: str
    mode: Literal["overwrite", "prepend", "append", "complete"]
    text: Optional[str] = None
