"""wordle.py — CLI entry point for the Wordle clone.

Run this file to start a game:

    python wordle.py
"""

import os
import random

from game import MAX_GUESSES, Game
from history import GameHistory

WORDS_FILE = "words.txt"


def load_words(filepath: str) -> list[str]:
    """Load words from *filepath* and validate each entry.

    Each line in the file should be a single lowercase five-letter word.
    Blank lines are skipped silently.

    Args:
        filepath: Path to the plain-text word list.

    Returns:
        A list of validated five-letter words.

    Raises:
        FileNotFoundError: If *filepath* does not exist.
        ValueError:        If any word in the file is not exactly five letters.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Word list not found: '{filepath}'")

    words: list[str] = []
    with open(filepath, encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            word = raw_line.strip().lower()
            if not word:
                continue  # Skip blank lines
            if len(word) != 5:
                raise ValueError(
                    f"Invalid word on line {line_number}: "
                    f"'{word}' is {len(word)} letters (expected 5)."
                )
            words.append(word)

    return words


def display_board(game: Game) -> None:
    """Print a separator line followed by the current game board."""
    print("\n" + "=" * 30)
    print(str(game))
    print("=" * 30)


def display_stats(history: GameHistory) -> None:
    """Print the player's cumulative statistics."""
    print("\n📊  Your Statistics")
    print("-" * 30)
    print(f"  Games played : {history.total_games}")
    print(f"  Wins         : {history.total_wins}")
    print(f"  Win %        : {history.win_percentage}%")
    print(f"  Current streak: {history.current_streak}")
    print(f"  Best streak  : {history.best_streak}")
    print("-" * 30)


def main() -> None:
    """Run a complete Wordle game from the command line."""
    # ------------------------------------------------------------------ #
    # Setup                                                                #
    # ------------------------------------------------------------------ #
    word_list = load_words(WORDS_FILE)
    secret = random.choice(word_list)

    game = Game(secret, word_list)
    history = GameHistory()

    print("╔══════════════════════════════╗")
    print("║         W O R D L E          ║")
    print("╚══════════════════════════════╝")
    print(f"Guess the {5}-letter word!  You have {MAX_GUESSES} attempts.")
    print("  ✓ = correct position   ~ = wrong position   ✗ = not in word\n")

    # ------------------------------------------------------------------ #
    # Main game loop                                                       #
    # ------------------------------------------------------------------ #
    while not game.is_over:
        display_board(game)

        guesses_used = len(game.guesses)
        guesses_left = MAX_GUESSES - guesses_used
        print(
            f"\nAttempt {guesses_used + 1}/{MAX_GUESSES}  "
            f"({guesses_left} remaining)"
        )

        raw_input = input("Your guess: ").strip().lower()

        if not raw_input:
            print("  ⚠  Please enter a word.")
            continue

        try:
            game.make_guess(raw_input)
        except ValueError as err:
            # Invalid guess — print the error but do NOT consume an attempt.
            print(f"  ⚠  {err}")
            continue

    # ------------------------------------------------------------------ #
    # Game-over screen                                                     #
    # ------------------------------------------------------------------ #
    display_board(game)

    if game.is_won:
        attempts = len(game.guesses)
        print(f"\n🎉  You got it in {attempts}/{MAX_GUESSES}!")
    else:
        print(f"\n😔  Hard luck!  The word was: {secret.upper()}")

    # ------------------------------------------------------------------ #
    # Persist and display stats                                            #
    # ------------------------------------------------------------------ #
    history.record_and_save(
        won=game.is_won,
        attempts=len(game.guesses),
        word=secret,
    )
    display_stats(history)


if __name__ == "__main__":
    main()
