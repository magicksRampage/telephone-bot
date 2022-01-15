import sys

import discord
import time
import telephone.config.core as tpcfg
import telephone.cmd.hello as tphello
import telephone.cmd.wordle as tpwordle
import telephone.utils.core as tputils
import telephone.backend.wordle as beword
from telephone.model.cmd import TpCmd

cmd_map = {
	tpcfg.cmd_hello: tphello.hello,
	tpcfg.cmd_wordle: tpwordle.wordle,
	tpcfg.cmd_wordleguess: tpwordle.guess
}

beword.init_valid_wordles()
beword.init_valid_guesses()

intents = discord.Intents.default()

client = discord.Client(intents=intents)

@client.event
async def on_message(message: discord.Message):
	time_now = int(time.time())

	""" do not interact with our own messages """
	if message.author.id == client.user.id or message.author.bot == True:
		return

	if message.content.startswith(tpcfg.cmd_prefix):
		cmd_obj = TpCmd(
			message=message,
			tokens=message.content.split(" "),
			client=client,
			mentions=message.mentions,
			guild=message.guild
		)

		cmd_fun = cmd_map.get(cmd_obj.cmd)
		if cmd_fun is not None:
			await cmd_fun(cmd_obj)

# find our REST API token
token = tputils.getToken()

if token == None or len(token) == 0:
	tputils.logMsg('Please place your API token in a file called "token", in the same directory as this script.')
	sys.exit(0)

# connect to discord and run indefinitely
client.run(token)