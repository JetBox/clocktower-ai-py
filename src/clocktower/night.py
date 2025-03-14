import warnings
from typing import List

from src.clocktower.status import get_game_status, finish_game
from src.clocktower.storyteller import select_and_kill_player, run_player_conversation_with_storyteller
from src.clocktower.types import Player


def run_night_phase(systemInstruction: str, players: List[Player]) -> None:
	user_input = input('Would you like to [W]ake a player, [K]ill a player or [E]nd the night? ')
	user_input = user_input.upper()

	if user_input == 'E':
		return
	elif user_input == 'K':
		select_and_kill_player(players)

		game_status = get_game_status(players)
		if game_status != 'ongoing':
			finish_game(game_status)
			return
		run_night_phase(systemInstruction, players)
	elif user_input != 'W':
		warnings.warn('You must choose [W], [K] or [E]!')
		run_night_phase(systemInstruction, players)

	player = select_player(players, 'Enter the name of the player that you want to wake up')
	message_for_player = input('What do you want to say to the player? ')

	run_player_conversation_with_storyteller(systemInstruction, player,
											 f"The storyteller wakes you in the night to tell you: \"{message_for_player}\"")

	run_night_phase(systemInstruction, players)
