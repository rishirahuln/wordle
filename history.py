"""history.py — Persistent game history and statistics for the Wordle clone."""

import json
import os

HISTORY_FILE = "history.jsonl"


class GameHistory:
    """Loads, stores, and saves the player's game history.

    History is persisted in ``history.json`` as a JSON array. Each entry is a
    dictionary with the keys:

    - ``won``      (bool)  – whether the player won the game
    - ``attempts`` (int)   – number of guesses used
    - ``word``     (str)   – the secret word for that game

    If ``history.json`` does not exist it is created automatically on the first
    save.

    Attributes:
        games: List of completed game records (dicts), oldest first.
    """

    def __init__(self) -> None:
        """Initialise GameHistory by loading data from ``history.json``.

        If the file does not exist, starts with an empty history.
        """
        self.games: list[dict] = []
        self._load()

    def _load(self) -> None:
        """Read history from disk; silently start fresh if the file is absent.

        The file is stored in JSON Lines format: one JSON object per line.
        Blank lines are skipped silently.
        """
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.games.append(json.loads(line))

    def save(self) -> None:
        """Append the most recent game record to ``history.json``.

        Opens the file in append mode so only the new record is written,
        regardless of how many previous records exist.
        """
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.games[-1]) + "\n")

    def record_and_save(self, won: bool, attempts: int, word: str) -> None:
        """Add a completed game to the history and save it.

        Args:
            won:      True if the player guessed the word correctly.
            attempts: Number of guesses the player used.
            word:     The secret word for the completed game.
        """
        self.games.append({"won": won, "attempts": attempts, "word": word})

        self.save()

    # ------------------------------------------------------------------ #
    # Statistics properties                                                #
    # ------------------------------------------------------------------ #

    @property
    def total_games(self) -> int:
        """Total number of completed games."""
        return len(self.games)

    @property
    def total_wins(self) -> int:
        """Total number of games won."""
        return sum(1 for g in self.games if g["won"])

    @property
    def win_percentage(self) -> float:
        """Percentage of games won, or 0.0 if no games have been played."""
        if self.total_games == 0:
            return 0.0
        return round(self.total_wins / self.total_games * 100, 1)

    @property
    def current_streak(self) -> int:
        """Number of consecutive wins ending with the most recent game.

        Walk backwards through the history and count wins until the first
        loss (or the beginning of the list) is reached.
        """
        streak = 0
        for game in reversed(self.games):
            if game["won"]:
                streak += 1
            else:
                break
        return streak

    @property
    def best_streak(self) -> int:
        """Longest consecutive winning streak across all recorded games."""
        best = 0
        current = 0
        for game in self.games:
            if game["won"]:
                current += 1
                if current > best:
                    best = current
            else:
                current = 0
        return best
