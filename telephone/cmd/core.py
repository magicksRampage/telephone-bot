from telephone.model.cmd import TpCmd
import telephone.utils.frontend as feutils
import telephone.config.core as tpcfg

async def help(cmd: TpCmd):
	await feutils.respond("**Wordlephone:**\nUse **{cmd_wordle}** to request a new wordle. Then use **{cmd_guess}** to guess the wordle.".format(
		cmd_wordle=tpcfg.cmd_wordle,
		cmd_guess=tpcfg.cmd_wordleguess
	), cmd.message)
