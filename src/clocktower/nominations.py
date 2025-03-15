import math
import warnings
from typing import List, Optional

from src.clocktower.players import broadcast_message, send_message_to_player, get_random_active_player
from src.clocktower.storyteller import make_storyteller_announcement
from src.clocktower.types import Player, NominationResult


def format_name_with_apostrophe(name: str) -> str:
	return f"{name}'s"


def get_player_input_in_nomination(systemInstruction: str, players: List[Player], player: Player, nominator: Player,
								   nominee: Player) -> str:
	player_response = send_message_to_player(systemInstruction, player,
											 f"Would you like to say anything about {'your' if nominator.name == player.name else format_name_with_apostrophe(nominator.name)}"
											 f"nomination for {'yourself' if nominee.name == player.name else nominee.name}? "
											 f"You must respond with a JSON object with three properties. The 'reasoning' property should include a string of your current train of thought, the 'action' property should either be 'idle' (to listen and wait for others to say something) or 'announcement' (to say something publicly). If you choose 'announcement', you must also include a 'message' property with the message you want to share publicly about the nomination. Try to keep on topic and avoid discussing unrelated topics during the nomination. "
											 f"{'Make sure to put your best foot forward and try to convince the town of your viewpoint.' if nominee.name == player.name or nominator.name == player.name else 'It is OK to stay quiet if you do not have anything important to add to the nomination. You will get another chance to speak afterwards if you want to discuss something else.'}",
											 ['idle', 'announcement'])

	if player_response == 'idle':
		return 'idle'
	elif player_response.action != 'announcement':
		raise Exception(f"Invalid player action in nomination '{player_response.action}'")

	print(f"{player.name}: {player_response.message}")

	broadcast_message(players,
					  f"During the nomination for {nominee.name}, {player.name} says: {player_response.message}")
	return 'announcement'


def run_nomination_discussion(systemInstruction: str, players: List[Player], nominator: Player, nominee: Player,
							  message_count=0) -> None:
	# After every 3rd, check if the storyteller wants to continue
	if message_count >= 3 and message_count % 3 == 0:
		user_input = input('`Would you like to [C]ontinue discussion, [M]ake an announcement or [P]roceed to voting? ')
		user_input = user_input.upper()

		if user_input == 'P':
			return
		elif user_input == 'M':
			make_storyteller_announcement(players)
			return run_nomination_discussion(systemInstruction, players, nominator, nominee, message_count + 1)
		elif user_input != 'C':
			warnings.warn("You must respond with either [C], [M] or [P]!")
			return run_nomination_discussion(systemInstruction, players, nominator, nominee, message_count + 1)

		# random_sleep()
		random_player = get_random_active_player(players)
		if not random_player:
			print("All players have chosen to idle")
			return

		action = get_player_input_in_nomination(systemInstruction, players, random_player, nominator, nominee)
		return run_nomination_discussion(systemInstruction, players, nominator, nominee,
										 message_count if action == 'idle' else message_count + 1)


def start_nomination(systemInstruction: str, players: List[Player], nominator: Player, nominee: Player,
					 message: str, existing_nomination=Optional[NominationResult]) -> NominationResult:
	nomination_announcement = f"{nominator.name} has nominated {nominee.name} for execution: {message}"

	broadcast_message(players, nomination_announcement, [nominator.name])

	for player in players:
		player.action_history.append('start_nomination')

	print(f"{nominator.name}, please give your reasoning for the nomination.")
	broadcast_message(players,
					  f"The storyteller has requested {nominator.name} to explain the reason for the nomination.")

	get_player_input_in_nomination(systemInstruction, players, nominator, nominator, nominee)

	print(f"{nominee.name}, please give your defense for the nomination.")
	broadcast_message(players, f"The storyteller has requested {nominee.name} to defend themselves.")

	get_player_input_in_nomination(systemInstruction, players, nominee, nominator, nominee)

	run_nomination_discussion(systemInstruction, players, nominator, nominee)

	# Votes are taken from the player to the left of the nominee clockwise until reaching the nominee last
	nominee_index = next((idx for idx, player in enumerate(players) if player.name == nominee.name), -1)
	vote_order = players[nominee_index + 1:] + players[:nominee_index + 1]

	alive_player_count = len([p for p in players if p.status == 'alive'])
	min_votes = existing_nomination.votes + 1 if existing_nomination else math.ceil(alive_player_count / 2)

	vote_prompt = [
		f"Votes for {nominee.name} will begin with {vote_order[0].name} and end with {nominee.name}, going clockwise around the circle.",
		"You don't have to vote if you don't want to, and sometimes it's beneficial to ensure that not too many people vote so that you still can overturn the nomination later in the day if you find a better candidate or learn new information.",
		f"If at least the majority of alive players vote, then {nominee.name} will be put on the block for execution." if not existing_nomination else None,
		f"There are currently {alive_player_count} alive players, so at least {min_votes} votes are required for the nomination to go through." if not existing_nomination else None,
		f"The previous nomination for {existing_nomination.nominee.name} got {existing_nomination.votes}, so at least {min_votes} votes are required to put {nominee.name} on the block instead." if existing_nomination else None,
		f"If {nominee.name} receives the same number of votes as {existing_nomination.nominee.name} received, the nomination will result in a tie and neither player will be executed." if existing_nomination else None,
		"Remember that if you are dead, you only get one more vote for the rest of the game.",
		"If you have already used your ghost vote, you cannot vote again."
	]
	vote_prompt = " ".join(filter(None, vote_prompt))

	print(
		f"Votes will begin with ${vote_order[0].name} and end with {nominee.name}. At least {min_votes} are required.")

	broadcast_message(players, vote_prompt)
	total_votes = 0

	for player in vote_order:
		if player.status == 'dead-without-vote':
			continue

		message = f"Would you like to vote for {nominee.name}? {'' if player.status != 'dead-with-vote' else 'Do not forget that you ar dead, so if you choose to vote now, you will not be able to vote again for the rest of the game.'}"

		player_response = send_message_to_player(systemInstruction, player,
												 message + f"Respond with a JSON object containing a 'reasoning' key that includes your train of thought, and an 'action' key which either has the value 'idle' (if you don't want to vote) or 'vote' (if you want to cast your vote).",
												 ['idle', 'vote'])

		has_voted = player_response.action == 'vote'
		if has_voted:
			total_votes += 1

		print(f"{player.name} is {'voting' if has_voted else 'not voting'} ({total_votes}/{min_votes})")

		broadcast_message(player,
						  f"{player.name} has chosen {'to vote' if has_voted else 'not to vote'} towards the execution of {nominee.name}. {'That is ' + str(total_votes) + ' out of ' + str(min_votes) + ' required votes so far' if total_votes < min_votes else 'That is ' + str(total_votes) + ' so far'}")

		if existing_nomination and existing_nomination.votes == total_votes:
			tie_message = f"{total_votes} players voted to execute {nominee.name}, which is a tie against the existing nomination for {existing_nomination.nominee.name}! Therefore, no one is on the block for execution now."
			print(tie_message)
			broadcast_message(players, tie_message)

			return NominationResult(result='tie', votes=total_votes, nominator=nominator, nominee=nominee)
		elif total_votes < min_votes:
			insufficient_votes_message = f"Only {total_votes} players voted to execut {nominee.name}, which is not enough! {'The nomination is now over' if not existing_nomination else 'The nomination is now over and ' + str(existing_nomination) + ' is still on the block for execution.'}"

			print(insufficient_votes_message)
			broadcast_message(players, insufficient_votes_message)

			return NominationResult(result='insufficient-votes', votes=total_votes, nominator=nominator,
									nominee=nominee)

		success_message = f"{total_votes} players voted to execute {nominee.name}, which is enough! {str(nominee.name) + ' is now on the block for execution' if not existing_nomination else str(nominee.name) + ' is now on the block for execution instead of ' + str(existing_nomination.nominee.name) + '.'}"

		print(success_message)
		broadcast_message(players, success_message)

		return NominationResult(result='on-the-block', votes=total_votes, nominator=nominator, nominee=nominee)
