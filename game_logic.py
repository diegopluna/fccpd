from typing import Dict
from quiz_api import QuizAPI

class QuizGame:
    def __init__(self, api_key: str):
        self.quiz_api = QuizAPI(api_key)
        self.current_score = 0
        self.current_question = 0
        self.questions = []
        self.total_questions = 0

    def start_new_game(self, category: str = None, difficulty: str = None, 
                      num_questions: int = 10) -> None:
        print("Starting new game")
        """Start a new game by fetching questions"""
        self.questions = self.quiz_api.get_questions(
            category=category,
            difficulty=difficulty,
            limit=num_questions
        )
        print("Questions fetched")
        self.total_questions = len(self.questions)
        self.current_question = 0
        self.current_score = 0

    def get_current_question(self) -> Dict:
        """Get the current question details"""
        if self.current_question >= self.total_questions:
            return None
        return self.questions[self.current_question]

    def check_answer(self, user_answers: Dict[str, bool]) -> bool:
        """Check if the user's answer is correct"""
        current_q = self.questions[self.current_question]
        correct_answers = current_q['correct_answers']
        
        is_correct = True
        for answer_key, is_selected in user_answers.items():
            correct_key = answer_key.replace('answer_', 'correct_') + '_correct'
            if str(is_selected).lower() != str(correct_answers.get(correct_key, 'false')).lower():
                is_correct = False
                break

        if is_correct:
            self.current_score += 1
        self.current_question += 1
        return is_correct

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.current_question >= self.total_questions

    def get_game_summary(self) -> Dict:
        """Get the game summary"""
        return {
            'total_questions': self.total_questions,
            'correct_answers': self.current_score,
            'score_percentage': (self.current_score / self.total_questions) * 100 if self.total_questions > 0 else 0
        }