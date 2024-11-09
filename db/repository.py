from .schema import User, Question, Game
from typing import TypeVar, Generic, Optional, List, Callable
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pydantic.types import List

class RepositoryError(Exception):
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def create(self, instance: T) -> Optional[T]:
        with self.session_factory() as session:
            try:
                session.add(instance)
                session.commit()
                session.refresh(instance)
                return instance
            except SQLAlchemyError as e:
                session.rollback()
                raise RepositoryError(f"Create operation failed: {str(e)}")

    def get_by_id(self, id: int) -> Optional[T]:
        with self.session_factory() as session:
            try:
                return session.query(self.model).filter(self.model.id == id).first()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Read operation failed: {str(e)}")

    def delete(self, id: int) -> bool:
        with self.session_factory() as session:
            try:
                instance = self.get_by_id(id)
                if instance:
                    session.delete(instance)
                    session.commit()
                    return True
                return False
            except SQLAlchemyError as e:
                session.rollback()
                raise RepositoryError(f"Delete operation failed: {str(e)}")

class UserRepository(BaseRepository[User]):
    model = User
    
    def get_by_username(self, username: str) -> Optional[User]:
        with self.session_factory() as session:
            try:
                return session.query(User).filter(User.username == username).first()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get user by username: {str(e)}", e)
    
    def update(self, user: User) -> Optional[User]:
        with self.session_factory() as session:
            try:
                # `merge` retorna a instância atualizada que está na sessão
                updated_user = session.merge(user)
                session.commit()
                return updated_user
            except SQLAlchemyError as e:
                session.rollback()
                raise RepositoryError(f"Failed to update user: {str(e)}", e)



class QuestionRepository(BaseRepository[Question]):
    model = Question

    def get_by_category(self, category: str) -> List[Question]:
        with self.session_factory() as session:
            try:
                return session.query(Question).filter(Question.category == category).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get questions by category: {str(e)}", e)
    
    def get_by_difficulty(self, difficulty: str) -> List[Question]:
        with self.session_factory() as session:
            try:
                return session.query(Question).filter(Question.difficulty == difficulty).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get questions by difficulty: {str(e)}", e)
    
    def get_by_tag(self, tag):
        with self.session_factory() as session:
            try:
                return session.query(Question).filter(Question.tags.contains(tag)).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get questions by tag: {str(e)}", e)
    
    def get_all(self):
        with self.session_factory() as session:
            try:
                return session.query(Question).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get all questions: {str(e)}", e)
    
    
class GameRepository(BaseRepository[Game]):
    model = Game
        
    def get_all(self):
        with self.session_factory() as session:
            try:
                return session.query(Game).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get all games: {str(e)}", e)
        
    def get_by_user(self, user: User):
        with self.session_factory() as session:
            try:
                return session.query(Game).filter(Game.user_id == user.id).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get games by user: {str(e)}", e)
    
    def get_last_game_by_user(self, user: User):
        with self.session_factory() as session:
            try:
                return session.query(Game).filter(Game.user_id == user.id).order_by(Game.id.desc()).first()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get last game by user: {str(e)}", e)
    
    def get_ordered_by_rounds(self):
        with self.session_factory() as session:
            try:
                return session.query(Game).order_by(Game.rounds).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get games ordered by rounds: {str(e)}", e)
    
    def get_ordered_by_score(self):
        with self.session_factory() as session:
            try:
                return session.query(Game).order_by(Game.score).all()
            except SQLAlchemyError as e:
                raise RepositoryError(f"Failed to get games ordered by score: {str(e)}", e)
