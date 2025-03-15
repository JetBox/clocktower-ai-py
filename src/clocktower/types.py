from dataclasses import dataclass
from typing import Literal, List, Optional

from google.generativeai.types import ContentDict

RoleType = Literal['townsfolk', 'outsider', 'minion', 'demon']
GameStatus = Literal['evil-wins', 'good-wins', 'ongoing']
PlayerStatus = Literal['alive', 'dead-with-vote', 'dead-without-vote']
NominationResultType = Literal['on-the-block', 'tie', 'insufficient-votes']


@dataclass
class Role:
	name: str
	type: RoleType
	ability: str
	detailed_ability: str
	player_tips: List[str]
	fighting_tips: Optional[List[str]] = None
	bluffing_tips: Optional[List[str]] = None
	examples: Optional[List[str]] = None

	@classmethod
	def from_dict(cls, data):
		return cls(**data)


@dataclass
class Player:
	name: str
	actual_role: str
	chat_history: List[ContentDict]
	action_history: List[str]
	status: PlayerStatus
	token_shown: Optional[str] = None


@dataclass
class PlayerResponse:
	reasoning: str
	action: str
	message: Optional[str] = None
	players: Optional[List[str]] = None


@dataclass
class PlayerResponseWithPlayer:
	player: Player
	player_response: PlayerResponse


@dataclass
class NominationResult:
	result: NominationResultType
	votes: int
	nominator: Player
	nominee: Player


@dataclass
class PlayerDiscussionResult:
	action: str
	nomination: Optional[NominationResult] = None
