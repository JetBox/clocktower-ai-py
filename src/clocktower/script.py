import json
from typing import List

from src.clocktower.types import Role
from src.services.constants import ROLES_DIRECTORY, PROMPTS_DIRECTORY


def get_role_json(role: str) -> Role:
	with open(f"{ROLES_DIRECTORY}/{role.lower().replace(' ','-')}.json", 'r') as file:
		role_string = json.load(file)
		return Role.from_dict(role_string)
	
def create_system_prompt(roles: List[str]) -> str:
	with open(f"{PROMPTS_DIRECTORY}/introduction.txt", "r") as file:
		introduction_prompt = file.readlines()
	
	script_prompt_parts = [
		introduction_prompt,
		"\n\nBelow is a detailed description of each character that is on the script:"
	]
	
	for role in roles:
		role_json = get_role_json(role)
		
		script_prompt_parts.append(f"\n\n{role_json.name} ({role_json.type}): {role_json.ability}")
		script_prompt_parts.append(f"\nThis is the detailed description for the {role_json.name}: ")
		script_prompt_parts.append(role_json.detailed_ability)
		script_prompt_parts.append(f"\n Below are some tips for playing as the {role_json.name}:")
		for player_tip in role_json.player_tips:
			script_prompt_parts.append(f" - {player_tip}")
		
		if role_json.bluffing_tips:
			script_prompt_parts.append(f"\nBelow are some tips for bluffing as the {role_json.name}:")
			for player_tip in role_json.bluffing_tips:
				script_prompt_parts.append(f" - {player_tip}")
				
		if role_json.fighting_tips:
			script_prompt_parts.append(f"\nBelow are some tips for fighting against the {role_json.name}")
			for player_tip in role_json.fighting_tips:
				script_prompt_parts.append(f" - {player_tip}")
				
		if role_json.examples:
			script_prompt_parts.append(f"\bBelow are some examples of how the {role_json} role is used:")
			for player_tip in role_json.examples:
				script_prompt_parts.append(f" - {player_tip}")
				
		script_prompt_parts.append(f"\n\nNow that you understand how each of these roles work in detail, below is a recap of the specific roles that are on the script: ")
		
		for role in roles:
			role_json = get_role_json(role)
			script_prompt_parts.append(f" - {role_json.name} ({role_json.type}): {role_json.ability}")
			
		with open(f"{PROMPTS_DIRECTORY}/conclusion.txt", "r") as file:
			conclusion_prompt = file.readlines()
		script_prompt_parts.append(f"\n\n{conclusion_prompt}")
		
		return '\n'.join(script_prompt_parts)