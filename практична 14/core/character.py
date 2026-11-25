"""Runtime combatant entity wrapping CharacterProfile."""

from __future__ import annotations

from core.combat import (
    DamageContext,
    build_magic_context,
    get_damage_strategy,
)
from core.models import CharacterProfile, DamageType


class Character:
    """Active battle unit executing attacks, heals, and abilities."""

    def __init__(self, profile: CharacterProfile, current_hp: float | None = None) -> None:
        self.profile = profile
        self.current_hp: float = (
            profile.max_health if current_hp is None else min(current_hp, profile.max_health)
        )

    @property
    def name(self) -> str:
        return self.profile.name

    @property
    def speed(self) -> int:
        return self.profile.speed + sum(i.bonus_speed for i in self.profile.items)

    @property
    def total_armor(self) -> float:
        return self.profile.armor + sum(i.bonus_armor for i in self.profile.items)

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0.0

    def receive_damage(self, amount: float) -> float:
        applied = max(0.0, round(amount, 2))
        self.current_hp = round(max(0.0, self.current_hp - applied), 2)
        return applied

    def attack(self, target: Character) -> float:
        """Execute a standard physical attack against target."""
        bonus_flat = sum(i.bonus_flat for i in self.profile.items) + sum(
            e.bonus_flat for e in self.profile.effects
        )
        ctx = DamageContext(
            dmg_flat=self.profile.damage + bonus_flat,
            target_armor=target.total_armor,
            target_phys_res=target.profile.phys_resist,
            target_magic_res=target.profile.magic_resist,
        )
        damage = get_damage_strategy(DamageType.PHYSICAL).calculate(ctx)
        return target.receive_damage(damage)

    def heal(self, target: Character, amount: float = 15.0) -> float:
        """Restore HP to target up to its max_health."""
        if not target.is_alive:
            return 0.0
        before = target.current_hp
        target.current_hp = round(min(target.profile.max_health, target.current_hp + max(0.0, amount)), 2)
        return round(target.current_hp - before, 2)

    def action(self, ability_index: int, target: Character) -> tuple[str, float]:
        """Use an ability from profile.abilities by index."""
        if ability_index < 0 or ability_index >= len(self.profile.abilities):
            raise IndexError(f"Ability index {ability_index} out of range for {self.name}")

        ability = self.profile.abilities[ability_index]
        if ability.is_heal:
            healed = self.heal(target, ability.base_power)
            return ability.name, healed

        if ability.damage_type == DamageType.MAGIC:
            ctx = build_magic_context(self.profile, target.profile, ability)
        else:
            ctx = DamageContext(
                dmg_flat=ability.base_power + ability.bonus_flat,
                target_armor=target.total_armor,
                target_phys_res=target.profile.phys_resist,
                target_magic_res=target.profile.magic_resist,
            )

        dmg = get_damage_strategy(ability.damage_type).calculate(ctx)
        return ability.name, target.receive_damage(dmg)

    def check_status(self) -> dict[str, object]:
        """Return a serializable snapshot of the character's current combat status."""
        return {
            "name": self.name,
            "hp": self.current_hp,
            "max_hp": self.profile.max_health,
            "alive": self.is_alive,
            "speed": self.speed,
            "armor": self.total_armor,
            "abilities": [a.name for a in self.profile.abilities],
        }