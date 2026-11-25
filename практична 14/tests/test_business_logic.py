"""Unit tests covering damage formulas, speed turn order, history, save/load, and loading units."""

import unittest

from core.combat import DamageContext, MagicDamageStrategy, PhysicalDamageStrategy
from core.game import Game
from core.models import Ability, CharacterProfile, DamageType, Item, StatusEffect
from core.turn import ActionId


class TestBusinessLogic(unittest.TestCase):
    """Test suite for Practical 14 core mechanics."""

    def test_physical_damage_formula_blocks_and_reduces(self) -> None:
        strategy = PhysicalDamageStrategy()
        # Armor completely blocks incoming damage
        blocked = strategy.calculate(
            DamageContext(dmg_flat=8.0, target_armor=10.0, target_phys_res=0.2, target_magic_res=0.0)
        )
        self.assertEqual(blocked, 0.0)

        # (25 - 10) * (1 - 0.2) = 12.0
        pierced = strategy.calculate(
            DamageContext(dmg_flat=25.0, target_armor=10.0, target_phys_res=0.2, target_magic_res=0.0)
        )
        self.assertEqual(pierced, 12.0)

    def test_magic_damage_formula_with_penetration_bonuses_and_debuffs(self) -> None:
        strategy = MagicDamageStrategy()
        # (30 * (1 - 0.2 + 0.1) + 5) * (1.2 - 0.2) = (27 + 5) * 1.0 = 32.0
        dmg = strategy.calculate(
            DamageContext(
                dmg_flat=30.0,
                target_armor=99.0,  # Magic ignores flat armor
                target_phys_res=0.5,
                target_magic_res=0.2,
                res_pen=0.1,
                bonus_flat=5.0,
                bonus_prof=1.2,
                dmg_ability_debuff=0.2,
            )
        )
        self.assertEqual(dmg, 32.0)

    def test_speed_based_turn_order_gives_extra_action_for_speed_200(self) -> None:
        game = Game()
        cfg = game.setup_game(["knight", "mage", "assassin"])
        game.start_game(cfg)

        # Assassin=200 (2 actions), Mage=150 (1 action), Knight=100 (1 action)
        order = game.begin_next_turn()
        self.assertEqual(order, ["Assassin", "Mage", "Assassin", "Knight"])

    def test_turn_history_save_load_and_dynamic_character_loading(self) -> None:
        game = Game()
        cfg = game.setup_game(["knight", "mage"])
        game.start_game(cfg)

        # Load a brand new character dynamically
        custom = CharacterProfile(
            name="Paladin",
            max_health=130.0,
            damage=18.0,
            armor=10.0,
            speed=110,
            items=[Item("Sun Relic", bonus_flat=3.0)],
            effects=[StatusEffect("Weakened", debuff_value=0.1)],
            abilities=[Ability("Smite", damage_type=DamageType.MAGIC, base_power=25.0)],
        )
        game.load_character(custom)
        self.assertEqual(len(game.config.characters), 3)

        game.begin_next_turn()
        game.perform_action(ActionId.ABILITY, "Mage", "Knight", ability_index=0)
        game.perform_action(ActionId.ATTACK, "Knight", "Mage")

        self.assertEqual(len(game.get_history()), 2)
        knight_hp_before_save = game.get_character("Knight").current_hp

        # Save state, mutate further, then restore state
        game.save_state("slot1")
        game.perform_action(ActionId.ATTACK, "Paladin", "Knight")
        self.assertLess(game.get_character("Knight").current_hp, knight_hp_before_save)

        game.load_state("slot1")
        self.assertEqual(game.get_character("Knight").current_hp, knight_hp_before_save)
        self.assertEqual(len(game.get_history()), 2)


if __name__ == "__main__":
    unittest.main()