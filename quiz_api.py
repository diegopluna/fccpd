import requests
from typing import List, Dict, Optional
import json

class QuizAPIError(Exception):
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class QuizAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://quizapi.io/api/v1"
        self.headers = {
            "X-Api-Key": self.api_key
        }

    def get_questions(self, category: Optional[str] = None, difficulty: Optional[str] = None, 
                     limit: int = 10, tags: Optional[List[str]] = None) -> List[Dict]:
        """Fetch questions from QuizAPI"""
        endpoint = f"{self.base_url}/questions"
        params = {
            "limit": limit,
            "category": category,
            "difficulty": difficulty,
            "tags": tags
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise QuizAPIError(f"Failed to fetch questions: {response.status_code}")