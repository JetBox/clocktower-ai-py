from typing import List

from src.clocktower.players import send_message_to_player, broadcast_message, get_random_active_player
from src.clocktower.types import Player


def get_player_input_in_private_chat(systemInstruction: str, player: Player, other_players: List[Player],
									 message_count=0) -> None:
	other_player_names = join_with_word([p.name for p in other_players])
	player_response = send_message_to_player(systemInstruction, player,
											 f"Would you like to say {'anything else' if message_count > 0 else 'anything'} in the private chat with {other_player_names}? You must respond with a JSON object with three properties. The 'reasoning' property should include a string of your current train of thought, the 'action' property should either be 'idle' (to listen and wait for others to say something) or 'private_message' (to say something in the private chat). If you choose 'private_message', you must also include a 'message' property with the message you want to share in the private chat.",
											 ['idle', 'private_message'])

	if player_response.action == 'idle':
		return
	elif player_response.action != 'private_message':
		raise Exception(f"Invalid player action in private chat {player_response.action}")

	print(f"{player.name} -> {other_player_names}: {player_response.message}")

	broadcast_message(other_players, f"In your private chat, {player.name} says: {player_response.message}")


def run_private_chat(systemInstruction: str, players_in_chat: List[Player], message_count=0) -> None:
	# await randomSleep()
	random_player_in_chat = get_random_active_player(players_in_chat)
	if not random_player_in_chat:
		print("The private chat is now over!")
		return

	get_player_input_in_private_chat(systemInstruction, random_player_in_chat,
									 [p for p in players_in_chat if p.name != random_player_in_chat.name],
									 message_count)

	return run_private_chat(systemInstruction, players_in_chat, message_count + 1)


def start_private_chat(systemInstruction: str, requester_player: Player, other_player_names: List[str],
					   all_players: List[Player]) -> None:
	other_player_names_lowercase = [p.lower() for p in other_player_names]
	other_players = [p for p in all_players if p.name.lower() in other_player_names_lowercase]

	if len(other_players) != len(other_player_names):
		raise Exception(
			f"Player {requester_player.name} tried to request a private hat with one or more invalid player name(s): [{', '.join(other_player_names)}]")

	players_in_chat = [requester_player] + other_players
	for player_in_chat in players_in_chat:
		other_players_in_chat = join_with_word([p.name for p in players_in_chat if p.name != player_in_chat.name])

		broadcast_message([player_in_chat], f"You are now in a private chat with {other_players_in_chat}")

	get_player_input_in_private_chat(systemInstruction, requester_player, other_players)
	run_private_chat(systemInstruction, players_in_chat, 1)
	for player_in_chat in players_in_chat:
		other_players_in_chat = join_with_word([p.name for p in players_in_chat if p.name != player_in_chat.name])
		broadcast_message([player_in_chat],
						  f"You have now finished the private chat with {other_players_in_chat} and rejoined the other players.")
