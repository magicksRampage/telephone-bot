import discord


async def respond(resp: str, msg: discord.Message):
	await msg.reply(content=resp, mention_author=False)
