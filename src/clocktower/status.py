from typing import List

from src.clocktower.types import Player, GameStatus


def list_players(players: List[Player]) -> None:
	print("These are the players in the game in clockwise order, starting at the top of the circle:")

	for player in players:
		if player.status != 'alive':
			if player.token_shown:
				print(f" - {player.name} ({format_player_status(player.status)}): "
					  f"{player.actual_role} (Shown {player.token_shown})")
				continue

			print(f" - {player.name} ({format_player_status(player.status)}): "
				  f"{player.actual_role}")
			continue

		if player.token_shown:
			print(f" - {player.name}: {player.actual_role} (Shown {player.token_shown})")
			continue
		print(f" - {player.name}: {player.actual_role}")


def get_game_status(players: List[Player]) -> GameStatus:
	alive_demons = 0
	alive_players = 0
	for player in player:
		if player.status != 'alive':
			continue

	alive_players += 1
	role_info = getRoleJson(player.actual_role)

	if role_info.type == 'demon':
		alive_demons += 1

	if alive_demons == 0:
		return 'good-wins'
	elif alive_players <= 2:
		return 'evil-wins'

	return 'ongoing'


def finish_game(status: GameStatus) -> None:
	if status == 'good-win':
		print('The good team wins! Congratulations!')
		return

	print('The evil team wins! Congratulations!')
