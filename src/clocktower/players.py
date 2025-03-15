import json
import math
import random
import warnings
from typing import List, Optional

from google.ai.generativelanguage_v1 import Part
from google.generativeai.types import ContentDict

from src.clocktower.types import Player, PlayerResponse, PlayerStatus
from src.services.constants import GENERATED_DATA_DIRECTORY


def send_message_to_player(systemInstruction: str, player: Player, message: str,
						   allowed_actions: List[str]) -> PlayerResponse:
	res = generate_response(systemInstruction, player.chat_history, message, allowed_actions)

	player.chat_history.append(ContentDict(role='user', parts=[Part(message)]))
	player.chat_history.append(ContentDict(role='model', parts=[Part(json.dumps(res))]))
	player.action_history.append(res.action)

	with open(f"{GENERATED_DATA_DIRECTORY}/{player.name}.csv", "a") as file:
		file.write(f"\"Storyteller\",\"{message}\",\"\",\"\"\n")
		file.write(f"\"Action\",\"{res.message or ''}\",\"{res.action}\",\"{res.reasoning}\"\n")

	return res


def select_player(players: List[Player], message: Optional[str]) -> Player:
	user_input = input(f"{message or 'Enter the players name'} ({join_with_word([p.name for p in players], 'or')})")

	for player in players:
		if player.name.upper() == user_input.upper():
			return player

	warnings.warn(f"Invalid player name \"{user_input}\"! Please try again...")
	return select_player(players, message)


def get_random_active_player(available_players: List[Player]) -> Player | None:
	selected_player = available_players[random.randint(0, len(available_players) - 1)]

	if len(selected_player.action_history) > 0:
		latest_action = selected_player.action_history[-1]
		if latest_action == 'idle':
			eligible_player = filter(
				len(p.action_history) > 0 or p.action_history[-1] != 'idle' for p in available_players)
			if not eligible_player:
				return None

			return get_random_active_player(available_players)

	return selected_player


def initialize_players(systemInstruction: str, players: List[Player]) -> None:
	for index, player in enumerate(players):
		initial_message = "These are the following players in the game, in clockwise order around the circle: \n"
		for other_index, other_player in enumerate(players):
			if other_player.name == player.name:
				initial_message += f" - {other_player.name} (You)\n"
			elif index == other_index - 1 or (index == 0 and other_index == len(players) - 1):
				initial_message += f" - {other_player.name} (Your neighbor to your left)\n"
			elif index == other_index + 1 or (index == len(players) - 1 and other_index == 0):
				initial_message += f" - {other_player.name} (Your neighbor to your right)\n"
			else:
				initial_message += f" - {other_player.name}\n"
		initial_message += f"You have been given the {player.token_shown or player.actual_role} token. The storyteller puts you to sleep.\n"
		initial_message += f"You must respond with a JSON object that includes a 'reasoning' property that shows your thought process, as well as an 'action' property that shows what action you would like to take.\n"
		initial_message += f"For now, the only action you can take is 'idle'. In the future, there may be other actions that you can take which will be communicated to you."

		player.chat_history = []
		with open(f"{GENERATED_DATA_DIRECTORY}/{player.name}.csv", "w") as file:
			file.write("\"Type\",\"Message\",\"Action\",\"Reasoning\"\n")
		send_message_to_player(systemInstruction, player, initial_message, ['idle'])


def broadcast_message(players: List[Player], message: str, excluded_player_names: Optional[List[str]]=None) -> None:
	for player in players:
		if excluded_player_names and player.name in excluded_player_names:
			continue

		player.chat_history.append(ContentDict(role='user', parts=[Part(message)]))
		player.action_history.append('hear_message')
		with open(f"{GENERATED_DATA_DIRECTORY}/{player.name}.csv", "a") as file:
			file.write(f"\"Message\",\"{message}\",\"\",\"\"\n")


def format_player_status(status: PlayerStatus) -> str:
	if status == 'alive':
		return 'Alive'
	elif status == 'dead-without-vote':
		return 'Dead without Ghost Vote'
	elif status == 'dead-with-vote':
		return 'Dead with Ghost Vote'
