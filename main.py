import os
import sys
from typing import Optional, Dict, Any
from db.conn import DatabaseConnection
from db.schema import User, Question
from db.repository import UserRepository, QuestionRepository, GameRepository, RepositoryError
from quiz_api import QuizAPI, QuizAPIError
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quiz_game.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MenuManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.session = None
        self.user_repo = None
        self.question_repo = None
        self.game_repo = None
        self.quiz_api = None
        
    def initialize(self) -> bool:
        """Initialize database connection and repositories."""
        try:
            db_connect = self.db.connect()
            if not db_connect:
                logger.error("Failed to connect to database")
                return False
            
            self.user_repo = UserRepository(session_factory=self.db.get_session)
            self.question_repo = QuestionRepository(session_factory=self.db.get_session)
            self.game_repo = GameRepository(session_factory=self.db.get_session)
            
            # Initialize QuizAPI with key from environment
            api_key = "Nu4Q4o5IFPwgTUWcEmgWUpwyK06B3yGg3TbmkkTM"
            # if not api_key:
            #     logger.error("QUIZ_API_KEY environment variable not set")
            #     return False
            
            self.quiz_api = QuizAPI(api_key)
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {str(e)}")
            return False
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_menu(self):
        """Display the main menu."""
        self.clear_screen()
        print(
            """
            === Quiz Game Management System ===

            User Operations:
            1. Create User
            2. View User
            3. Update User
            4. Delete User

            Question Operations:
            5. Add Question
            6. View Question
            7. Update Question
            8. Delete Question

            Game Operations:
            9. Start New Game
            10. View Game History
            11. View Leaderboard
            12. Delete Game

            13. Exit
            """
        )
    
    def get_user_input(self, prompt: str, validate_func=None) -> Optional[str]:
        """Get and validate user input."""
        while True:
            value = input(prompt).strip()
            if not value:
                return None
            if validate_func is None or validate_func(value):
                return value
            print("Invalid input. Please try again.")
            
    def handle_user_operations(self, choice: str):
        """Handle user-related operations."""
        try:
            if choice == "1":
                username = self.get_user_input("Enter username: ")
                if username:
                    dict_user = {"username": username}
                    new_user = User(**dict_user)
                    user = self.user_repo.create(new_user)
                    logger.info(f"Created user: {username}")
                    print(f"User created successfully! ID: {user.id}")
                    
            elif choice == "2":
                user_id = self.get_user_input("Enter user ID: ", str.isdigit)
                if user_id:
                    user = self.user_repo.get_by_id(int(user_id))
                    if user:
                        print(f"User found: {user.username}")
                        games = self.game_repo.get_by_user(user)
                        print(f"Total games played: {len(games)}")
                    else:
                        print("User not found")
                        
            elif choice == "3":
                user_id = self.get_user_input("Enter user ID: ", str.isdigit)
                if user_id:
                    user = self.user_repo.get_by_id(int(user_id))
                    if user:
                        print(f"User found: {user.username}")
                        new_username = self.get_user_input("Enter new username: ")
                        if new_username:
                            user.username = new_username
                            self.user_repo.update(user)
                            print("User updated successfully!")
                        else:
                            print("User not found")
                            
            elif choice == "4":
                user_id = self.get_user_input("Enter user ID: ", str.isdigit)
                if user_id:
                    user = self.user_repo.get_by_id(int(user_id))
                    print(f"User found: {user.username}")
                    if user:
                        confirm = input("Are you sure? This will delete all user data (y/n): ")
                        if confirm.lower() == 'y':
                            if self.user_repo.delete(int(user_id)):
                                print("User deleted successfully!")
                            else:
                                print("User not found")
                            
        except RepositoryError as e:
            logger.error(f"Repository error in user operations: {str(e)}")
            print("An error occurred while processing your request")
            if hasattr(e, 'original_error'):
                logger.error(f"Original error: {str(e.original_error)}")
    
    def handle_question_operations(self, choice: str):
        """Handle question-related operations."""
        try:
            if choice == "5":
                question = {
                    "question": self.get_user_input("Enter question: "),
                    "description": self.get_user_input("Enter description: "),
                    "answers": {
                        "answer_a": self.get_user_input("Enter answer A: "),
                        "answer_b": self.get_user_input("Enter answer B: "),
                        "answer_c": self.get_user_input("Enter answer C: "),
                        "answer_d": self.get_user_input("Enter answer D: "),
                        "answer_e": self.get_user_input("Enter answer E: "),
                        "answer_f": self.get_user_input("Enter answer F: ")
                    },
                    "multiple_correct_answers": False, # recomendo tirar isso aqui
                    "correct_answers": {
                        "answer_a_correct": False,
                        "answer_b_correct": False,
                        "answer_c_correct": False,
                        "answer_d_correct": False,
                        "answer_e_correct": False,
                        "answer_f_correct": False
                    },
                    "explanation": self.get_user_input("Enter explanation: "),
                    "tip": self.get_user_input("Enter tip (or press Enter to skip): "),
                    "tags": [tag.strip() for tag in self.get_user_input("Enter tags (comma-separated): ").split(",")],
                    "category": self.get_user_input("Enter category: "),
                    "difficulty": self.get_user_input("Enter difficulty (easy/medium/hard): ")
                }

                print(f"{question['question']}\n")
                for key, answer in question['answers'].items():
                    print(f"{key[-1].upper()}) {answer}")

                correct_answers = [answer.strip() for answer in self.get_user_input("Enter correct answers (comma-separated): ").lower().split(",") if answer in ['a', 'b', 'c', 'd', 'e', 'f']]
                for answer in correct_answers:
                    key = f"answer_{answer.lower()}_correct"
                    question['correct_answers'][key] = True

                answers_list = [ question["answers"][f"answer_{letter}"] for letter in "abcdef" ]

                correct_answers_list = [ question["correct_answers"].get(f"answer_{letter}_correct", False) for letter in "abcdef"]

                new_question = Question(
                    question=question["question"],
                    description=question["description"],
                    answers=answers_list,
                    correct_answers=correct_answers_list,
                    explanation=question["explanation"],
                    tip=question["tip"] if question["tip"] else None,
                    tags=question["tags"],
                    category=question["category"],
                    difficulty=question["difficulty"]
                )
                
                saved_question = self.question_repo.create(new_question)
                logger.info(f"Created question: {saved_question.question}")
                print(f"Question created successfully! ID: {saved_question.id}")
                
            elif choice == "6":
                question_id = self.get_user_input("Enter question ID: ", str.isdigit)
                if question_id:
                    question = self.question_repo.get_by_id(int(question_id))
                    if question:
                        print(f"Question: {question.question}")
                        print(f"Description: {question.description}")
                        print(f"Category: {question.category}")
                        print(f"Difficulty: {question.difficulty}")
                        print(f"Tags: {', '.join(question.tags)}")
                        print(f"Tip: {question.tip}")
                        print(f"Explanation: {question.explanation}")
                        print("Answers:")
                        for letter, answer, correctness in zip("abcdef", question.answers, question.correct_answers):
                            print(f"{letter}) {answer} ({'Correct' if correctness else 'Incorrect'})")
                        print(question.correct_answers)
                    else:
                        print("Question not found")
            
            elif choice == "7":
                print("Update Question")
                print("Not implemented yet")
            
            elif choice == "8":
                print("Delete Question")
                print("Not implemented yet")
        
        except RepositoryError as e:
            logger.error(f"Repository error in game operations: {str(e)}")
            print("An error occurred while processing your request")
                
    def handle_game_operations(self, choice: str):
        """Handle game-related operations."""
        try:
            if choice == "9":
                user_id = self.get_user_input("Enter user ID: ", str.isdigit)
                if not user_id:
                    return
                    
                user = self.user_repo.get_by_id(int(user_id))
                if not user:
                    print("User not found")
                    return
                    
                # Get game settings
                category = self.get_user_input("Enter category (or press Enter for any): ")
                difficulty = self.get_user_input("Enter difficulty (easy/medium/hard): ")
                
                try:
                    # Fetch questions from API
                    questions = self.quiz_api.get_questions(
                        category=category,
                        difficulty=difficulty,
                        limit=10
                    )
                    
                    # Start game
                    game = self.start_game(user, questions)
                    if game:
                        print(f"Game completed! Score: {game.score}/{game.rounds}")
                        
                except QuizAPIError as e:
                    logger.error(f"Quiz API error: {str(e)}")
                    print("Failed to fetch questions. Please try again later.")
                    
            elif choice == "10":
                user_id = self.get_user_input("Enter user ID: ", str.isdigit)
                if user_id:
                    games = self.game_repo.get_by_user_id(int(user_id))
                    if games:
                        print("\nGame History:")
                        for game in games:
                            print(f"Game ID: {game.id}, Score: {game.score}/{game.rounds}, "
                                  f"Date: {game.created_at}")
                    else:
                        print("No games found for this user")
                        
            elif choice == "11":
                # Show top 10 scores
                games = self.game_repo.get_top_scores(limit=10)
                if games:
                    print("\nLeaderboard:")
                    for i, game in enumerate(games, 1):
                        user = self.user_repo.get_by_id(game.user_id)
                        print(f"{i}. {user.username}: {game.score} points "
                              f"({game.score/game.rounds*100:.1f}%)")
                else:
                    print("No games found")
                    
            elif choice == "12":
                game_id = self.get_user_input("Enter game ID: ", str.isdigit)
                if game_id:
                    if self.game_repo.delete(int(game_id)):
                        print("Game deleted successfully!")
                    else:
                        print("Game not found")
                        
        except RepositoryError as e:
            logger.error(f"Repository error in game operations: {str(e)}")
            print("An error occurred while processing your request")
            
    def start_game(self, user, questions) -> Optional[Dict[str, Any]]:
        """Run a game session."""
        score = 0
        total_questions = len(questions)
        
        for i, question in enumerate(questions, 1):
            self.clear_screen()
            print(f"\nQuestion {i}/{total_questions}")
            print(f"\n{question['question']}")
            
            if question['description']:
                print(f"\nDescription: {question['description']}")
                
            # Display answers
            answers = question['answers']
            for key, answer in answers.items():
                if answer:
                    print(f"\n{key[-1].upper()}) {answer}")
                    
            # Get user answer
            while True:
                answer = input("\nYour answer (A/B/C/D/E/F): ").upper()
                if answer in 'ABCDEF':
                    break
                print("Invalid input. Please enter A, B, C, D, E, or F.")
                
            # Check answer
            answer_key = f"answer_{answer.lower()}_correct"
            if question['correct_answers'].get(answer_key) == "true":
                score += 1
                print("\nCorrect!")
            else:
                print("\nIncorrect!")
                
            if question['explanation']:
                print(f"\nExplanation: {question['explanation']}")
                
            input("\nPress Enter to continue...")
            
        # Save game results
        try:
            game_data = {
                "user_id": user.id,
                "questions": [q['id'] for q in questions],
                "rounds": total_questions,
                "score": score
            }
            game = self.game_repo.create(game_data)
            return game
        except RepositoryError as e:
            logger.error(f"Failed to save game results: {str(e)}")
            print("Failed to save game results, but here's your score: "
                  f"{score}/{total_questions}")
            return None
    
    def run(self):
        """Run the main application loop."""
        if not self.initialize():
            print("Failed to initialize application. Check the logs for details.")
            return

        while True:
            try:
                self.print_menu()
                choice = self.get_user_input("\nEnter your choice (1-13): ")
                
                if not choice:
                    continue
                    
                if choice in ["1", "2", "3", "4"]:
                    self.handle_user_operations(choice)
                elif choice in ["5", "6", "7", "8"]:
                    self.handle_question_operations(choice)
                elif choice in ["9", "10", "11", "12"]:
                    self.handle_game_operations(choice)
                elif choice == "13":
                    print("\nThank you for using the Quiz Game!")
                    break
                else:
                    print("Invalid choice!")
                
                input("\nPress Enter to continue...")
                
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                print("An unexpected error occurred. Please try again.")
                input("\nPress Enter to continue...")

        if self.session:
            self.session.close()
def main():
    menu = MenuManager()
    menu.run()

if __name__ == '__main__':
    main()