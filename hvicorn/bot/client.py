"""hvicorn Bot 核心模块

这个模块包含了 hvicorn 框架的核心 Bot 类和相关功能。
Bot 类负责管理 WebSocket 连接、事件处理、命令路由和用户状态跟踪。
"""

import asyncio
import websockets
import ssl
from typing import Optional, Literal, Callable, List, Dict, Any, Union
from pydantic import BaseModel
from hvicorn.models.client import *
from hvicorn.models.server import *
from json import loads, dumps
from hvicorn.utils.generate_customid import generate_customid
from hvicorn.utils.json_to_object import json_to_object, verifyNick
from hvicorn.models.client import CustomRequest
from hvicorn.bot.optional_features import OptionalFeatures
from traceback import format_exc
from logging import debug, warning

# hack.chat 的 WebSocket 服务器地址
WS_ADDRESS = "wss://hack.chat/chat-ws"


class CommandContext:
    """命令上下文类
    
    表示命令执行时的上下文环境，包含命令发送者、触发方式、参数等信息。
    这个类会被传递给所有的命令处理函数，提供便捷的响应和查询方法。
    """

    def __init__(
        self,
        bot: "Bot",
        sender: User,
        triggered_via: Literal["chat", "whisper"],
        text: str,
        args: str,
        event: Union[WhisperPackage, ChatPackage],
    ) -> None:
        """初始化命令上下文实例

        Args:
            bot (Bot): Bot 实例引用
            sender (User): 触发命令的用户对象
            triggered_via (Literal["chat", "whisper"]): 命令触发方式（公开聊天或私聊）
            text (str): 完整的命令文本（包括命令前缀）
            args (str): 命令参数（不包括命令前缀的部分）
            event (Union[WhisperPackage, ChatPackage]): 触发命令的原始事件对象
        """
        self.bot: "Bot" = bot  # Bot 实例
        self.sender: User = sender  # 命令发送者
        self.triggered_via: Literal["chat", "whisper"] = triggered_via  # 触发方式
        self.text: str = text  # 完整命令文本
        self.args: str = args  # 命令参数
        self.event: Union[WhisperPackage, ChatPackage] = event  # 原始事件

    async def respond(self, text, at_sender=True):
        """响应命令
        
        根据命令的触发方式（公开聊天或私聊）自动选择合适的响应方式。
        如果命令来自公开聊天，则在频道中回复；如果来自私聊，则私聊回复。

        Args:
            text (str): 要响应的文本内容
            at_sender (bool, optional): 是否在响应中 @ 提及发送者。默认为 True。
                                       仅在公开聊天时有效，私聊时忽略此参数。
        """
        if self.triggered_via == "chat":
            # 在公开频道中回复，可选择是否 @ 发送者
            await self.bot.send_message(
                ("@" + self.sender.nick + " " if at_sender else "") + str(text)
            )
        elif self.triggered_via == "whisper":
            # 通过私聊回复
            await self.bot.whisper(self.sender.nick, text)
        else:
            warning("Unknown trigger method, ignoring")


class Bot:
    """hack.chat 机器人类
    
    这是 hvicorn 框架的核心类，负责管理与 hack.chat 服务器的连接、
    事件处理、命令路由、用户状态跟踪等所有机器人功能。
    
    主要功能：
    - WebSocket 连接管理
    - 自动维护在线用户列表
    - 事件分发系统（全局处理器和类型特定处理器）
    - 命令注册和自动路由
    - 插件系统支持
    """

    def __init__(self, nick: str, channel: str, password: Optional[str] = None) -> None:
        """初始化 Bot 实例

        Args:
            nick (str): 机器人的昵称（1-24 个字符，仅限字母数字和下划线）
            channel (str): 要加入的频道名称
            password (Optional[str], optional): 频道密码（如果需要）。默认为 None。
        """
        self.nick = nick  # 机器人昵称
        self.channel = channel  # 目标频道
        self.password = password  # 频道密码（可选）
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None  # WebSocket 连接对象
        self.startup_functions: List[Callable] = []  # 启动时执行的函数列表
        # 事件处理函数字典，__GLOBAL__ 是特殊键，用于全局事件处理
        self.event_functions: Dict[Any, List[Callable]] = {
            "__GLOBAL__": [self._internal_handler]  # 内部处理器默认注册为全局处理器
        }
        self.wsopt: Dict = {}  # WebSocket 连接选项
        self.killed: bool = False  # 机器人是否已被终止的标志
        self.users: List[User] = []  # 当前频道的在线用户列表（自动维护）
        self.commands: Dict[str, Callable] = {}  # 命令前缀到处理函数的映射
        self.optional_features: OptionalFeatures = OptionalFeatures()  # 可选功能配置
        self.loaded_plugins: Dict[str, Dict[str, List]] = {}  # 已加载插件的跟踪信息

    async def _send_model(self, model: BaseModel) -> None:
        """发送 Pydantic 模型到 WebSocket
        
        将 Pydantic 模型序列化为 JSON 并通过 WebSocket 发送到服务器。
        自动过滤 None 值字段，CustomRequest 类型会直接使用原始 JSON。

        Args:
            model (BaseModel): 要发送的 Pydantic 模型对象
        """
        if type(model) == CustomRequest:
            # CustomRequest 特殊处理：直接使用原始 JSON（绕过 Pydantic 验证）
            payload = model.rawjson
        else:
            try:
                # 将 Pydantic 模型转换为字典
                data = model.model_dump()
            except:
                warning(f"Cannot stringify model, ignoring: {model}")
                return
            # 过滤掉值为 None 的字段，减少传输数据量
            payload = {}
            for k, v in data.items():
                if v != None:
                    payload.update({k: v})
        if self.websocket:
            debug(f"Sent payload: {payload}")
            # 将字典序列化为 JSON 字符串并发送
            await self.websocket.send(dumps(payload))
        else:
            warning(f"Websocket isn't open, ignoring: {model}")

    def get_users_by(
        self,
        by: Literal[
            "nick",
            "hash",
            "trip",
            "color",
            "isBot",
            "level",
            "uType",
            "userid",
            "function",
        ],
        matches: Union[str, Callable],
    ) -> List[User]:
        """根据指定属性或自定义函数获取用户列表
        
        支持两种查询方式：
        1. 属性匹配：根据用户对象的具体属性（如昵称、等级等）进行精确匹配
        2. 函数过滤：使用自定义函数对每个用户进行判断

        Args:
            by (Literal): 查询依据，可以是用户属性名或 "function"
                - "nick": 昵称
                - "hash": 用户哈希值
                - "trip": 识别码
                - "color": 颜色
                - "isBot": 是否为机器人
                - "level": 等级
                - "uType": 用户类型（user/mod/admin）
                - "userid": 用户 ID
                - "function": 使用自定义函数过滤
            matches (Union[str, Callable]): 匹配值或过滤函数
                - 当 by != "function" 时：要匹配的具体值
                - 当 by == "function" 时：接受 User 对象返回 bool 的函数

        Returns:
            List[User]: 匹配的用户对象列表
            
        示例:
            # 获取所有管理员
            admins = bot.get_users_by("uType", "admin")
            # 使用自定义函数获取高等级用户
            vips = bot.get_users_by("function", lambda u: u.level >= 100)
        """
        results = []
        for user in self.users:
            if by != "function":
                # 属性精确匹配
                if user.__dict__.get(by) == matches:
                    results.append(user)
            else:
                # 使用自定义函数过滤
                if callable(matches):
                    if matches(user):
                        results.append(user)
                else:
                    raise ValueError(f"Function {matches} is not callable")
        return results

    def get_user_by(
        self,
        by: Literal[
            "nick",
            "hash",
            "trip",
            "color",
            "isBot",
            "level",
            "uType",
            "userid",
            "function",
        ],
        matches: Union[str, Callable],
    ) -> Optional[User]:
        """
        Get a single user by a specific attribute or custom function.

        Args:
            by (Literal): The attribute to match by.
            matches (Union[str, Callable]): The value to match or a custom function.

        Returns:
            Optional[User]: The matching user, if found.
        """
        result = self.get_users_by(by, matches)
        return result[0] if result else None

    def get_user_by_nick(self, nick: str) -> Optional[User]:
        """
        Get a user by their nickname.

        Args:
            nick (str): The nickname to search for.

        Returns:
            Optional[User]: The matching user, if found.
        """
        return self.get_user_by("nick", nick)

    async def _internal_handler(self, event: BaseModel) -> None:
        """内部事件处理器
        
        这是框架的核心处理器，负责维护机器人的内部状态。
        主要处理以下任务：
        1. 用户列表同步（OnlineSet/Add/Remove）
        2. 命令路由（从 Chat/Whisper 事件中提取并执行命令）
        3. 用户信息更新（UpdateUser 事件）
        
        此处理器自动注册为全局事件处理器，会接收所有事件。

        Args:
            event (BaseModel): 要处理的事件对象
        """
        # 处理在线用户列表设置事件（首次加入频道或刷新）
        if isinstance(event, OnlineSetPackage):
            self.users = event.users  # 完整替换用户列表
        # 处理新用户加入事件
        elif isinstance(event, OnlineAddPackage):
            self.users.append(
                User(
                    channel=event.channel,
                    color=event.color,
                    hash=event.hash,
                    isBot=event.isBot,
                    isme=False,
                    level=event.level,
                    nick=event.nick,
                    trip=event.trip,
                    uType=event.uType,
                    userid=event.userid,
                )
            )
        # 处理用户离开事件
        elif isinstance(event, OnlineRemovePackage):
            user = self.get_user_by_nick(event.nick)
            if user:
                self.users.remove(user)  # 从列表中移除该用户
        # 处理公开聊天消息中的命令
        if isinstance(event, ChatPackage):
            for command in self.commands.items():
                # 检查消息是否以命令前缀开头（前缀+空格）或完全匹配前缀
                if event.text.startswith(command[0] + " ") or event.text == command[0]:
                    try:
                        # 从用户列表中查找发送者
                        user = self.get_user_by_nick(event.nick)
                        if not user:
                            raise RuntimeError("User not found")
                        # 创建命令上下文并调用处理函数
                        await command[1](
                            CommandContext(
                                self,
                                user,
                                "chat",  # 触发方式：公开聊天
                                event.text,  # 完整消息文本
                                (
                                    # 提取命令参数（去除前缀后的部分）
                                    event.text.split(" ", 1)[1]
                                    if event.text != command[0]
                                    else ""  # 如果只有前缀，参数为空字符串
                                ),
                                event,  # 原始事件对象
                            )
                        )
                    except:
                        warning(f"Ignoring exception in command: \n{format_exc()}")
        if isinstance(event, WhisperPackage):
            for command in self.commands.items():
                if (
                    event.content.startswith(command[0] + " ")
                    or event.content == command[0]
                ):
                    try:
                        user = self.get_user_by_nick(event.nick)
                        if not user:
                            raise RuntimeError("User not found")
                        await command[1](
                            CommandContext(
                                self,
                                user,
                                "whisper",
                                event.content,
                                (
                                    event.content.split(" ", 1)[1]
                                    if event.content != command[0]
                                    else ""
                                ),
                                event,
                            )
                        )
                    except:
                        warning(f"Ignoring exception in command: \n{format_exc()}")
        # 处理用户信息更新事件
        if isinstance(event, UpdateUserPackage):
            if not event.nick:
                return
            # 找到要更新的用户对象
            target_user = self.get_user_by_nick(event.nick)
            # 遍历更新包中的所有字段
            for k, v in event.model_dump().items():
                if (
                    k in dir(target_user)  # 字段存在于用户对象中
                    and v != None  # 新值不为空
                    and v != target_user.__getattribute__(k)  # 值发生了变化
                ):
                    # 更新用户对象的对应属性
                    target_user.__setattr__(k, v)

    async def _connect(self) -> None:
        """连接到 WebSocket 服务器
        
        建立与 hack.chat 服务器的 WebSocket 连接。
        如果启用了 bypass_gfw_dns_poisoning 功能，
        会使用 IP 地址直连以绕过 GFW 的 DNS 污染（但可能存在安全风险）。
        """
        debug(f"Connecting to {WS_ADDRESS}, Websocket options: {self.wsopt}")
        if (
            WS_ADDRESS == "wss://hack.chat/chat-ws"
            and self.optional_features.bypass_gfw_dns_poisoning
        ):
            # 启用 GFW 绕过模式：使用 IP 地址直连
            debug(
                f"Connecting to wss://104.131.138.176/chat-ws instead of wss://hack.chat/chat-ws to bypass GFW DNS poisoning"
            )
            warning(
                f"Enabling bypass_gfw_dns_poisoning can bypass GFW's DNS poisoning, but this can cause man-in-the-middle attacks."
            )
            # 创建不验证证书的 SSL 上下文（存在安全风险）
            insecure_ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            insecure_ssl_context.check_hostname = False
            insecure_ssl_context.verify_mode = ssl.CERT_NONE
            # 使用 IP 地址但保留域名的 SNI
            self.websocket = await websockets.connect(
                "wss://hack.chat/chat-ws",
                host="104.131.138.176",  # 直接连接到 IP
                ssl=insecure_ssl_context,
                **self.wsopt,
            )
        else:
            # 正常连接模式
            self.websocket = await websockets.connect(WS_ADDRESS, **self.wsopt)
        debug(f"Connected!")

    async def _run_events(
        self, event_type: Any, args: list, taskgroup: asyncio.TaskGroup
    ):
        """运行特定类型的事件处理器
        
        从注册的处理器中找到对应类型的处理函数并执行。
        支持同步和异步处理函数，异步函数会以 Task 形式并发执行。

        Args:
            event_type (Any): 事件类型（如 ChatPackage）或 "__GLOBAL__"
            args (list): 要传递给处理函数的参数列表
            taskgroup (asyncio.TaskGroup): 用于管理并发任务的任务组
        """
        for function in self.event_functions.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(function):
                    # 异步函数：创建任务并发执行
                    taskgroup.create_task(function(*args))
                else:
                    # 同步函数：直接调用
                    function(*args)
            except:
                warning(f"Ignoring exception in event: \n{format_exc()}")

    async def join(self) -> None:
        """加入指定的频道
        
        发送 join 请求包到服务器，将机器人加入到目标频道。
        如果频道设有密码，会自动带上密码。
        """
        debug(f"Sending join package")
        await self._send_model(
            JoinRequest(nick=self.nick, channel=self.channel, password=self.password)
        )
        await asyncio.sleep(1)  # 等待 1 秒让服务器处理
        debug(f"Done!")

    async def send_message(self, text, editable=False) -> Message:
        """发送消息到频道
        
        在当前频道发送一条公开消息。
        如果设置 editable=True，会生成 customId，使消息可编辑。

        Args:
            text (str): 要发送的消息文本
            editable (bool, optional): 是否使消息可编辑。默认为 False。

        Returns:
            Message: 消息对象，如果 editable=True，可以通过 msg._edit() 编辑
            
        示例:
            # 普通消息
            await bot.send_message("Hello, world!")
            # 可编辑消息
            msg = await bot.send_message("Loading...", editable=True)
            await msg._edit("overwrite", "Done!")
        """
        # 如果需要可编辑，生成唯一 ID
        customId = generate_customid() if editable else None
        await self._send_model(ChatRequest(text=text, customId=customId))

        # 创建消息对象
        msg = Message(text, customId)

        # 为消息对象添加 _edit 方法
        async def wrapper(*args, **kwargs):
            await self._send_model(msg._generate_edit_request(*args, **kwargs))

        msg.__setattr__("_edit", wrapper)
        return msg

    async def whisper(self, nick: str, text: str) -> None:
        """发送私聊消息
        
        向指定用户发送私聊（只有对方和自己可见）。

        Args:
            nick (str): 接收者的昵称
            text (str): 私聊内容
        """
        await self._send_model(WhisperRequest(nick=nick, text=text))

    async def emote(self, text: str) -> None:
        """发送动作消息
        
        发送一条动作消息（类似 IRC 的 /me 命令）。
        在页面上会显示为斜体格式，如：*BotName does something*

        Args:
            text (str): 动作文本
            
        示例:
            await bot.emote("挥手问好")
            # 显示为: *BotName 挥手问好*
        """
        await self._send_model(EmoteRequest(text=text))

    async def change_color(self, color: str = "reset") -> None:
        """更改机器人的颜色
        
        设置机器人昵称显示的颜色。可以使用颜色名或十六进制颜色代码。

        Args:
            color (str, optional): 新颜色。默认为 "reset" （重置为默认颜色）。
                                   支持颜色名（如 "red"、"blue"）或 hex 值（如 "#FF5733"）
        """
        await self._send_model(ChangeColorRequest(color=color))

    async def change_nick(self, nick: str) -> None:
        """更改机器人的昵称
        
        修改机器人在频道中显示的昵称。
        昵称必须符合 hack.chat 的命名规则：1-24 个字符，仅包含字母、数字和下划线。

        Args:
            nick (str): 新昵称

        Raises:
            ValueError: 如果昵称不符合命名规则
            
        注意:
            - 更改成功后，self.nick 会自动更新
            - 频道中会显示 "OldNick is now NewNick"
        """
        if not verifyNick(nick):
            raise ValueError("Invalid Nickname")
        await self._send_model(ChangeNickRequest(nick=nick))
        self.nick = nick  # 更新内部记录的昵称

    async def invite(self, nick: str, channel: Optional[str] = None) -> None:
        """
        Invite a user to a channel.

        Args:
            nick (str): The nickname of the user to invite.
            channel (Optional[str], optional): The channel to invite to. Defaults to None.
        """
        await self._send_model(InviteRequest(nick=nick, to=channel))

    async def ping(self) -> None:
        """
        Send a ping request to the server.
        """
        await self._send_model(PingRequest())

    def on(
        self, event_type: Optional[Any] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """事件处理器装饰器
        
        用于注册事件处理函数的装饰器。
        可以指定特定事件类型，或不指定以注册为全局处理器。

        Args:
            event_type (Optional[Any], optional): 要处理的事件类型（如 ChatPackage）。
                                                  如为 None，则注册为全局处理器。
                                                  默认为 None。

        Returns:
            Callable: 装饰器函数
            
        示例:
            # 处理特定类型的事件
            @bot.on(hvicorn.ChatPackage)
            async def on_chat(event: hvicorn.ChatPackage):
                print(f"{event.nick}: {event.text}")
            
            # 全局处理器（接收所有事件）
            @bot.on()
            async def on_any_event(event):
                print(f"Event: {type(event)}")
        """

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            nonlocal event_type
            if event_type is None:
                event_type = "__GLOBAL__"  # 未指定类型，注册为全局处理器
            if event_type in self.event_functions.keys():
                # 追加到现有处理器列表
                self.event_functions[event_type].append(func)
                debug(f"Added handler for {event_type}: {func}")
            else:
                # 创建新的处理器列表
                self.event_functions[event_type] = [func]
                debug(f"Set handler for {event_type} to {func}")
            return func

        return wrapper

    def startup(self, function: Callable) -> None:
        """注册启动函数
        
        注册一个在机器人启动时执行的函数。
        这些函数会在加入频道后、开始接收事件前执行。

        Args:
            function (Callable): 要在启动时运行的函数（支持同步和异步）
            
        示例:
            @bot.startup
            async def on_start():
                print("机器人已启动！")
                await bot.send_message("大家好！")
        """
        self.startup_functions.append(function)
        debug(f"Added startup function: {function}")
        return None

    def command(
        self, prefix: str
    ) -> Callable[[Callable[[CommandContext], Any]], Callable[[CommandContext], Any]]:
        """命令处理器装饰器
        
        用于注册命令处理函数的装饰器。
        当用户发送的消息以指定前缀开头时，会触发对应的处理函数。

        Args:
            prefix (str): 命令前缀（如 "/ping"、"!help" 等）

        Returns:
            Callable: 装饰器函数
            
        注意:
            - 使用装饰器时，处理函数 **必须** 是异步的 (async def)
            - 如果需要同步函数，请使用 register_command() 方法
            
        示例:
            @bot.command("/ping")
            async def pong(ctx: hvicorn.CommandContext):
                await ctx.respond("Pong!")
            
            # 用户发送 "/ping" 或 "/ping hello" 都会触发此命令
        """

        def wrapper(func: Callable[[CommandContext], Any]):
            if prefix in self.commands.keys():
                # 警告：覆盖现有命令
                warning(
                    f"Overriding function {self.commands[prefix]} for command prefix {prefix}"
                )
            self.commands[prefix] = func
            return func

        return wrapper

    def register_event_function(self, event_type: Any, function: Callable):
        """
        Register an event handler function.

        Args:
            event_type (Any): The type of event to handle.
            function (Callable): The function to handle the event.
        """
        if event_type in self.event_functions.keys():
            self.event_functions[event_type].append(function)
            debug(f"Added handler for {event_type}: {function}")
        else:
            self.event_functions[event_type] = [function]
            debug(f"Set handler for {event_type} to {function}")

    def register_global_function(self, function: Callable):
        """
        Register a global event handler function.

        Args:
            function (Callable): The function to handle all events.
        """
        self.register_event_function("__GLOBAL__", function)

    def register_startup_function(self, function: Callable):
        """
        Register a startup function.

        Args:
            function (Callable): The function to run at startup.
        """
        self.startup_functions.append(function)
        debug(f"Added startup function: {function}")

    def register_command(self, prefix: str, function: Callable):
        """
        Register a command handler function.

        Args:
            prefix (str): The command prefix.
            function (Callable): The function to handle the command.
        """
        if prefix in self.commands.keys():
            warning(
                f"Overriding function {self.commands[prefix]} for command prefix {prefix}"
            )
        self.commands[prefix] = function

    def kill(self) -> None:
        """
        Kill the bot and close the websocket connection.

        Raises:
            ConnectionError: If the websocket is already closed or not open.
        """
        self.killed = True
        debug("Killing ws")
        if not self.websocket:
            raise ConnectionError("Websocket is already closed / not open")
        asyncio.create_task(self.websocket.close())

    async def close_ws(self) -> None:
        """
        Close the websocket connection.

        Raises:
            ConnectionError: If the websocket is already closed or not open.
        """
        debug("Closing ws")
        if not self.websocket:
            raise ConnectionError("Websocket is already closed / not open")
        await self.websocket.close()

    async def load_plugin(
        self,
        plugin_name: str,
        init_function: Optional[Callable] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Load a plugin.

        Args:
            plugin_name (str): The name of the plugin to load.
            init_function (Optional[Callable], optional): Custom initialization function. Defaults to None.
            *args: Additional positional arguments to pass to the init function.
            **kwargs: Additional keyword arguments to pass to the init function.
        """
        # 记录插件加载前的状态
        commands_before = set(self.commands.keys())
        event_handlers_before = {k: len(v) for k, v in self.event_functions.items()}
        
        if not init_function:
            try:
                plugin = __import__(plugin_name)
            except ImportError:
                debug(f"Failed to load plugin {plugin_name}, ignoring")
                return
            if "plugin_init" not in dir(plugin):
                debug(f"Failed to find init function of plugin {plugin_name}, ignoring")
                return
            if not callable(plugin.plugin_init):
                debug(f"Init function of plugin {plugin_name} isn't callable, ignoring")
                return
            try:
                if asyncio.iscoroutinefunction(plugin.plugin_init):
                    await plugin.plugin_init(self, *args, **kwargs)
                else:
                    plugin.plugin_init(self, *args, **kwargs)
            except:
                debug(f"Failed to init plugin {plugin_name}: \n{format_exc()}")
                return
        else:
            try:
                if asyncio.iscoroutinefunction(init_function):
                    await init_function(self, *args, **kwargs)
                else:
                    init_function(self, *args, **kwargs)
            except:
                debug(f"Failed to init plugin {plugin_name}: \n{format_exc()}")
                return
        
        debug(f"Loaded plugin {plugin_name}")
        
        # 记录插件注册的命令和事件处理器（用于卸载）
        commands_after = set(self.commands.keys())
        new_commands = list(commands_after - commands_before)
        
        new_handlers = {}
        for event_type, handlers in self.event_functions.items():
            before_count = event_handlers_before.get(event_type, 0)
            if len(handlers) > before_count:
                new_handlers[event_type] = handlers[before_count:]
        
        self.loaded_plugins[plugin_name] = {
            "commands": new_commands,
            "handlers": new_handlers
        }

    def unload_plugin(self, plugin_name: str) -> None:
        """
        卸载插件，移除其注册的所有命令和事件处理器。

        Args:
            plugin_name (str): 要卸载的插件名称
        """
        if plugin_name not in self.loaded_plugins:
            debug(f"Plugin {plugin_name} is not loaded, ignoring unload request")
            return
        
        plugin_info = self.loaded_plugins[plugin_name]
        
        # 移除插件注册的命令
        for command in plugin_info["commands"]:
            if command in self.commands:
                del self.commands[command]
                debug(f"Unregistered command: {command}")
        
        # 移除插件注册的事件处理器
        for event_type, handlers in plugin_info["handlers"].items():
            if event_type in self.event_functions:
                for handler in handlers:
                    if handler in self.event_functions[event_type]:
                        self.event_functions[event_type].remove(handler)
                        debug(f"Unregistered handler for {event_type}")
        
        # 从已加载插件列表中移除
        del self.loaded_plugins[plugin_name]
        debug(f"Unloaded plugin {plugin_name}")

    async def run(self, ignore_self: bool = True, wsopt: Dict = {}) -> None:
        """
        Run the bot.

        Args:
            ignore_self (bool, optional): Whether to ignore messages from the bot itself. Defaults to True.
            wsopt (Dict, optional): Additional websocket options. Defaults to {}.

        Raises:
            RuntimeError: If there's a websocket connection error.
        """
        self.wsopt = wsopt if wsopt != {} else self.wsopt
        await self._connect()
        await self.join()
        for function in self.startup_functions:
            debug(f"Running startup function: {function}")
            if asyncio.iscoroutinefunction(function):
                await function()
            else:
                function()
        try:
            async with asyncio.TaskGroup() as taskgroup:
                while not self.killed and self.websocket is not None:
                    try:
                        package = await self.websocket.recv()
                    except websockets.ConnectionClosed:
                        debug("Connection closed")
                        self.killed = True
                        await self._run_events("disconnect", [], taskgroup=taskgroup)
                        break
                    except Exception as e:
                        raise RuntimeError("Websocket connection error: ", e)
                    if not package:
                        debug("Killed")
                        self.killed = True
                        break
                    package_dict: Dict[Any, Any] = loads(package)
                    try:
                        event = json_to_object(package_dict)
                    except Exception as e:
                        debug(e)
                        warning(
                            f"Failed to parse event, ignoring: {package_dict} cause exception: \n{format_exc()}"
                        )
                        continue
                    debug(f"Got event {type(event)}::{str(event)}")
                    if isinstance(
                        event,
                        (
                            ChatPackage,
                            EmotePackage,
                            OnlineAddPackage,
                            OnlineRemovePackage,
                            WhisperPackage,
                        ),
                    ):
                        if event.nick == self.nick and ignore_self:
                            debug("Found self.nick, ignoring")
                            continue
                    else:
                        debug("No nick provided in event, passing loopcheck")
                    await self._run_events("__GLOBAL__", [event], taskgroup)
                    await self._run_events(type(event), [event], taskgroup)
                if self.websocket and self.websocket.open:
                    self.kill()
        except asyncio.exceptions.CancelledError:
            pass
