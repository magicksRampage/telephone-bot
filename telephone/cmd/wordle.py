import time

from telephone.backend.player import TpPlayer
from telephone.model.cmd import TpCmd
import telephone.backend.wordle as beword
import telephone.utils.frontend as feutils
import telephone.config.wordle as cfgword
import telephone.config.core as tpcfg


async def wordle(cmd: TpCmd):
	player = TpPlayer(cmd.message.author.id)
	id_wordle = beword.current_wordles.get(player.id_user)
	if id_wordle is None:
		id_wordle = beword.get_wordle_for_user(player.id_user)
		beword.current_wordles[player.id_user] = id_wordle
	last_guess = beword.get_last_guess(id_wordle)
	wordle = beword.TpWordle(id_wordle)

	if last_guess is not None:
		diff = gen_diff_for_wordle_guess(wordle.word, last_guess.guess)
		resp = "The last guess for this wordle was:\n{guess}\n{diff}\nMake a new guess.".format(
			guess=last_guess.guess,
			diff=diff_to_string(diff)
		)
	else:
		resp = "New Wordle. Make an initial guess."
	await feutils.respond(resp, cmd.message)


async def guess(cmd: TpCmd):
	player = TpPlayer(cmd.message.author.id)

	id_wordle = beword.current_wordles.get(player.id_user)
	if id_wordle is None:
		return await feutils.respond("Use {cmd} to get a new wordle first.".format(cmd=tpcfg.cmd_wordle), cmd.message)

	if cmd.tokens_count < 2:
		return await feutils.respond("Please specify a guess.", cmd.message)

	guess: str = cmd.tokens[1]
	guess = guess.strip().lower()

	if len(guess) != 5:
		return await feutils.respond("Invalid guess. Needs to be length 5.", cmd.message)

	if not beword.is_valid_guess(guess):
		return await feutils.respond("Invalid guess. Word is not in word list.", cmd.message)

	wordle = beword.TpWordle(id_wordle)
	beword.make_guess(guess=guess, wordle=wordle, guesser=player.id_user)
	diff = gen_diff_for_wordle_guess(word=wordle.word, guess=guess)

	resp = "{guess}\n{diff}".format(guess=guess, diff=diff_to_string(diff))

	beword.current_wordles[player.id_user] = None

	if wordle.word == guess:
		player.wordle_points += 5
		player.persist()

		wordle.solved = 1
		wordle.persist()

		resp += "\n\n"
		resp += "Congratulations, you solved the wordle!"

	return await feutils.respond(resp, cmd.message)


def gen_diff_for_wordle_guess(word: str, guess: str):
	diff = list(map(lambda _: 0, guess))
	word_without_guess = str(word)

	for i_guess in range(len(guess)):
		letter_guess = guess[i_guess]
		if letter_guess == word[i_guess]:
			word_without_guess = word_without_guess[:i_guess]
			if len(word) > i_guess + 1:
				word_without_guess += word[i_guess+1:]
			diff[i_guess] = 2

	for i_guess in filter(lambda i: diff[i] != 2, range(len(guess))):
		letter_guess = guess[i_guess]
		if word_without_guess.find(letter_guess) > -1:
			diff[i_guess] = 1

	return diff


def diff_to_string(diff: list[int]):
	return "".join(map(lambda d: cfgword.wordle_diff_to_emoji.get(d), diff))
