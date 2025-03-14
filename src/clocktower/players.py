import json
from typing import List

from google.ai.generativelanguage_v1 import Part
from google.generativeai.types import ContentDict, 

from src.clocktower.types import Player
from src.services.constants import GENERATED_DATA_DIRECTORY


def send_message_to_player(systemInstruction: str, player: Player, message: str, allowed_actions: List[str]):
	res = generate_response(systemInstruction, player.chat_history, message, allowed_actions)
	
	player.chat_history.append(ContentDict(role='user', parts=[Part(message)]))
	player.chat_history.append(ContentDict(role='model', parts=[Part(json.dumps(res))]))
	player.action_history.append(res.action)
	
		