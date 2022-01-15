CREATE OR REPLACE TABLE players (
    id_user bigint NOT NULL,
    wordle_points int NOT NULL DEFAULT '0',
    PRIMARY KEY (id_user)
);

CREATE OR REPLACE TABLE wordle_candidates (
    word varchar(32) NOT NULL,
    PRIMARY KEY (word)
);

CREATE OR REPLACE TABLE wordle_valid_guesses (
    word varchar(32) NOT NULL,
    PRIMARY KEY (word)
);

CREATE OR REPLACE TABLE wordles (
    id_wordle int NOT NULL AUTO_INCREMENT,
    word varchar(32) NOT NULL,
    solved int NOT NULL DEFAULT '0',
    PRIMARY KEY (id_wordle)
);

CREATE OR REPLACE TABLE wordle_guess_history (
    id_wordle int NOT NULL,
    guess_no int NOT NULL,
    guess varchar(32) NOT NULL DEFAULT '',
    guess_time int NOT NULL,
    id_guesser bigint NOT NULL,

    FOREIGN KEY (id_wordle)
		REFERENCES wordles(id_wordle)
		ON DELETE CASCADE
);