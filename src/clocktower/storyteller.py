from typing import List

from src.clocktower.types import Player


def run_player_conversation_with_storyteller(systemInstruction: str, player: Player, message: string) -> None:
	player_response = send_message_to_player(systemInstruction, player,
											 f"{message}\n\nPlease respond with a JSON object that contains a 'reasoning' property which includes your train of thought, as well as an 'action' property and a 'message' property. The action should be either 'talk_to_storyteller' to provide a response to the storyteller, or 'idle' to end the conversation. If you choose to talk to the storyteller, please include the message in the 'message' property.",
											 ['talk_to_storyteller', 'idle'])

	if player_response.action == 'idle':
		print(f"{player.name} has chosen not to respond.")
		return
	elif player_response.action != 'talk_to_storyteller':
		raise Exception(f"Invalid player action ${player_response.action} during storyteller conversation!")

	print(f"{player.name}: {player_response.message}")
	message_for_player = input(f"How would you like to respond to {player.name}? ")

	run_player_conversation_with_storyteller(systemInstruction, player, message_for_player)


def select_and_kill_player(players: List[Player]) -> Player:
	player = select_player(players, 'Enter the name of the player that you want to kill')

	if player.status == 'alive':
		print(f"You have killed {player.name}!")
		player.status = 'dead-with-vote'
	else:
		print(f"{player.name} was already dead, so nothing happens.")

	return player


def make_storyteller_announcement(players: List[Player]) -> None:
	message = input("What would you like to announce? ")

	broadcast_message(players, message)
