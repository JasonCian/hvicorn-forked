"""Chat 模块 - 聊天消息相关类

包含 Message 类（可编辑消息）和 ChatRequest（发送消息请求）。
"""

from pydantic import BaseModel
from typing import Optional, Literal
from hvicorn.models.client.update_message import UpdateMessageRequest
from asyncio import run
from warnings import warn


class Message:
    """异步消息类
    
    表示一条发送到 hack.chat 的消息。
    如果在发送时指定了 customId，该消息就可以在发送后编辑。
    
    特性:
        text (str): 消息内容
        customId (Optional[str]): 唯一标识符，如果提供则消息可编辑
        editable (bool): 消息是否可编辑
        
    编辑模式:
        - overwrite: 完全替换消息内容
        - prepend: 在消息开头插入文本
        - append: 在消息末尾追加文本
        - complete: 标记消息为完成，之后不可再编辑
    """

    def __init__(self, text: str, customId: Optional[str] = None) -> None:
        """初始化 Message 实例

        Args:
            text (str): 消息内容
            customId (Optional[str], optional): 唯一标识符。默认为 None。
        """
        self.text = text
        self.customId = customId
        self.editable = customId is not None  # 有 customId 才可编辑

    def _generate_edit_request(
        self, mode: Literal["overwrite", "prepend", "append", "complete"], text: str
    ):
        """生成消息编辑请求
        
        内部方法，用于创建 UpdateMessageRequest 对象。

        Args:
            mode (Literal["overwrite", "prepend", "append", "complete"]): 编辑模式
            text (str): 要用于编辑的文本

        Returns:
            UpdateMessageRequest: 表示编辑请求的对象

        Raises:
            ValueError: 如果消息不可编辑或缺少 customId
        """
        if not self.editable:
            raise ValueError("This message isn't editable.")
        if self.customId:
            return UpdateMessageRequest(customId=self.customId, mode=mode, text=text)
        else:
            raise ValueError("Missing customId")

    async def _edit(
        self, mode: Literal["overwrite", "prepend", "append", "complete"], text: str
    ) -> None: 
        """内部编辑方法
        
        此方法会在 Bot 类中被重写，用于实际发送编辑请求。
        """
        ...

    async def edit(self, text):
        """异步编辑消息（覆盖模式）
        
        完全替换消息内容。

        Args:
            text (str): 新的消息内容

        Returns:
            编辑方法的返回结果
            
        示例:
            msg = await bot.send_message("Hello", editable=True)
            await msg.edit("Hi there!")
        """
        self.text = text
        return await self._edit("overwrite", text)

    async def prepend(self, text):
        """异步在消息开头插入文本

        Args:
            text (str): 要插入的文本

        Returns:
            编辑方法的返回结果
            
        示例:
            msg = await bot.send_message("World", editable=True)
            await msg.prepend("Hello ")  # 结果: "Hello World"
        """
        self.text = text + self.text
        return await self._edit("prepend", text)

    async def append(self, text):
        """异步在消息末尾追加文本

        Args:
            text (str): 要追加的文本

        Returns:
            编辑方法的返回结果
            
        示例:
            msg = await bot.send_message("Hello", editable=True)
            await msg.append(" World")  # 结果: "Hello World"
        """
        self.text += text
        return await self._edit("append", text)

    async def complete(self):
        """异步标记消息为完成，使其不可再编辑
        
        调用此方法后，消息将不能再次被编辑。

        Returns:
            UpdateMessageRequest: 表示完成请求的对象

        Raises:
            SyntaxError: 如果缺少 customId
        """
        self.editable = False
        if not self.customId:
            raise SyntaxError("Missing customId")
        return UpdateMessageRequest(customId=self.customId, mode="complete")

    def __add__(self, string: str):
        """
        Implement the addition operator to append text to the message.

        Args:
            string (str): The text to append.

        Returns:
            Message: The updated Message instance.
        """
        warn(DeprecationWarning("The __add__ method starts a new event loop and is not considered best practice. Will be removed in a future release."))
        run(self.append(string))
        return self

    def __radd__(self, string: str):
        """
        Implement the right addition operator to prepend text to the message.

        Args:
            string (str): The text to prepend.

        Returns:
            Message: The updated Message instance.
        """
        warn(DeprecationWarning("The __radd__ method starts a new event loop and is not considered best practice. Will be removed in a future release."))
        run(self.prepend(string))
        return self


class ChatRequest(BaseModel):
    """聊天消息请求模型
    
    表示发送到 hack.chat 频道的公开消息请求。
    
    属性:
        cmd: 命令类型，始终为 "chat"
        text: 要发送的消息文本
        customId: 可选的唯一标识符，如果提供则消息可编辑
    """
    cmd: Literal["chat"] = "chat"
    text: str
    customId: Optional[str] = None
