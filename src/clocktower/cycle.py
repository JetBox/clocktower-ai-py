from typing import List

from src.clocktower.night import run_night_phase
from src.clocktower.status import get_game_status, finish_game, list_players
from src.clocktower.types import Player

def run_day_night_cycle(systemInstruction: str, players: List[Player], day_count=1) -> None:
	game_status = get_game_status(players)
	if game_status != 'ongoing':
		return finish_game(game_status)

	print("It is now the night. All players close their eyes.")

	list_players(players)

	run_night_phase(systemInstruction, players)

	user_input = input(
		"The night phase is now over. What would you like to say to the town as they wake in the morning? ")

	broadcast_message(players,
					  f"{user_input}. {'If you died and you are the Klutz or claiming to be the Klutz, then you need to announce this now and choose a player soon. If your role gained information during the night, or if you are bluffing a role that gains information during the night, you can share that now if you wish. Remember to maintain a consistent alibi and avoid contradicting yourself. ' if day_count > 1 else ''}")
	
	run_discussion_phase(systemInstruction, players)
	
	run_day_night_cycle(systemInstruction, players, day_count + 1)
