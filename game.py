"""game.py — Core game logic for the Wordle clone.

Contains constants, GuessResult, evaluate_guess, and the Game class.
"""

WORD_LENGTH = 5
MAX_GUESSES = 6

# Status values for each letter in a guess
CORRECT = "correct"   # Right letter, right position
PRESENT = "present"   # Right letter, wrong position
ABSENT = "absent"     # Letter not in the word (or already accounted for)


class GuessResult:
    """Represents the outcome of a single guess.

    Each letter in the guessed word is assigned one of three statuses:
      - 'correct': letter is in the right position
      - 'present': letter exists in the secret but is in the wrong position
      - 'absent':  letter does not appear (or is already accounted for)
    """

    def __init__(self, guess: str, statuses: list[str]) -> None:
        """Initialise a GuessResult.

        Args:
            guess:    The five-letter word that was guessed.
            statuses: A list of WORD_LENGTH status strings, one per letter.
        """
        self.guess = guess
        self.statuses = statuses

    def __str__(self) -> str:
        """Return a two-line string showing the guess and its per-letter status.

        Example:
            S  P  E  E  D
            ✓  ✓  ~  ✗  ✗
        """
        status_symbols = {CORRECT: "✓", PRESENT: "~", ABSENT: "✗"}
        letters_row = "  ".join(letter.upper() for letter in self.guess)
        symbols_row = "  ".join(status_symbols[s] for s in self.statuses)
        return f"{letters_row}\n{symbols_row}"


def evaluate_guess(secret: str, guess: str) -> GuessResult:
    """Compare *guess* against *secret* and return a GuessResult.

    The evaluation follows the standard Wordle rules:

    1. First, mark all letters that are in the correct position as CORRECT.
       Keep a count of the remaining (unmatched) letters in the secret word.
    2. Then, for each non-correct position, check whether the guessed letter
       appears in the remaining pool.  If it does, mark it PRESENT and reduce
       the pool count for that letter so it cannot be claimed again.
       Otherwise mark it ABSENT.

    This two-pass approach correctly handles duplicate letters.

    Example:
        secret = "spine", guess = "speed"
        S -> correct   (position 0 matches)
        P -> correct   (position 1 matches)
        E -> present   (position 2: 'e' is in secret but not at index 2)
        E -> absent    (position 3: the only 'e' in secret is already consumed)
        D -> absent    (position 4: 'd' is not in secret)

    Args:
        secret: The five-letter secret word.
        guess:  The five-letter guessed word.

    Returns:
        A GuessResult describing the status of each letter.
    """
    statuses: list[str] = [ABSENT] * WORD_LENGTH

    # Count unmatched letters in the secret (used in the second pass).
    remaining: dict[str, int] = {}

    # --- Pass 1: find correct-position matches ---
    for i in range(WORD_LENGTH):
        if guess[i] == secret[i]:
            statuses[i] = CORRECT
        else:
            # This secret letter is still "available" for a PRESENT match.
            remaining[secret[i]] = remaining.get(secret[i], 0) + 1

    # --- Pass 2: find present (wrong-position) matches ---
    for i in range(WORD_LENGTH):
        if statuses[i] == CORRECT:
            continue  # Already handled.
        letter = guess[i]
        if remaining.get(letter, 0) > 0:
            statuses[i] = PRESENT
            remaining[letter] -= 1
        # else: leave as ABSENT (already set)

    return GuessResult(guess, statuses)


class Game:
    """Manages the state of a single Wordle game session.

    Attributes:
        secret:       The word the player must guess.
        word_list:    The full list of valid words (used to validate guesses).
        guesses:      Ordered list of GuessResult objects for guesses so far.
    """

    def __init__(self, secret: str, word_list: list[str]) -> None:
        """Initialise a new Game.

        Args:
            secret:    The five-letter word the player must guess.
            word_list: The complete list of valid five-letter words.
        """
        self.secret: str = secret
        self.word_list: list[str] = word_list
        self.guesses: list[GuessResult] = []

    @property
    def is_won(self) -> bool:
        """Return True if the player's last guess was the correct word."""
        if not self.guesses:
            return False
        last_statuses = self.guesses[-1].statuses
        return all(s == CORRECT for s in last_statuses)

    @property
    def is_over(self) -> bool:
        """Return True if the game has ended (either won or no guesses left)."""
        return self.is_won or len(self.guesses) >= MAX_GUESSES

    def make_guess(self, word: str) -> GuessResult:
        """Attempt a guess and return its GuessResult.

        Invalid guesses raise a ValueError and do NOT consume an attempt.

        Args:
            word: The word the player wants to guess (must be lowercase).

        Returns:
            A GuessResult for the submitted guess.

        Raises:
            ValueError: If the game is already over, the word length is wrong,
                        or the word is not in the word list.
        """
        if self.is_over:
            raise ValueError("The game is already over.")
        if len(word) != WORD_LENGTH:
            raise ValueError(
                f"Guess must be exactly {WORD_LENGTH} letters. "
                f"'{word}' has {len(word)}."
            )
        if word not in self.word_list:
            raise ValueError(f"'{word}' is not in the word list.")

        result = evaluate_guess(self.secret, word)
        self.guesses.append(result)
        return result

    def __str__(self) -> str:
        """Render the complete game board.

        Shows each past guess with its result, then empty rows for the
        remaining attempts.

        Example board with 2 guesses used out of 6:

            S  P  E  E  D
            ✓  ✓  ~  ✗  ✗

            B  R  A  V  E
            ~  ✗  ✗  ✗  ~

            _ _ _ _ _   (guess 3)
            _ _ _ _ _   (guess 4)
            _ _ _ _ _   (guess 5)
            _ _ _ _ _   (guess 6)
        """
        rows: list[str] = []
        for result in self.guesses:
            rows.append(str(result))
            rows.append("")  # blank line between guesses

        remaining = MAX_GUESSES - len(self.guesses)
        for i in range(remaining):
            guess_num = len(self.guesses) + i + 1
            rows.append(f"_  _  _  _  _   (guess {guess_num})")

        return "\n".join(rows)
