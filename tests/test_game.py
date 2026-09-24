"""tests/test_game.py — pytest test suite for the Wordle core game logic."""

import pytest

from game import (
    ABSENT,
    CORRECT,
    MAX_GUESSES,
    PRESENT,
    WORD_LENGTH,
    Game,
    GuessResult,
    evaluate_guess,
)

# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def make_game(secret: str = "crane", extra_words: list[str] | None = None) -> Game:
    """Return a Game with a small word list for testing."""
    words = [secret, "brisk", "speed", "spine", "slate", "abbey", "brace"]
    if extra_words:
        words.extend(extra_words)
    return Game(secret, words)


# ------------------------------------------------------------------ #
# evaluate_guess tests                                                 #
# ------------------------------------------------------------------ #

class TestEvaluateGuess:
    """Tests for the evaluate_guess function."""

    def test_all_correct(self) -> None:
        """Guessing the exact secret word gives all CORRECT statuses."""
        result = evaluate_guess("crane", "crane")
        assert result.statuses == [CORRECT] * WORD_LENGTH

    def test_all_absent(self) -> None:
        """A word with no shared letters gives all ABSENT statuses."""
        result = evaluate_guess("crane", "bitty")
        # none of b,i,t,t,y appear in "crane"
        assert result.statuses == [ABSENT] * WORD_LENGTH

    def test_mix_correct_present_absent(self) -> None:
        """Mixed result: some correct, some present, some absent."""
        result = evaluate_guess("spine", "speed")
        # s->correct, p->correct, e->present, e->absent, d->absent
        assert result.statuses[0] == CORRECT   # s
        assert result.statuses[1] == CORRECT   # p
        assert result.statuses[2] == PRESENT   # e (exists in spine)
        assert result.statuses[3] == ABSENT    # e (only one e remains)
        assert result.statuses[4] == ABSENT    # d

    def test_duplicate_letters_in_guess(self) -> None:
        """Duplicate letters in the guess are handled without overcounting."""
        # secret = "spine", guess = "speed" — already proven above.
        # Extra: secret = "abbey", guess = "keeps"
        # k->absent, e->present (1 e in abbey at index?), e->?, p->absent, s->absent
        # abbey: a=0,b=1,b=2,e=3,y=4  => 'e' appears once at index 3
        # keeps: k=0,e=1,e=2,p=3,s=4
        # Pass1: no position matches
        # remaining from abbey: {a:1, b:2, e:1, y:1}
        # Pass2: k->absent(no k), e->present(consume e), e->absent(no more e),
        #        p->absent, s->absent
        result = evaluate_guess("abbey", "keeps")
        assert result.statuses == [ABSENT, PRESENT, ABSENT, ABSENT, ABSENT]

    def test_duplicate_letters_correct_takes_priority(self) -> None:
        """A correct-position match consumes its letter before PRESENT checks."""
        # secret = "speed", guess = "seedy"
        # s->correct(s@0), p->absent, e->correct(e@2 in secret="speed" is 'e')
        # Wait, "speed"=s,p,e,e,d ; "seedy"=s,e,e,d,y
        # pos0: s==s -> correct
        # pos1: e != p -> remaining {p:1, e:1, d:1}
        # pos2: e == e -> correct, remaining {p:1, d:1}
        # pos3: d == e? No. secret[3]='e', guess[3]='d'
        #        remaining: after pass1 {p:1, e:1, d:1}  wait let me redo
        # "speed": s=0,p=1,e=2,e=3,d=4
        # "seedy": s=0,e=1,e=2,d=3,y=4
        # Pass1 (correct matches): pos0 s==s correct, pos2 e==e correct
        #   remaining (non-matched secret letters): pos1->p, pos3->e, pos4->d
        #   remaining = {p:1, e:1, d:1}
        # Pass2: pos1 guess='e' -> present (consume e), remaining={p:1,d:1}
        #        pos3 guess='d' -> present(consume d from remaining), remaining={p:1}
        #        pos4 guess='y' -> absent
        result = evaluate_guess("speed", "seedy")
        assert result.statuses[0] == CORRECT   # s
        assert result.statuses[1] == PRESENT   # e (present in remaining)
        assert result.statuses[2] == CORRECT   # e
        assert result.statuses[3] == PRESENT   # d (present in remaining)
        assert result.statuses[4] == ABSENT    # y

    def test_guess_result_returns_correct_type(self) -> None:
        """evaluate_guess always returns a GuessResult instance."""
        result = evaluate_guess("crane", "brace")
        assert isinstance(result, GuessResult)
        assert result.guess == "brace"
        assert len(result.statuses) == WORD_LENGTH


# ------------------------------------------------------------------ #
# GuessResult.__str__ tests                                            #
# ------------------------------------------------------------------ #

class TestGuessResultStr:
    """Tests for GuessResult string representation."""

    def test_str_contains_letters_and_symbols(self) -> None:
        """__str__ output contains the guess letters and status symbols."""
        result = GuessResult("crane", [CORRECT, CORRECT, ABSENT, PRESENT, ABSENT])
        output = str(result)
        assert "C" in output
        assert "✓" in output
        assert "~" in output
        assert "✗" in output


# ------------------------------------------------------------------ #
# Game tests                                                           #
# ------------------------------------------------------------------ #

class TestGame:
    """Tests for the Game class."""

    def test_make_guess_valid(self) -> None:
        """A valid guess returns a GuessResult and is added to game.guesses."""
        game = make_game("crane")
        result = game.make_guess("brisk")
        assert isinstance(result, GuessResult)
        assert len(game.guesses) == 1

    def test_make_guess_not_in_word_list_raises(self) -> None:
        """make_guess raises ValueError for words not in the word list."""
        game = make_game("crane")
        with pytest.raises(ValueError, match="not in the word list"):
            game.make_guess("zzzzz")

    def test_make_guess_wrong_length_raises(self) -> None:
        """make_guess raises ValueError when the guess length is wrong."""
        game = make_game("crane")
        with pytest.raises(ValueError):
            game.make_guess("hi")

    def test_invalid_guess_does_not_consume_attempt(self) -> None:
        """An invalid guess must not use up one of the player's attempts."""
        game = make_game("crane")
        try:
            game.make_guess("zzzzz")  # not in word list
        except ValueError:
            pass
        assert len(game.guesses) == 0

    def test_is_won_after_correct_guess(self) -> None:
        """is_won becomes True after guessing the exact secret word."""
        game = make_game("crane")
        game.make_guess("crane")
        assert game.is_won is True

    def test_is_won_false_before_correct_guess(self) -> None:
        """is_won is False before the secret word is guessed."""
        game = make_game("crane")
        game.make_guess("brisk")
        assert game.is_won is False

    def test_is_over_after_win(self) -> None:
        """is_over is True immediately after winning."""
        game = make_game("crane")
        game.make_guess("crane")
        assert game.is_over is True

    def test_is_over_after_max_guesses(self) -> None:
        """is_over becomes True after MAX_GUESSES failed guesses."""
        wrong_words = ["brisk", "speed", "spine", "slate", "abbey", "brace"]
        assert len(wrong_words) == MAX_GUESSES
        game = Game("crane", ["crane"] + wrong_words)
        for word in wrong_words:
            game.make_guess(word)
        assert game.is_over is True
        assert game.is_won is False

    def test_guess_rejected_when_game_is_over(self) -> None:
        """make_guess raises ValueError when the game is already finished."""
        game = make_game("crane")
        game.make_guess("crane")  # win immediately
        with pytest.raises(ValueError, match="already over"):
            game.make_guess("brisk")

    def test_game_str_shows_remaining_slots(self) -> None:
        """__str__ should list empty slots for remaining guesses."""
        game = make_game("crane")
        output = str(game)
        # Before any guess, all 6 rows should be empty slots
        assert output.count("_ ") > 0

    def test_game_str_shows_previous_guesses(self) -> None:
        """__str__ includes previous guess results."""
        game = make_game("crane")
        game.make_guess("brisk")
        output = str(game)
        assert "B" in output or "b" in output.lower()
