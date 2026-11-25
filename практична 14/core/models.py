"""Domain models: Item, Ability, StatusEffect, and CharacterProfile."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DamageType(Enum):
    """Supported damage categories."""

    PHYSICAL = "physical"
    MAGIC = "magic"


@dataclass(frozen=True)
class Item:
    """Equipment item granting flat damage, defense, or proficiency bonuses."""

    name: str
    bonus_flat: float = 0.0
    bonus_prof: float = 0.0
    bonus_armor: float = 0.0
    bonus_speed: int = 0


@dataclass(frozen=True)
class Ability:
    """Active skill used during combat (damage or healing)."""

    name: str
    damage_type: DamageType = DamageType.MAGIC
    base_power: float = 15.0
    res_pen: float = 0.0
    bonus_flat: float = 0.0
    bonus_prof: float = 0.0
    is_heal: bool = False


@dataclass(frozen=True)
class StatusEffect:
    """Temporary buff or debuff modifying combat formulas."""

    name: str
    bonus_flat: float = 0.0
    bonus_prof: float = 0.0
    debuff_value: float = 0.0


@dataclass
class CharacterProfile:
    """Base character blueprint loaded from persistence/API or custom creation."""

    name: str
    max_health: float = 100.0
    damage: float = 20.0
    armor: float = 5.0
    phys_resist: float = 0.1
    magic_resist: float = 0.15
    speed: int = 100
    items: list[Item] = field(default_factory=list)
    abilities: list[Ability] = field(default_factory=list)
    effects: list[StatusEffect] = field(default_factory=list)

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def add_ability(self, ability: Ability) -> None:
        self.abilities.append(ability)

    def add_effect(self, effect: StatusEffect) -> None:
        self.effects.append(effect)