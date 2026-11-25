"""Strategy pattern for physical and magic damage formulas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.models import Ability, DamageType


@dataclass(frozen=True)
class DamageContext:
    """Normalized inputs required by damage calculation strategies."""

    dmg_flat: float
    target_armor: float
    target_phys_res: float
    target_magic_res: float
    res_pen: float = 0.0
    bonus_flat: float = 0.0
    bonus_prof: float = 1.0
    dmg_ability_debuff: float = 0.0


class IDamageStrategy(ABC):
    """Strategy interface for computing final damage."""

    @abstractmethod
    def calculate(self, ctx: DamageContext) -> float:
        """Compute resulting non-negative damage."""


class PhysicalDamageStrategy(IDamageStrategy):
    """Physical damage: flat armor reduction followed by percentage resistance."""

    def calculate(self, ctx: DamageContext) -> float:
        after_armor = max(0.0, ctx.dmg_flat - ctx.target_armor)
        res_factor = max(0.0, 1.0 - ctx.target_phys_res)
        return round(after_armor * res_factor, 2)


class MagicDamageStrategy(IDamageStrategy):
    """
    Magic damage formula:
    dmg_magic = (dmg_flat * max(0, 1 - res_tgt + res_pen) + bonus_flat)
                * max(0, bonus_prof - dmg_ability)
    """

    def calculate(self, ctx: DamageContext) -> float:
        res_multiplier = max(0.0, 1.0 - ctx.target_magic_res + ctx.res_pen)
        prof_multiplier = max(0.0, ctx.bonus_prof - ctx.dmg_ability_debuff)
        total = (ctx.dmg_flat * res_multiplier + ctx.bonus_flat) * prof_multiplier
        return round(max(0.0, total), 2)


def get_damage_strategy(damage_type: DamageType) -> IDamageStrategy:
    """Factory returning the appropriate damage calculation strategy."""
    if damage_type == DamageType.MAGIC:
        return MagicDamageStrategy()
    return PhysicalDamageStrategy()


def build_magic_context(
    attacker_profile,
    target_profile,
    ability: Ability,
) -> DamageContext:
    """Aggregate item, skill, buff bonuses and debuffs for magic damage."""
    item_flat = sum(i.bonus_flat for i in attacker_profile.items)
    buff_flat = sum(e.bonus_flat for e in attacker_profile.effects)
    bonus_flat = item_flat + ability.bonus_flat + buff_flat

    item_prof = sum(i.bonus_prof for i in attacker_profile.items)
    buff_prof = sum(e.bonus_prof for e in attacker_profile.effects)
    bonus_prof = 1.0 + item_prof + ability.bonus_prof + buff_prof

    dmg_ability_debuff = sum(e.debuff_value for e in attacker_profile.effects)

    return DamageContext(
        dmg_flat=ability.base_power,
        target_armor=target_profile.armor + sum(i.bonus_armor for i in target_profile.items),
        target_phys_res=target_profile.phys_resist,
        target_magic_res=target_profile.magic_resist,
        res_pen=ability.res_pen,
        bonus_flat=bonus_flat,
        bonus_prof=bonus_prof,
        dmg_ability_debuff=dmg_ability_debuff,
    )