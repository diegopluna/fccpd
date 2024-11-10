from datetime import datetime
from typing import Optional
from db.conn import DatabaseConnection
from db.schema import User, Question, Game
from db.repository import UserRepository, QuestionRepository, GameRepository
from game_logic import QuizGame
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class QuizApplication:
    def __init__(self, api_key: str):
        self.db = DatabaseConnection()
        self.user_repo = UserRepository(self.db)
        self.game_repo = GameRepository(self.db)
        self.question_repo = QuestionRepository(self.db)
        self.game_logic = QuizGame(api_key)

    def clear_screen(self):
        print("\033[H\033[J")
    
    def press_to_continue(self):
        input("Press Enter to continue...")
        print("\033[H\033[J")

    def main_menu(self):
        self.clear_screen()
        print("Welcome to the Quiz Game!")
        print("1. Login or register")
        print("2. Manage database")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            self.start_game()
        elif choice == '2':
            self.db_menu()
        elif choice == '3':
            print("Goodbye!")
        else:
            print("Invalid choice")
            self.press_to_continue()
            self.main_menu()

    def db_menu(self):
        self.clear_screen()
        print("Database Management")
        print("1. Create")
        print("2. Read")
        print("3. Update")
        print("4. Delete")
        print("5. Back")
        choice = input("Enter your choice: ")
        if choice == '1':
            self.create_menu()
        elif choice == '2':
            self.read_menu()
        elif choice == '3':
            self.update_menu()
        elif choice == '4':
            self.delete_menu()
        elif choice == '5':
            self.main_menu()
        else:
            print("Invalid choice")
            self.db_menu()

    def create_menu(self):
        self.clear_screen()
        print("Create Menu")
        print("1. Create User")
        print("2. Create Question")
        print("3. Back")
        choice = input("Enter your choice: ")
        if choice == '1':
            self.create_user()
        elif choice == '2':
            self.create_question()
        elif choice == '3':
            self.db_menu()
        else:
            print("Invalid choice")
            self.create_menu()
    
    def create_user(self):
        while True:
            username = input("Enter username: ")
            if not username:
                print("Username cannot be empty")
            else:
                existing_user = self.user_repo.get_user_by_username(username)
                if existing_user:
                    print("User already exists")
                else:
                    user = self.user_repo.create_user(username)
                    if user:
                        print(f"User {user.username} created with ID {user.id}")
                        self.press_to_continue()
                        self.create_menu()
                    else:
                        print("Failed to create user")
                    break
    
    def create_question(self):
        question = Question(
            id=0,
            question=input("Enter question: "),
            description=input("Enter description: "),
            explanation=input("Enter explanation: "),
            category=input("Enter category: "),
            difficulty=input("Enter difficulty: "),
            answers=[input(f"Enter answer {_+1}: ") for _ in range(4)],
            correct_answers=[input(f"Is answer {_+1} correct? (true/false): ") == 'true' for _ in range(4)]
        )
        saved_question = self.question_repo.create_question(question)
        if saved_question:
            print(f"Question {saved_question.id} created")
            print(f"Question: {saved_question.question}")
            print(f"Description: {saved_question.description}")
            print(f"Explanation: {saved_question.explanation}")
            print(f"Category: {saved_question.category}")
            print(f"Difficulty: {saved_question.difficulty}")
            print("Answers:")
            for i, (answer, correct) in enumerate(zip(question.answers, question.correct_answers)):
                print(f"{i+1}. {answer} ({'Right' if correct else 'Wrong'})")
            self.press_to_continue()
        else:
            print("Failed to create question")
        self.create_menu()

    def read_menu(self):
        self.clear_screen()
        print("Read Menu")
        print("1. Read all Users")
        print("2. Read User by Id")
        print("3. Read all Questions")
        print("4. Read Question by Id")
        print("5. Read all Games")
        print("6. Read Game by Id")
        print("7. Back")
        choice = input("Enter your choice: ")
        if choice == '1':
            self.read_users()
        elif choice == '2':
            self.read_user()
        elif choice == '3':
            self.read_questions()
        elif choice == '4':
            self.read_question()
        elif choice == '5':
            self.read_games()
        elif choice == '6':
            self.read_game()
        elif choice == '7':
            self.db_menu()
    
    def read_users(self):
        users = self.user_repo.get_all_users()
        print("Users:")
        for user in users:
            print(f"{user.id}: {user.username}")
        self.press_to_continue()
        self.read_menu()

    def read_user(self):
        user_id = int(input("Enter user ID: "))
        user = self.user_repo.get_user_by_id(user_id)
        if user:
            print(f"User {user.id}: {user.username}")
        else:
            print("User not found")
        self.press_to_continue()
        self.read_menu()
    
    def read_questions(self):
        questions = self.question_repo.get_all_questions()
        print("Questions:")
        for question in questions:
            print(f"{question.id}: {question.question}")
        self.press_to_continue()
        self.read_menu()
    
    def read_question(self):
        question_id = int(input("Enter question ID: "))
        question = self.question_repo.get_question_by_id(question_id)
        if question:
            print(f"Question {question.id}: {question.question}")
            print(f"Description: {question.description}")
            print(f"Explanation: {question.explanation}")
            print(f"Category: {question.category}")
            print(f"Difficulty: {question.difficulty}")
            print("Answers:")
            for i, (answer, correct) in enumerate(zip(question.answers, question.correct_answers)):
                print(f"{i+1}. {answer} ({'Right' if correct else 'Wrong'})")
        else:
            print("Question not found")
        self.press_to_continue()
        self.read_menu()

    def read_games(self):
        games = self.game_repo.get_all_games()
        print("Games:")
        for game in games:
            print(f"Game {game.id}: User: {game.user_id}, Score: {game.score}/{game.score}, Played on: {game.created_at}")
        self.press_to_continue()
        self.read_menu()
    
    def read_game(self):
        game_id = int(input("Enter game ID: "))
        game = self.game_repo.get_game_by_id(game_id)
        game_questions = self.game_repo.get_game_questions(game_id)
        if game:
            print(f"Game {game.id}: User: {game.user_id}, Score: {game.score}/{game.score}, Played on: {game.created_at}")
        else:
            print("Game not found")
        if game_questions:
            print("Questions:")
            for game_question in game_questions:
                question = self.question_repo.get_question_by_id(game_question.question_id)
                print(f"Question {question.id}: {question.question}")
                print("Answers:")
                for i, (answer, correct) in enumerate(zip(question.answers, question.correct_answers)):
                    print(f"{i+1}. {answer} ({'Right' if correct else 'Wrong'})")
                print(f"Selected answer: {game_question.selected_answer_index + 1} {'(Correct)' if game_question.is_correct else '(Wrong)'}")
        self.press_to_continue()
        self.read_menu()
    
    def update_menu(self):
        self.clear_screen()
        print("Update Menu")
        print("1. Update Question")
        print("2. Back")
        choice = input("Enter your choice: ")
        if choice == '1':
            self.update_question()
        elif choice == '2':
            self.press_to_continue()
            self.db_menu()
        else:
            print("Invalid choice")
            self.press_to_continue()
            self.update_menu()
    
    def update_question(self):
        question_id = int(input("Enter question ID: "))
        question = self.question_repo.get_question_by_id(question_id)
        if not question:
            print("Question not found")
            self.press_to_continue()
            self.update_menu()
            return
        
        print("Update Question")
        print("If you do not want to update a field, leave it empty")

        print(f"Current question: {question.question}")
        new_question = input("Enter new question: ")
        if new_question:
            question.question = new_question
        print(f"Current description: {question.description}")
        new_description = input("Enter new description: ")
        if new_description:
            question.description = new_description
        print(f"Current explanation: {question.explanation}")
        new_explanation = input("Enter new explanation: ")
        if new_explanation:
            question.explanation = new_explanation
        print(f"Current category: {question.category}")
        new_category = input("Enter new category: ")
        if new_category:
            question.category = new_category
        print(f"Current difficulty: {question.difficulty}")
        new_difficulty = input("Enter new difficulty: ")
        if new_difficulty:
            question.difficulty = new_difficulty
        print("Current answers:")
        for i, (answer, correct) in enumerate(zip(question.answers, question.correct_answers)):
            print(f"{i+1}. {answer} ({'Right' if correct else 'Wrong'})")
        new_answers = [input(f"Enter new answer {_+1}: ") for _ in range(4)]
        new_correct_answers = [input(f"Is answer {_+1} correct? (true/false): ") == 'true' for _ in range(4)]
        if new_answers:
            question.answers = new_answers
        if new_correct_answers:
            question.correct_answers = new_correct_answers
        
        updated_question = self.question_repo.update_question(question)
        if updated_question:
            print(f"Question {updated_question.id} updated")
            print(f"Question: {updated_question.question}")
            print(f"Description: {updated_question.description}")
            print(f"Explanation: {updated_question.explanation}")
            print(f"Category: {updated_question.category}")
            print(f"Difficulty: {updated_question.difficulty}")
            print("Answers:")
            for i, (answer, correct) in enumerate(zip(question.answers, question.correct_answers)):
                print(f"{i+1}. {answer} ({'Right' if correct else 'Wrong'})")
            self.press_to_continue()
        else:
            print("Failed to update question")
        self.update_menu()
    
    def delete_menu(self):
        self.clear_screen()
        print("Delete Menu")
        print("1. Delete Game")
        print("2. Back")
        choice = input("Enter your choice: ")
        if choice == '1':
            self.delete_game()
        elif choice == '2':
            self.db_menu()
        else:
            print("Invalid choice")
            self.delete_menu()
    
    def delete_game(self):
        game_id = int(input("Enter game ID: "))
        game = self.game_repo.get_game(game_id)
        if not game:
            print("Game not found")
            self.press_to_continue()
            self.delete_menu()
            return
        
        if self.game_repo.delete_game(game_id):
            print(f"Game {game_id} deleted")
        else:
            print("Failed to delete game")
        self.press_to_continue()
        self.delete_menu()

    def log_user(self) -> Optional[User]:
        while True:
            username = input("Enter your username: ")
            if not username:
                print("Username cannot be empty")
            else:
                user = self.user_repo.get_user_by_username(username)
                if user:
                    print(f"Welcome back, {username}!")
                    return user
                else:
                    print("User not found, would you like to register?")
                    register = input("(y/n): ")
                    if register.lower() == 'y':
                        print(f"Registering new user: {username}")
                        print(f"Welcome, {username}!")
                        return self.register_user(username)
                    else:
                        break
        return None
        
    def register_user(self, username: str) -> Optional[User]:
        try:
            user = self.user_repo.create_user(username)
            logger.info(f"Created new user: {username}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return None
        
    def start_game(self, user_id: int, num_rounds: int) -> Optional[Game]:
        logger.info(f"Starting new game for user {user_id}")
        try:
            logger.debug(f"Fetching user {user_id}")
            # Create new game
            game = self.game_repo.create_game(user_id, num_rounds)
            logger.debug(f"Created game {game}")
            if not game:
                return None
                
            # Fetch questions from API
            logger.debug(f"Fetching questions from API")
            self.game_logic.start_new_game(num_questions=num_rounds)
            
            logger.debug(self.game_logic.questions)
            # Store questions in database
            logger.debug(f"Storing questions in database")
            question_ids = []
            for q in self.game_logic.questions:
                # Create question object
                logger.debug(f"Creating question object")
                question = Question(
                    id=0,  # Will be set by database
                    question=q.get('question', ''),
                    description=q.get('description', ''),
                    explanation=q.get('explanation', ''),
                    category=q.get('category', 'general'),
                    difficulty=q.get('difficulty', 'medium'),
                    answers=[q['answers'].get(f'answer_{l}', '') for l in "abcdef" if q['answers'].get(f'answer_{l}') is not None],
                    correct_answers=[q['correct_answers'].get(f'answer_{l}_correct', 'false') == 'true' for l in "abcdef"]
                )
                print(question)
                
                # Save question
                logger.debug(f"Saving question to database")
                saved_question = self.question_repo.create_question(question)
                question_ids.append(saved_question.id)
            
            # Link questions to game
            self.game_repo.add_game_questions(game.id, question_ids)
            
            logger.info(f"Started new game {game.id} for user {user_id}")
            return game
            
        except Exception as e:
            logger.error(f"Failed to start game: {str(e)}")
            return None
        
    # def answer_question(self, game_id: int, question_id: int, 
    #                    answer_index: int) -> bool:
    #     try:
    #         # Get game and validate
    #         game = self.game_repo.get_game(game_id)
    #         if not game:
    #             logger.error(f"Game {game_id} not found")
    #             return False
                
    #         # Record answer
    #         conn = self.db.get_connection()
    #         try:
    #             with conn.cursor() as cur:
    #                 cur.execute("""
    #                     UPDATE game_questions 
    #                     SET selected_answer_index = %s,
    #                         answered_at = %s
    #                     WHERE game_id = %s AND question_id = %s
    #                     RETURNING id
    #                 """, (answer_index, datetime.now(), game_id, question_id))
    #                 conn.commit()
    #                 return True
    #         finally:
    #             self.db.return_connection(conn)
                
    #     except Exception as e:
    #         logger.error(f"Failed to record answer: {str(e)}")
    #         return False
        
    def close(self):
        try:
            self.db.close_all_connections()
            logger.info("Closed all database connections")
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")
            
    def display_question(self, question: Question) -> None:
        print("\n" + "="*50)
        print(f"Question: {question.question}")
        if question.description:
            print(f"Description: {question.description}")
        print("\nAnswers:")
        for i, answer in enumerate(question.answers):
            print(f"{i+1}. {answer}")
        print(question.correct_answers)
            
    def play_game(self, game_id: int) -> None:
        try:
            game = self.game_repo.get_game(game_id)
            if not game:
                logger.error("Game not found")
                return

            questions = self.game_repo.get_game_questions(game_id)
            total_correct = 0

            for i, game_question in enumerate(questions, 1):
                question = self.question_repo.get_question_by_id(game_question.question_id)
                if not question:
                    continue

                self.display_question(question)

                answers_num = len(question.answers)
                
                while True:
                    try:
                        answer = int(input(f"\nEnter your answer (1-{answers_num}): ")) - 1 #0 indexing the answer
                        if 0 <= answer <= answers_num - 1:
                            break
                        print("Please enter a valid answer number")
                    except ValueError:
                        print("Please enter a number")

                is_correct = question.correct_answers[answer]
                
                # Update game question
                self.question_repo.answer_question(game_id, question.id, answer, is_correct)
                
                if is_correct:
                    total_correct += 1
                    print("\n✅ Correct!")
                else:
                    print("\n❌ Wrong!")
                    print(f"The correct answer(s) was(were):")
                    for idx in range(answers_num):
                        if question.correct_answers[idx]:
                            print(f"{idx+1}. {question.answers[idx]}")
                
                if question.explanation:
                    print(f"Explanation: {question.explanation}")
                
                print(f"\nCurrent score: {total_correct}/{i}")

            # Update final score
            self.update_game_score(game_id, total_correct)
            print(f"\nGame Over! Final score: {total_correct}/{len(questions)}")

        except Exception as e:
            logger.error(f"Error during game play: {str(e)}")
            
    def update_game_score(self, game_id: int, score: int) -> bool:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE games 
                    SET score = %s
                    WHERE id = %s
                """, (score, game_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update score: {str(e)}")
            return False
        finally:
            self.db.return_connection(conn)
def main():
    app = QuizApplication("Nu4Q4o5IFPwgTUWcEmgWUpwyK06B3yGg3TbmkkTM")
    try:
        app.main_menu()

        user = app.log_user()
        if user is None:
            print("Goodbye!")
        else:
            while True:
                while True:
                    try:
                        rounds = int(input("How many questions would you like? (1-10): "))
                        if 1 <= rounds <= 10:
                            break
                        print("Please enter a number between 1 and 10")
                    except ValueError:
                        print("Please enter a valid number")
                game = app.start_game(user.id, rounds)
                if game:
                    app.play_game(game.id)
                    play_again = input("\nWould you like to play again? (y/n): ")
                    if play_again.lower() != 'y':
                        print("Thanks for playing!")
                        break
    finally:
        app.close()
        
if __name__ == '__main__':
    main()