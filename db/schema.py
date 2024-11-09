from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    
@dataclass
class Question:
    id: int
    question: str
    description: str
    explanation: str
    category: str
    difficulty: str
    answers: Dict[str, str]
    correct_answers: Dict[str,bool]
    
@dataclass
class Game:
    id: int
    user_id: int
    rounds: int
    score: int
    created_at: datetime
    
@dataclass
class GameQuestion:
    id: int
    game_id: int
    question_id: int
    selected_answer_key: Optional[str]
    is_correct: Optional[bool]
    answered_at: Optional[datetime]
