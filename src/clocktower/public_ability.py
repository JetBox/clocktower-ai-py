import warnings
from typing import List, Optional

from src.clocktower.players import broadcast_message
from src.clocktower.status import get_game_status, finish_game
from src.clocktower.storyteller import select_and_kill_player
from src.clocktower.types import Player, GameStatus


def use_public_ability(players: List[Player], player: Player, message: str,
					   selected_player: Optional[str] = None) -> None:
	print(f"{player.name} wants to use a public ability: {message}")

	broadcast_message(players, f"{player.name} has used a public ability: {message}", [player.name])
	user_input = input(
		f"{player.name} has tried to use a public ability. Would you like to [S]end a message, [K]ill a player, or [E]nd the game? ")
	user_input = user_input.upper()

	if user_input == 'K':
		select_and_kill_player(players)
		game_status = get_game_status(players)
		if game_status != 'ongoing':
			return finish_game(game_status)
	elif user_input == 'E':
		winning_team = input("What team should win the game? [G]ood or [E]vil? ")
		winning_team = winning_team.upper()

		return finish_game(GameStatus('good-wins' if winning_team == 'G' else 'evil-wins'))
	elif user_input != 'S':
		warnings.warn("You must choose [S], {k], or [E]!")
		return use_public_ability(players, player, message, selected_player)

	message_for_town = input("How would you respond to the town? ")
	broadcast_message(players, message_for_town)
