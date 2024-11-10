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
        
    def answer_question(self, game_id: int, question_id: int, 
                       answer_index: int) -> bool:
        try:
            # Get game and validate
            game = self.game_repo.get_game(game_id)
            if not game:
                logger.error(f"Game {game_id} not found")
                return False
                
            # Record answer
            conn = self.db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE game_questions 
                        SET selected_answer_index = %s,
                            answered_at = %s
                        WHERE game_id = %s AND question_id = %s
                        RETURNING id
                    """, (answer_index, datetime.now(), game_id, question_id))
                    conn.commit()
                    return True
            finally:
                self.db.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to record answer: {str(e)}")
            return False
        
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
                        answer = int(input(f"\nEnter your answer (1-{answers_num}): "))
                        if 1 <= answer <= answers_num:
                            break
                        print("Please enter a valid answer number")
                    except ValueError:
                        print("Please enter a number")

                # Convert to 0-based index
                answer_key = f"answer_{answer}"
                correct_key = f"correct_answer_{answer}_correct"
                is_correct = question.correct_answers.get(correct_key, False)
                
                # Update game question
                self.answer_question(game_id, question.id, answer_key)
                
                if is_correct:
                    total_correct += 1
                    print("\n✅ Correct!")
                else:
                    print("\n❌ Wrong!")
                    correct_answers = [k for k, v in question.correct_answers.items() 
                                if v and k.startswith("correct_answer_")]
                    if correct_answers:
                        correct_num = correct_answers[0].split("_")[2]
                        correct_text = question.answers[f"answer_{correct_num}"]
                        print(f"The correct answer was: {correct_text}")
                    
                
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
        # Example usage
        user = app.log_user()
        if user is None:
            print("Goodbye!")
        else:
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
    finally:
        app.close()
        
if __name__ == '__main__':
    main()