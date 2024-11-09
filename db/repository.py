from conn import DatabaseConnection
from schema import Question, Game
from typing import List, Optional

class QuestionRepository:
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    def create_question(self, question: Question, answers: List[tuple[str, bool]], tags: List[str]) -> Optional[Question]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                # Insert question
                cur.execute("""
                    INSERT INTO questions (question, description, explanation, tip, category_id, difficulty_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    question.question, question.description, question.explanation,
                    question.tip, question.category_id, question.difficulty_id
                ))
                question_id = cur.fetchone()[0]

                # Insert answers
                for idx, (answer_text, is_correct) in enumerate(answers):
                    cur.execute("""
                        WITH inserted_answer AS (
                            INSERT INTO answers (text)
                            VALUES (%s)
                            RETURNING id
                        )
                        INSERT INTO question_answers (question_id, answer_id, is_correct, order_index)
                        SELECT %s, id, %s, %s
                        FROM inserted_answer
                    """, (answer_text, question_id, is_correct, idx))

                # Insert tags
                for tag_name in tags:
                    cur.execute("""
                        WITH inserted_tag AS (
                            INSERT INTO tags (name)
                            VALUES (%s)
                            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                            RETURNING id
                        )
                        INSERT INTO question_tags (question_id, tag_id)
                        SELECT %s, id
                        FROM inserted_tag
                    """, (tag_name, question_id))

                conn.commit()
                return self.get_question_by_id(question_id)
        except Exception as e:
            conn.rollback()
            print(f"Error creating question: {e}")
            return None
        finally:
            self.db.return_connection(conn)

    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, question, description, explanation, tip, category_id, difficulty_id
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
                    RETURNING id, user_id, rounds, score, created_at
                """, (user_id, rounds))
                conn.commit()
                result = cur.fetchone()
                if result:
                    return Game(*result)
        except Exception as e:
            conn.rollback()
            print(f"Error creating game: {e}")
            return None
        finally:
            self.db.return_connection(conn)

    def answer_question(self, game_id: int, question_id: int, answer_id: int) -> bool:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                # Check if answer is correct
                cur.execute("""
                    SELECT is_correct 
                    FROM question_answers 
                    WHERE question_id = %s AND answer_id = %s
                """, (question_id, answer_id))
                result = cur.fetchone()
                is_correct = result[0] if result else False

                # Update game_questions
                cur.execute("""
                    UPDATE game_questions 
                    SET selected_answer_id = %s,
                        is_correct = %s,
                        answered_at = CURRENT_TIMESTAMP
                    WHERE game_id = %s AND question_id = %s
                """, (answer_id, is_correct, game_id, question_id))

                # Update game score if answer is correct
                if is_correct:
                    cur.execute("""
                        UPDATE games 
                        SET score = score + 1
                        WHERE id = %s
                    """, (game_id,))

                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error answering question: {e}")
            return False
        finally:
            self.db.return_connection(conn)