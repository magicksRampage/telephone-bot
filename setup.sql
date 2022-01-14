CREATE TABLE players (
    id_user bigint NOT NULL,
    wordle_points int NOT NULL DEFAULT '0',
    PRIMARY KEY (id_user)
);

CREATE TABLE wordles (
    word varchar(32) NOT NULL,
    solved int NOT NULL DEFAULT '0',
    PRIMARY KEY (word)
);

CREATE TABLE wordle_guess_history (
    word varchar(32) NOT NULL,
    guess_no int NOT NULL,
    guess varchar(32) NOT NULL DEFAULT '',
    guess_time int NOT NULL,
    id_guesser bigint NOT NULL,

    PRIMARY KEY (word, guess_no)
);