from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import math
from . import db_manager  # Import db_manager here


class Category(Enum):
    FASHION = "Fashion"
    SPORTS = "Sports"
    FILMS = "Films"
    TECHNOLOGY = "Technology"


class POST:
    """
    POST class for social media posts
    Manages post content, reactions, categories, and scoring
    """

    def __init__(self, user_id: int = 0, content: str = ""):
        self.timestamp = datetime.now()
        self.user_id = user_id
        self.post_id = 0
        self.score = 0
        self.content = content
        self.categories: List[Category] = []
        self.like_count = 0
        self.dislike_count = 0
        self.comment_count = 0

    @staticmethod
    def get_by_id(post_id: int) -> Optional[Dict]:
        """Fetch a post dictionary by ID via db_manager"""
        return db_manager.read_post(post_id)

    # ===== Setters =====
    def set_user_id(self, user_id: int) -> None:
        self.user_id = user_id

    def set_post_id(self, post_id: int) -> None:
        self.post_id = post_id

    def set_score(self, score: int) -> None:
        self.score = score

    def set_content(self, content: str) -> None:
        self.content = content

    def set_timestamp(self, timestamp: datetime) -> None:
        self.timestamp = timestamp

    def set_like_count(self, like_count: int) -> None:
        self.like_count = like_count

    def set_dislike_count(self, dislike_count: int) -> None:
        self.dislike_count = dislike_count

    def set_comment_count(self, comment_count: int) -> None:
        self.comment_count = comment_count

    def set_categories(self, categories: List[Category]) -> None:
        self.categories = categories

    # ===== Getters =====
    def get_user_id(self) -> int:
        return self.user_id

    def get_post_id(self) -> int:
        return self.post_id

    def get_score(self) -> int:
        return self.score

    def get_content(self) -> str:
        return self.content

    def get_categories(self) -> List[Category]:
        return self.categories

    def get_like_count(self) -> int:
        return self.like_count

    def get_dislike_count(self) -> int:
        return self.dislike_count

    def get_comment_count(self) -> int:
        return self.comment_count

    def get_timestamp(self) -> datetime:
        return self.timestamp

    # ===== Classification =====
    def classify(self) -> None:
        text = self.content.lower()
        scores = {Category.FASHION: 0, Category.SPORTS: 0, Category.FILMS: 0, Category.TECHNOLOGY: 0}

        if "fashion" in text: scores[Category.FASHION] += 2
        if "style" in text or "clothes" in text or "outfit" in text: scores[Category.FASHION] += 1

        if "football" in text or "exercise" in text: scores[Category.SPORTS] += 2
        if "match" in text or "goal" in text or "gym" in text: scores[Category.SPORTS] += 1

        if "movie" in text: scores[Category.FILMS] += 2
        if "film" in text or "cinema" in text or "actor" in text or "star" in text: scores[Category.FILMS] += 1

        if "ai" in text or "computer" in text: scores[Category.TECHNOLOGY] += 2
        if "software" in text or "app" in text or "tech" in text: scores[Category.TECHNOLOGY] += 1

        THRESHOLD = 2
        self.categories = [cat for cat, score in scores.items() if score >= THRESHOLD]

    # ===== Reactions (In-Memory updates) =====
    def add_like(self, user_id: int) -> None:
        self.like_count += 1
        self.score += 1

    def add_dislike(self, user_id: int) -> None:
        self.dislike_count += 1
        self.score -= 1

    def add_comment(self, user_id: int, comment: str) -> None:
        self.comment_count += 1

    # ===== Scoring =====
    def update_score(self) -> int:
        popularity_score = (self.like_count * 5) + (self.comment_count * 10) - (self.dislike_count * 5)
        now = datetime.now()
        duration = (now - self.timestamp).total_seconds() / 3600
        time_score = 1000 / math.pow(duration + 1, 2)
        self.score = int(time_score + popularity_score)
        return self.score

    # ===== Utility Methods =====
    def to_dict(self) -> dict:
        return {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'timestamp': self.timestamp,
            'categories': [cat.value for cat in self.categories],
            'like_count': self.like_count,
            'dislike_count': self.dislike_count,
            'comment_count': self.comment_count,
            'score': self.score
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'POST':
        post = cls(user_id=data.get('user_id', 0), content=data.get('content', ''))
        post.set_post_id(data.get('post_id', 0))
        post.set_score(data.get('score', 0))

        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], datetime):
                post.set_timestamp(data['timestamp'])
            elif isinstance(data['timestamp'], str):
                try:
                    post.set_timestamp(datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S"))
                except ValueError:
                    pass

        if 'categories' in data:
            categories = []
            for cat_str in data['categories']:
                try:
                    if isinstance(cat_str, str):
                        categories.append(Category(cat_str))
                    elif isinstance(cat_str, Category):
                        categories.append(cat_str)
                except ValueError:
                    pass
            post.set_categories(categories)

        post.set_like_count(data.get('like_count', 0))
        post.set_dislike_count(data.get('dislike_count', 0))
        post.set_comment_count(data.get('comment_count', 0))
        return post

    def __str__(self) -> str:
        return f"POST(id={self.post_id}, user={self.user_id}, content='{self.content[:50]}...', score={self.score})"

    def __repr__(self) -> str:
        return f"POST(post_id={self.post_id}, user_id={self.user_id}, score={self.score})"