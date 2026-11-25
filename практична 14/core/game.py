"""Central Game facade orchestrating turn-based flow, history, and save/load."""

from __future__ import annotations

from core.character import Character
from core.config import GameConfig, PersistenceStub
from core.models import CharacterProfile
from core.turn import ActionId, Turn, TurnActionRecord


class Game:
    """Facade encapsulating the core game loop without UI dependencies."""

    def __init__(self, persistence: PersistenceStub | None = None) -> None:
        self._persistence = persistence or PersistenceStub()
        self.config: GameConfig = GameConfig()
        self.turns: list[Turn] = []
        self._active_turn: Turn | None = None

    def setup_game(self, roster_keys: list[str] | None = None) -> GameConfig:
        """Create an initial GameConfig by loading character profiles."""
        keys = roster_keys or ["knight", "mage"]
        characters = [
            Character(self._persistence.fetch_character_profile(key)) for key in keys
        ]
        self.config = GameConfig(characters=characters, current_turn_number=0, history_log=[])
        return self.config

    def start_game(self, config: GameConfig) -> None:
        """Start or resume a game session from a GameConfig."""
        self.config = config
        self.turns = []
        self._active_turn = None

    def load_character(self, profile: CharacterProfile) -> Character:
        """Load a new custom character into the current game session."""
        character = Character(profile)
        self.config.characters.append(character)
        return character

    def load_character_by_key(self, key: str) -> Character:
        """Load a catalog character from persistence stub into the session."""
        profile = self._persistence.fetch_character_profile(key)
        return self.load_character(profile)

    def get_character(self, name: str) -> Character:
        for char in self.config.characters:
            if char.name.lower() == name.lower():
                return char
        raise KeyError(f"Character '{name}' is not in the current game.")

    def begin_next_turn(self) -> list[str]:
        """Start a new Turn and return the speed-sorted action order."""
        self.config.current_turn_number += 1
        turn = Turn(
            turn_number=self.config.current_turn_number,
            participants=self.config.characters,
        )
        order = turn.begin_turn()
        self.turns.append(turn)
        self._active_turn = turn
        return order

    def perform_action(
        self,
        action_id: ActionId,
        actor_name: str,
        target_name: str,
        ability_index: int = 0,
    ) -> TurnActionRecord:
        """Perform a combat action inside the active turn and record it."""
        if self._active_turn is None:
            self.begin_next_turn()
        assert self._active_turn is not None

        actor = self.get_character(actor_name)
        target = self.get_character(target_name)
        record = self._active_turn.act(action_id, actor, target, ability_index=ability_index)
        summary = (
            f"Turn {record.turn_number}: {record.actor} -> {record.target} "
            f"[{record.detail}] value={record.value} (target HP={record.target_hp_after})"
        )
        self.config.history_log.append(summary)
        return record

    def get_history(self) -> list[str]:
        """Return full battle action history."""
        return list(self.config.history_log)

    def get_statuses(self) -> list[dict[str, object]]:
        """Return status dictionaries for all characters (UI-friendly payload)."""
        return [char.check_status() for char in self.config.characters]

    def save_state(self, slot: str = "autosave") -> None:
        """Persist current GameConfig into the persistence stub."""
        self._persistence.save_config(slot, self.config)

    def load_state(self, slot: str = "autosave") -> GameConfig:
        """Restore GameConfig from persistence stub and reactivate it."""
        restored = self._persistence.load_config(slot)
        self.start_game(restored)
        return restored