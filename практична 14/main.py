
"""Demo script exercising Practical 14 core business logic without UI coupling."""

from core.game import Game
from core.models import Ability, CharacterProfile, DamageType
from core.turn import ActionId


def main() -> None:
    game = Game()
    config = game.setup_game(["knight", "mage", "assassin"])
    game.start_game(config)

    # Load an additional character dynamically
    game.load_character(
        CharacterProfile(
            name="Cleric",
            max_health=95.0,
            damage=12.0,
            armor=5.0,
            magic_resist=0.3,
            speed=120,
            abilities=[Ability("Holy Light", base_power=22.0, is_heal=True)],
        )
    )

    order = game.begin_next_turn()
    print("=== TURN 1 ACTION ORDER (BY SPEED) ===")
    print(" -> ".join(order))

    game.perform_action(ActionId.ATTACK, "Assassin", "Mage")
    game.perform_action(ActionId.ABILITY, "Mage", "Knight", ability_index=0)
    game.perform_action(ActionId.ABILITY, "Cleric", "Mage", ability_index=0)
    game.perform_action(ActionId.ATTACK, "Knight", "Assassin")

    game.save_state("turn_1_checkpoint")

    print("\n=== STATUSES AFTER TURN 1 ===")
    for status in game.get_statuses():
        print(status)

    print("\n=== BATTLE HISTORY ===")
    for entry in game.get_history():
        print(entry)

    # Mutate state and verify restore from saved checkpoint
    game.perform_action(ActionId.ATTACK, "Assassin", "Knight")
    print(f"\nKnight HP after extra hit: {game.get_character('Knight').current_hp}")
    game.load_state("turn_1_checkpoint")
    print(f"Knight HP after restoring checkpoint: {game.get_character('Knight').current_hp}")


if __name__ == "__main__":
    main()