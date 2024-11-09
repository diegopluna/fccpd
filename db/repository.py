from .conn import DatabaseConnection
from .schema import Question, Game, User, GameQuestion
from typing import List, Optional

class UserRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_user(self, username: str) -> Optional[User]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (username)
                    VALUES (%s)
                    RETURNING id
                """, (username,))
                user_id = cur.fetchone()[0]
                conn.commit()
                return User(id=user_id, username=username)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db.return_connection(conn)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
                result = cur.fetchone()
                return User(id=result[0], username=result[1]) if result else None
        finally:
            self.db.return_connection(conn)

class QuestionRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    def create_question(self, question: Question) -> Optional[Question]:
        conn = self.db.get_connection()
        try:
            print("Creating question")
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO questions (
                        question, description, explanation, 
                        category, difficulty, answers, correct_answers
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    question.question,
                    question.description,
                    question.explanation,
                    question.category,
                    question.difficulty,
                    question.answers,
                    question.correct_answers
                ))
                print("Question created")
                question_id = cur.fetchone()[0]
                conn.commit()
                
                # Update the question id and return
                question.id = question_id
                return question
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db.return_connection(conn)

    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, question, description, explanation, category, difficulty, answers, correct_answers
                    FROM questions
                    WHERE id = %s
                """, (question_id,))
                result = cur.fetchone()
                if result:
                    return Question(*result)
                return None
        finally:
            self.db.return_connection(conn)
            
class GameRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_game(self, user_id: int, rounds: int) -> Optional[Game]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO games (user_id, rounds, score)
                    VALUES (%s, %s, 0)
                    RETURNING id, created_at
                """, (user_id, rounds))
                game_id, created_at = cur.fetchone()
                conn.commit()
                return Game(id=game_id, user_id=user_id, rounds=rounds, 
                          score=0, created_at=created_at)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db.return_connection(conn)
    
    def add_game_questions(self, game_id: int, question_ids: List[int]) -> bool:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                for question_id in question_ids:
                    cur.execute("""
                        INSERT INTO game_questions (game_id, question_id)
                        VALUES (%s, %s)
                    """, (game_id, question_id))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.db.return_connection(conn)
    
    def get_game(self, game_id: int) -> Optional[Game]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, user_id, rounds, score, created_at 
                    FROM games WHERE id = %s
                """, (game_id,))
                result = cur.fetchone()
                if result:
                    return Game(
                        id=result[0],
                        user_id=result[1],
                        rounds=result[2],
                        score=result[3],
                        created_at=result[4]
                    )
                return None
        finally:
            self.db.return_connection(conn)
    
    def get_game_questions(self, game_id: int) -> List[GameQuestion]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, game_id, question_id, selected_answer_index, 
                           is_correct, answered_at
                    FROM game_questions 
                    WHERE game_id = %s
                """, (game_id,))
                return [
                    GameQuestion(
                        id=row[0],
                        game_id=row[1],
                        question_id=row[2],
                        selected_answer_index=row[3],
                        is_correct=row[4],
                        answered_at=row[5]
                    )
                    for row in cur.fetchall()
                ]
        finally:
            self.db.return_connection(conn)