"""GameConfig and persistence stub simulating the DATA layer."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from core.character import Character
from core.models import Ability, CharacterProfile, DamageType, Item


@dataclass
class GameConfig:
    """Serializable configuration and saved state of a battle session."""

    characters: list[Character] = field(default_factory=list)
    current_turn_number: int = 0
    history_log: list[str] = field(default_factory=list)


class PersistenceStub:
    """In-memory stub standing in for the Persistence (DATA) layer."""

    def __init__(self) -> None:
        self._saved_slots: dict[str, GameConfig] = {}
        self._roster_catalog: dict[str, CharacterProfile] = {
            "knight": CharacterProfile(
                name="Knight",
                max_health=120.0,
                damage=24.0,
                armor=8.0,
                phys_resist=0.15,
                magic_resist=0.10,
                speed=100,
                items=[Item("Iron Blade", bonus_flat=4.0, bonus_armor=2.0)],
                abilities=[
                    Ability("Shield Bash", damage_type=DamageType.PHYSICAL, base_power=28.0),
                ],
            ),
            "mage": CharacterProfile(
                name="Mage",
                max_health=90.0,
                damage=14.0,
                armor=3.0,
                phys_resist=0.05,
                magic_resist=0.25,
                speed=150,
                items=[Item("Arcane Staff", bonus_flat=5.0, bonus_prof=0.15)],
                abilities=[
                    Ability(
                        "Arcane Bolt",
                        damage_type=DamageType.MAGIC,
                        base_power=30.0,
                        res_pen=0.10,
                    ),
                    Ability("Mend", base_power=20.0, is_heal=True),
                ],
            ),
            "assassin": CharacterProfile(
                name="Assassin",
                max_health=85.0,
                damage=20.0,
                armor=4.0,
                phys_resist=0.10,
                magic_resist=0.10,
                speed=200,
                abilities=[
                    Ability("Shadow Strike", damage_type=DamageType.PHYSICAL, base_power=25.0),
                ],
            ),
        }

    def fetch_character_profile(self, key: str) -> CharacterProfile:
        profile = self._roster_catalog.get(key.lower())
        if profile is None:
            raise KeyError(f"Character profile '{key}' not found in persistence stub.")
        return deepcopy(profile)

    def register_character_profile(self, key: str, profile: CharacterProfile) -> None:
        self._roster_catalog[key.lower()] = deepcopy(profile)

    def save_config(self, slot: str, config: GameConfig) -> None:
        self._saved_slots[slot] = deepcopy(config)

    def load_config(self, slot: str) -> GameConfig:
        if slot not in self._saved_slots:
            raise KeyError(f"Save slot '{slot}' does not exist.")
        return deepcopy(self._saved_slots[slot])