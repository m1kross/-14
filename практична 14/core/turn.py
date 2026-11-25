"""Turn encapsulation: speed-based action ordering and combat history records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from core.character import Character


class ActionId(Enum):
    """Supported actions within a turn."""

    ATTACK = "attack"
    HEAL = "heal"
    ABILITY = "ability"


@dataclass(frozen=True)
class TurnActionRecord:
    """Single logged action inside a turn."""

    turn_number: int
    action_id: ActionId
    actor: str
    target: str
    detail: str
    value: float
    target_hp_after: float


@dataclass
class Turn:
    """Represents one round of the turn-based battle with speed-ordered queue."""

    turn_number: int
    participants: list[Character]
    action_queue: list[Character] = field(default_factory=list)
    records: list[TurnActionRecord] = field(default_factory=list)

    def begin_turn(self) -> list[str]:
        """
        Compute turn action order based on character speed:
        - speed 100 -> 1 action
        - speed 150 -> acts before 100
        - speed 200 -> acts first and gets an extra action mid-turn
        """
        slots: list[tuple[int, int, int, Character]] = []
        for idx, char in enumerate(self.participants):
            if not char.is_alive:
                continue
            action_count = max(1, char.speed // 100)
            for step in range(action_count):
                priority = char.speed - step * 100
                # Higher priority first, then higher base speed, then original roster order
                slots.append((priority, char.speed, -idx, char))

        slots.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        self.action_queue = [item[3] for item in slots]
        return [c.name for c in self.action_queue]

    def act(
        self,
        action_id: ActionId,
        actor: Character,
        target: Character,
        ability_index: int = 0,
    ) -> TurnActionRecord:
        """Execute an action from actor on target and record it in turn history."""
        if not actor.is_alive:
            raise ValueError(f"Character '{actor.name}' is defeated and cannot act.")

        if action_id == ActionId.ATTACK:
            value = actor.attack(target)
            detail = "Basic physical attack"
        elif action_id == ActionId.HEAL:
            value = actor.heal(target)
            detail = "Standard heal"
        elif action_id == ActionId.ABILITY:
            ability_name, value = actor.action(ability_index, target)
            detail = f"Ability '{ability_name}'"
        else:
            raise ValueError(f"Unsupported action: {action_id}")

        record = TurnActionRecord(
            turn_number=self.turn_number,
            action_id=action_id,
            actor=actor.name,
            target=target.name,
            detail=detail,
            value=value,
            target_hp_after=target.current_hp,
        )
        self.records.append(record)
        return record