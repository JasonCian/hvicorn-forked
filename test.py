"""hvicorn 框架综合测试示例

这个文件演示了 hvicorn 的主要功能：
- 启动函数
- 事件处理
- 命令系统
- 可编辑消息
- 私聊和动作消息
- 邀请功能
"""

from hvicorn import Bot, CommandContext, ChatPackage
from logging import basicConfig, DEBUG
from asyncio import run, sleep
import random
import traceback

# 启用调试日志，查看详细的 WebSocket 交互信息
basicConfig(level=DEBUG)

# 创建 Bot 实例，昵称为 "test_hvicorn"，加入 "test" 频道
bot = Bot("test_hvicorn", "test")
owner_trip = "LMeOEB"  # 机器人主人的识别码


@bot.startup
async def greetings():
    """启动函数 - 机器人加入频道后自动执行
    
    发送欢迎消息，介绍可用命令。
    """
    await bot.send_message(
        "Hello world! I am hvicorn demo bot.\nCommands:\n\t`.hv editmsg` - demos updatemessage.\n\t`.hv invite` - demos inviting.\n\t`.hv emote` - demos emote.\n\t`.hv threading` - demos multithreading.\n\t`.hv plugin` - test plugin.\n\t`.hv afk` - a test plugin again, but it can mark you as AfKing.\nSpecial command: try sending awa"
    )


@bot.on(ChatPackage)
async def on_chat(msg: ChatPackage):
    """聊天消息事件处理器
    
    当有人在消息中包含 "awa" 时：
    1. 发送用户信息
    2. 发送私聊消息
    3. 发送动作消息（拥抱）
    """
    if "awa" in msg.text:
        # 在频道中公开回复
        await bot.send_message(
            f"Hey, @{msg.nick}, I see you awa-ing!\nHere's ur info(By hvicorn): {bot.get_user_by_nick(msg.nick)}"
        )
        await sleep(1)  # 等待 1 秒
        # 发送私聊消息
        await bot.whisper(msg.nick, "Here's a *✨secret✨* message for you!")
        await sleep(1)
        # 发送动作消息
        await bot.emote(f"hugs {msg.nick}")


@bot.command(".hv editmsg")
async def editmsg(ctx: CommandContext):
    """演示可编辑消息功能
    
    发送一条消息，5 秒后追加内容。
    """
    # 发送可编辑消息
    msg = await ctx.bot.send_message("Do you like playing ", editable=True)
    await sleep(5)  # 等待 5 秒
    # 随机选择一个游戏名称
    choice = (
        random.choice(["Genshin impact", "Honkai impact", "Minecraft", "Project sekai"])
        + "?"
    )
    # 追加到消息末尾
    await msg.append(choice)


@bot.command(".hv invite")
async def invite(ctx: CommandContext):
    """演示邀请功能
    
    邀请命令发送者加入另一个频道。
    """
    await ctx.bot.invite(ctx.sender.nick, "somechannel")


@bot.command(".hv emote")
async def emote(ctx: CommandContext):
    """演示动作消息功能
    
    发送一条动作消息（斜体显示）。
    """
    await ctx.bot.emote("awa")


@bot.command(".hv async")
async def async_command(ctx: CommandContext):
    await ctx.respond("Use any command if u want. this command will block for 10secs.")
    await sleep(10)
    await ctx.respond("I'm back!")


@bot.command(".hv exec")
async def execute(ctx: CommandContext):
    if ctx.sender.trip != owner_trip:
        return await ctx.respond("I wouldn't do that...")
    try:
        exec(ctx.text.split(" ", 2)[2], globals())
    except Exception:
        traceback.print_exc()
    return await ctx.respond("Done! check console!")


@bot.register_global_function
async def log(event):
    print(event)


async def run_bot():
    await bot.load_plugin("testplugin", command_name=".hv plugin")
    await bot.load_plugin("example_plugin_afk", command_prefix=".hv afk")

    await bot.run()


run(run_bot())
