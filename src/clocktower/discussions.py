import warnings
from typing import List, Optional

from src.clocktower.nominations import start_nomination
from src.clocktower.players import send_message_to_player, broadcast_message, get_random_active_player
from src.clocktower.status import get_game_status, finish_game
from src.clocktower.storyteller import make_storyteller_announcement
from src.clocktower.types import PlayerDiscussionResult, Player, NominationResult, PlayerResponse


def send_discussion_input(systemInstruction: str, selected_player: Player, nominations_open: bool,
						  existing_nomination: Optional[NominationResult]) -> PlayerResponse:
	message = ''
	message += "It's currently the discussion phase." if not nominations_open else ''
	message += "It's currently the nomination phase. You can nominate a player for execution, or make a public announcement. You can no longer talk to the storyteller in private (e.g. to use character abilities) you'll need to wait until the next day if you want to do this." if nominations_open and not existing_nomination and selected_player.status == 'alive' else ''
	message += f"It's currently the nomination phase and {existing_nomination.nominee.name} is on the block for execution with {existing_nomination.votes} votes. You can still nominate a different player if you think they should die instead, or you can do nothing and {existing_nomination.nominee.name} will be executed shortly." if nominations_open and existing_nomination and selected_player.status == 'alive' else ''
	message += f"It's currently the nomination phase. You can't nominate anyone because you are dead, but you can still participate in the discussion." if nominations_open and selected_player.status != 'alive' else ''
	message += f" You can make any of the following actions: \n"
	message += f" - 'announcement': Publicly announce some information to all players. You must put your announcement in the 'announcement' property.\n"
	message += f" - 'public_ability': Use a character ability that functions in public, such as the Slayer or the Klutz. If you are targeting a player with your ability, you need to specify the player you are targeting in the 'player' property. You must also include a message to the storyteller and the town which explains what you are doing in the 'message' property. You can attempt to use a public ability even if you don't actually have the ability, and if it doesn't work you can always claim that you might be drunk or poisoned, etc.\n" if not nominations_open else ''
	message += f" - 'request_private_chat': Request a private chat with one or more players. You will need to include a message to publicly ask those players to chat using the 'message' property.\n" if not nominations_open else ''
	message += f" - 'talk_to_storyteller': Privately ask the storyteller a question. You will need to include your message for the storyteller in the 'message' property.\n" if not nominations_open else ''
	message += f" - 'nominate': Make a nomination for a specific player. You can only nominate once per day, and each player can only be nominated once per day. You need to include a message to share with the town in the 'message' property as well as the name of the player you want to nominate as a single entry in the 'players' array.\n" if nominations_open and selected_player.status == 'alive' else ''
	message += f" - 'idle': Do nothing, and listen to what other members of the town do first. Don't be afraid to idle and listen for other input before jumping in. Often it is better to stay quiet than to over-share, even if you are good.\n"
	message += f"\n\nPlease respond with a JSON object including your 'reasoning', 'action', and the 'message' that you would like to share, if applicable to the action you are taking. If you need to list one or more players as part of your action, include a string array with the property 'players' in your response.\n"
	possible_actions = ['announcement', 'idle']
	if not nominations_open:
		possible_actions.append('public_ability')
		possible_actions.append('request_private_chat')
		possible_actions.append('talk_to_storyteller')
	elif selected_player.status == 'alive':
		possible_actions.append('nominate')
	return send_message_to_player(systemInstruction, selected_player, message, possible_actions)


def get_player_input_for_discussions_phase(systemInstruction: str, players: List[Player], selected_player: Player,
										   nominations_open: bool,
										   existing_nomination: Optional[NominationResult]) -> PlayerDiscussionResult:
	player_response = send_discussion_input(systemInstruction, selected_player, nominations_open, existing_nomination)
	if player_response.action == 'idle':
		return PlayerDiscussionResult(action='idle')
	elif player_response.action == 'announcement':
		if not player_response.message:
			warnings.warn(f"Player announcement is missing message: {selected_player}, {player_response}")
			raise Exception("Player announcement was missing message!")
		print(f"{selected_player.name}: {player_response.message}")
		broadcast_message(players, f"{selected_player.name} has made the announcement: {player_response.message}",
						  [selected_player.name])
		return PlayerDiscussionResult(action='announcement')
	elif player_response.action == 'public_ability':
		if not player_response.message:
			warnings.warn(f"Public ability use is missing message: {selected_player}, {player_response}")
			raise Exception("Public ability use was missing message!")

		use_public_ability(players, selected_player, player_response.message,
						   player_response.players[0] if player_response.players and len(
							   player_response.players) else None)
		return PlayerDiscussionResult(action='public_ability')
	elif player_response.action == 'talk_to_storyteller':
		if nominations_open:
			raise Exception("Cannot talk to storyteller during nominations!")
		elif not player_response.message:
			warnings.warn(
				f"Player {selected_player.name} has requested to talk to the storyteller but is missing a message: {selected_player}, {player_response}")
			raise Exception("Storyteller chat was missing message!")
		print(f"{selected_player.name} has requested to talk to the storyteller: {player_response.message}")
		storyteller_response = input(f"How would you like to respond to {selected_player.name}")
		run_player_conversation_with_storyteller(systemInstruction, selected_player,
												 f"The storyteller has answered: {storyteller_response}")
		return PlayerDiscussionResult(action='talk_to_storyteller')
	elif player_response.action == 'request_private_chat':
		if nominations_open:
			raise Exception("Cannot begin a private chat during nominations!")
		elif not player_response.message:
			warnings.warn(
				f"Player {selected_player.name} requested a private chat but didn't include a message: {selected_player}, {player_response}")
			raise Exception("requested a private chat but didn't include a message!")
		elif not player_response.players or len(player_response.players) == 0:
			raise Exception(
				f"{selected_player.name} requested a private chat but didn't list any players: {player_response.message}")
		player_names = join_with_word(player_response.players)
		print(f"{selected_player.name} has requested a private chat with ${player_names}: {player_response.message}")
		broadcast_message(players, f"{selected_player.name} has made the announcement: {player_response.message}",
						  [selected_player.name])
		start_private_chat(systemInstruction, selected_player, player_response.players, players)
		return PlayerDiscussionResult(action='request_private_chat')
	elif player_response.action == 'nominate':
		if not nominations_open:
			raise Exception(f"{selected_player.name} made a nomination before Nominations were opened!")
		elif not player_response.players or len(player_response.players) == 0:
			raise Exception(f"{selected_player.name} made a nomination without specifying any players!")
		elif player_response.players and len(player_response.players) > 1:
			raise Exception(f"{selected_player.name} nominated more than one player at once!")
		elif not player_response.message:
			raise Exception(f"{selected_player} made a nomination without a message!")
		elif selected_player.status != 'alive':
			raise Exception(f"{selected_player.name} tried to nominate when they were dead!")

		nominated_player = next((p for p in players if p.name == player_response.players[0]), None)
		if not nominated_player:
			raise Exception(f"Invalid player name {player_response.players[0]} for nomination.")

		nomination_result = start_nomination(systemInstruction, players, selected_player, nominated_player,
											 player_response.message)
		return PlayerDiscussionResult(action='nomination', nomination=nomination_result)

	raise Exception(f"Invalid action {player_response.action} during the discussion phase from {selected_player.name}.")


def complete_discussion_phase(players: List[Player], nomination: Optional[NominationResult]) -> None:
	if not nomination:
		message = f"The day is now over and no one made any nominations! Good night!"
		broadcast_message(players, message)
		return

	user_input = input(
		f"Nominations are now closed. {nomination.nominee.name} was nominated by {nomination.nominator.name} and received {nomination.votes}, which is enough for execution. Does {nomination.nominee.name} die [Y/n]? ")
	user_input = user_input.upper()
	if user_input == 'Y':
		message = f"{nomination.nominee.name} is executed and dies! Goodnight!"
		if nomination.nominee.status == 'alive':
			nomination.nominee.status = 'dead-with-vote'
			game_status = get_game_status(players)
			if game_status != 'ongoing':
				return finish_game(game_status)

		print(message)
		broadcast_message(players, f"Nominations are now closed. {message}")
		return
	elif user_input == 'N':
		message = f"{nomination.nominee.name} is executed, but does not die! Goodnight!"
		print(message)
		broadcast_message(players, f"Nominations are now closed. {message}")
		return

	warnings.warn("You must choose [Y] or [N]!")
	return complete_discussion_phase(players, nomination)


def run_discussion_phase(systemInstruction: str, players: List[Player], message_count: int = 0,
						 nominations_open: bool = False,
						 existing_nomination: Optional[NominationResult] = None) -> None:
	# Every 6 messages, check if the storyteller wants to continue the discussion
	if not nominations_open and message_count >= 6 and message_count % 6 == 0:
		user_input = input("Would you like to [C]ontinue discussion, [M]ake an announcement or [O]pen nominations: ")
		user_input = user_input.upper()

		if user_input == 'O':
			print("Nominations are now open!")
			broadcast_message(players,
							  "The storyteller has opened nominations! Does anyone have a player that they wish to nominate for execution?")
			return run_discussion_phase(systemInstruction, players, message_count + 1, True)
		elif user_input == 'M':
			make_storyteller_announcement(players)
			return run_discussion_phase(systemInstruction, players, message_count + 1, nominations_open)
		elif user_input != 'C':
			warnings.warn("You must respond with either [C], [M], or [O]!")
			return run_discussion_phase(systemInstruction, players, message_count, nominations_open,
										existing_nomination)
	elif nominations_open and message_count % 4 == 0:
		user_input = input("Would you like to [C]ontinue nominations, [M]ake an announcement, or [E]nd the day? ")
		user_input = user_input.upper()

		if user_input == 'E':
			return complete_discussion_phase(players, existing_nomination)
		elif user_input == 'M':
			make_storyteller_announcement(players)
			return run_discussion_phase(systemInstruction, players, message_count + 1, nominations_open,
										existing_nomination)
		elif user_input != 'C':
			warnings.warn("You must respond with either [C], [M], or [E]!")
			return run_discussion_phase(systemInstruction, players, message_count, nominations_open,
										existing_nomination)

	# await random_sleep()
	selected_player = get_random_active_player(players)
	if not selected_player:
		return complete_discussion_phase(players, existing_nomination)

	result = get_player_input_for_discussions_phase(systemInstruction, players, selected_player, nominations_open,
													existing_nomination)
	if result.nomination and result.nomination.result != 'insufficient-votes':
		return run_discussion_phase(systemInstruction, players, message_count + 1, nominations_open,
									None if result.nomination.result == 'tie' else result.nomination)

	return run_discussion_phase(systemInstruction, players,
								message_count if result.action == 'idle' else message_count + 1)
