from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import ARRAY
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"
    
class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True)
    question = Column(String(100), nullable=False)
    description = Column(String(100), nullable=False)
    answers = Column(ARRAY(String(100)))
    # multiple_correct_answers = Column(Boolean, nullable=False)
    correct_answers = Column(ARRAY(Boolean))
    explanation = Column(String(100), nullable=False)
    tip = Column(String(100), nullable=True)
    tags = Column(ARRAY(String(100)))
    category = Column(String(100), nullable=False)
    difficulty = Column(String(100))
    
    
class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    rounds = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    questions = Column(ARRAY(Integer))
    
    
# [
#   {
#     "id": 1,
#     "question": "How to delete a directory in Linux?",
#     "description": "delete folder",
#     "answers": {
#       "answer_a": "ls",
#       "answer_b": "delete",
#       "answer_c": "remove",
#       "answer_d": "rmdir",
#       "answer_e": null,
#       "answer_f": null
#     },
#     "multiple_correct_answers": "false",
#     "correct_answers": {
#       "answer_a_correct": "false",
#       "answer_b_correct": "false",
#       "answer_c_correct": "false",
#       "answer_d_correct": "true",
#       "answer_e_correct": "false",
#       "answer_f_correct": "false"
#     },
#     "explanation": "rmdir deletes an empty directory",
#     "tip": null,
#     "tags": [],
#     "category": "linux",
#     "difficulty": "Easy"
#   }
# ]