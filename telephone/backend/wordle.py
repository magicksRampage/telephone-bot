import random
import time
from dataclasses import dataclass
from dataclasses import field

import telephone.backend.core as becore
import telephone.utils.core as tputils

current_wordles = {}


@becore.databaseclass(table="wordles")
@dataclass
class TpWordle:
	id_wordle: int
	word: str = field(init=False, default="")
	solved: int = field(init=False, default=0)

@becore.databaseclass(table="wordle_guess_history")
@dataclass
class TpWordleGuess:
	id_wordle: int
	guess_no: int
	guess: str = field(init=False, default="")
	guess_time: int = field(init=False, default=0)
	id_guesser: int = field(init=False, default=0)


def init_valid_wordles():
	init_word_list("wordlist.txt", "wordle_candidates")
	init_word_list("wordlist.txt", "wordle_valid_guesses")


def init_valid_guesses():
	init_word_list("guesslist.txt", "wordle_valid_guesses")


def init_word_list(f_name, table):

	tputils.logMsg("loading word list")

	words = tuple()
	file = None
	try:
		file = open(f_name, "r")
		f_lines = file.readlines()

		f_lines = map(lambda l: l.rstrip(), f_lines)
		words = tuple(filter(lambda l: len(l) == 5 and l.find("'") == -1, f_lines))

	except IOError:
		print("Could not read {} file.".format(f_name))
	finally:
		if file is not None:
			file.close()

	if len(words) > 0:
		becore.execute_sql_query("REPLACE INTO {table} VALUES {values}".format(
			table=table,
			values=",".join(map(lambda x: "(%s)", words))
		), words)

	tputils.logMsg("done loading word list")


def get_wordle_for_user(id_user: int):
	data = becore.execute_sql_query(
		"SELECT id_wordle FROM wordles WHERE id_wordle NOT IN (SELECT id_wordle FROM wordle_guess_history WHERE id_guesser = %s)",
		(id_user,)
	)

	wordles_taken = list(current_wordles.values())

	for row in data:
		wordle_id = row[0]
		if wordle_id not in wordles_taken:
			return wordle_id

	return generate_new_wordle()


def generate_new_wordle():
	words = becore.execute_sql_query("SELECT word FROM wordle_candidates")
	chosen = random.choice(words)[0]

	wordle_id = becore.execute_sql_query("INSERT INTO wordles (word) VALUES (%s)", (chosen,))

	return wordle_id


def get_last_guess(id_wordle: int):
	data = becore.execute_sql_query("SELECT guess, guess_no FROM wordle_guess_history WHERE id_wordle = %s ORDER BY guess_no DESC LIMIT 1", (id_wordle,))

	if len(data) > 0:
		guess_value = data[0][0]
		guess_no = data[0][1]
		return TpWordleGuess(guess_value, guess_no)
	else:
		return None


def is_valid_guess(guess: str):
	data = becore.execute_sql_query("SELECT * FROM wordle_valid_guesses WHERE word = %s", (guess,))

	return len(data) > 0


def make_guess(guess: str, wordle: TpWordle, guesser: int):
	time_now = int(time.time())
	last_guess = get_last_guess(wordle.id_wordle)

	new_guess_no = last_guess.guess_no + 1 if last_guess is not None else 0

	becore.execute_sql_query(
		"INSERT INTO wordle_guess_history (id_wordle, guess_no, guess, guess_time, id_guesser) VALUES (%s, %s, %s, %s, %s)",
		(wordle.id_wordle, new_guess_no, guess, time_now, guesser)
	)

	new_guess = TpWordleGuess(id_wordle=wordle.id_wordle, guess_no=new_guess_no)

	return new_guess
