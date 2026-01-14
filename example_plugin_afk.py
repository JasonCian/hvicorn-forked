"""示例插件: AFK (离开键盘) 功能

这个插件允许用户标记自己为 AFK（Away From Keyboard）状态。
主要功能:
1. 用户可以通过命令标记自己为 AFK，并可选提供原因
2. 当其他人 @ 提及AFK 用户时，会自动提示该用户处于 AFK 状态
3. AFK 用户再次发言时会自动取消 AFK 状态

示例用法:
    await bot.load_plugin(
        "example_plugin_afk",
        command_prefix="/afk",
        on_afk="你已被标记为离开。",
        afk_tip="{nick} 现在处于离开状态。"
    )
"""

import hvicorn
from typing import Dict, Optional

# 全局字典，存储 AFK 用户及其原因
# 键: 用户昵称，值: AFK 原因（可选）
afked_users: Dict[str, Optional[str]] = {}


async def plugin_init(
    bot: hvicorn.Bot,
    command_prefix: str = "/afk",
    on_afk: str = "You are marked AfK.",
    afk_tip: str = "{nick} is now AfK.",
    already_afk: str = "You are already AfKed.",
    reason: str = "Reason: {reason}",
    welcome_back: str = "Welcome back.",
):
    """插件初始化函数
    
    所有 hvicorn 插件必须定义一个名为 plugin_init 的函数。
    这个函数会在插件加载时被调用，用于注册命令和事件处理器。
    
    Args:
        bot: hvicorn Bot 实例
        command_prefix: AFK 命令的前缀，默认为 "/afk"
        on_afk: 用户标记 AFK 时的提示消息
        afk_tip: 当有人 @ AFK 用户时的提示消息，{nick} 会被替换为用户昵称
        already_afk: 用户已经是 AFK 状态时的提示
        reason: 显示 AFK 原因的格式，{reason} 会被替换为实际原因
        welcome_back: 用户返回时的欢迎消息
    """

    async def mark_afk(ctx: hvicorn.CommandContext):
        """处理 AFK 命令
        
        将用户标记为 AFK 状态。用户可以提供可选的原因。
        """
        reason = ctx.args if ctx.args else None  # 获取 AFK 原因（如果有）
        if ctx.sender.nick in afked_users.keys():
            # 用户已经是 AFK 状态
            return await ctx.respond(already_afk)
        # 将用户添加到 AFK 字典中
        afked_users.update({ctx.sender.nick: reason})
        return await ctx.respond(on_afk)

    async def back_check(event):
        """检查 AFK 用户是否返回
        
        全局事件处理器，监控所有事件。
        当 AFK 用户再次发言时，自动移除其 AFK 状态。
        """
        if "nick" not in dir(event):
            # 事件不包含昵称，忽略
            return
        if "text" in dir(event) and event.text.startswith(command_prefix):
            # 如果是 AFK 命令本身，不取消 AFK 状态
            return
        if event.nick in afked_users.keys():
            # 用户发言，移除 AFK 状态
            del afked_users[event.nick]
            return await bot.send_message(f"@{event.nick} {welcome_back}")

    async def on_chat(event: hvicorn.ChatPackage):
        """处理聊天消息，检查是否 @ 了 AFK 用户
        
        当有人 @ 提及 AFK 用户时，自动发送提示。
        """
        # 遍历所有 AFK 用户
        for user in afked_users.items():
            if f"@{user[0]}" in event.text:
                # 消息中 @ 了这个 AFK 用户
                await bot.send_message(
                    f"@{event.nick} {afk_tip.format(nick=user[0])}"
                    + (" " + reason.format(reason=user[1]) if user[1] else "")  # 如果有原因，也显示
                )
                return  # 只处理第一个匹配的 AFK 用户

    # 注册命令处理器
    bot.register_command(command_prefix, mark_afk)
    # 注册全局事件处理器（用于检查用户返回）
    bot.register_global_function(back_check)
    # 注册聊天消息处理器（用于检查 @ 提及）
    bot.register_event_function(hvicorn.ChatPackage, on_chat)
