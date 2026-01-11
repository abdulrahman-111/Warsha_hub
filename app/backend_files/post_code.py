from datetime import datetime
from typing import List, Optional
from enum import Enum
import math
import re

from fontTools.misc.classifyTools import classify


class Category(Enum):
    """Enumeration for post categories matching user interests"""

    TECHNOLOGY = "Technology"
    SPORTS = "Sports"
    MUSIC = "Music"
    ART = "Art"
    READING = "Reading"
    TRAVEL = "Travel"
    COOKING = "Cooking"
    GAMING = "Gaming"
    PHOTOGRAPHY = "Photography"
    FITNESS = "Fitness"
    FASHION = "Fashion"
    FILMS = "Films"



class POST:
    """
    POST class for social media posts
    Manages post content, reactions, categories, and scoring
    """

    def __init__(self, user_id: int = 0, content: str = ""):
        """
        Initialize a new POST object

        Args:
            user_id: ID of the user who created the post
            content: Text content of the post
        """
        self.timestamp = datetime.now()
        self.user_id = user_id
        self.post_id = 0
        self.score = 0
        self.content = content
        self.categories: List[Category] = []
        self.like_count = 0
        self.dislike_count = 0
        self.comment_count = 0

    # ===== Setters =====

    def set_user_id(self, user_id: int) -> None:
        """Set the user ID (author ID)"""
        self.user_id = user_id

    def set_post_id(self, post_id: int) -> None:
        """Set the post ID (typically set by database)"""
        self.post_id = post_id

    def set_score(self, score: int) -> None:
        """Set the post score"""
        self.score = score

    def set_content(self, content: str) -> None:
        """Set the post content"""
        self.content = content

    def set_timestamp(self, timestamp: datetime) -> None:
        """Set the timestamp (typically from database)"""
        self.timestamp = timestamp

    def set_like_count(self, like_count: int) -> None:
        """Set the like count"""
        self.like_count = like_count

    def set_dislike_count(self, dislike_count: int) -> None:
        """Set the dislike count"""
        self.dislike_count = dislike_count

    def set_comment_count(self, comment_count: int) -> None:
        """Set the comment count"""
        self.comment_count = comment_count

    def set_categories(self) -> None:
        """Set the categories list"""
        classify()

    # ===== Getters =====

    def get_user_id(self) -> int:
        """Get the user ID"""
        return self.user_id

    def get_post_id(self) -> int:
        """Get the post ID"""
        return self.post_id

    def get_score(self) -> int:
        """Get the post score"""
        return self.score

    def get_content(self) -> str:
        """Get the post content"""
        return self.content

    def get_categories(self) -> List[Category]:
        """Get the categories list"""
        return self.categories

    def get_like_count(self) -> int:
        """Get the like count"""
        return self.like_count

    def get_dislike_count(self) -> int:
        """Get the dislike count"""
        return self.dislike_count

    def get_comment_count(self) -> int:
        """Get the comment count"""
        return self.comment_count

    def get_timestamp(self) -> datetime:
        """Get the timestamp"""
        return self.timestamp

    # ===== Classification =====

    import re

    def classify(self) -> None:
        """
        Automatically classify the post into categories based on keywords,
        using regex to catch variations and word boundaries.
        """
        # Lowercase and remove punctuation for consistency
        text = re.sub(r'[^\w\s]', '', self.content.lower())

        # Define regex patterns for each category
        patterns = {
            Category.TECHNOLOGY: [r'\bai\b', r'\bcomputer\b', r'\bsoftware\b', r'\bapp\b', r'\btech\b'],
            Category.SPORTS: [r'\bfootball\b', r'\bexercise\b', r'\bmatch\b', r'\bgoal\b', r'\bgym\b'],
            Category.MUSIC: [r'\bmusic\b', r'\bsong\b', r'\bband\b', r'\bconcert\b', r'\balbum\b'],
            Category.ART: [r'\bart\b', r'\bpainting\b', r'\bsculpture\b', r'\bdrawing\b', r'\bexhibition\b'],
            Category.READING: [r'\bbook\b', r'\breading\b', r'\bnovel\b', r'\bliterature\b', r'\bauthor\b'],
            Category.TRAVEL: [r'\btravel\b', r'\btrip\b', r'\bvacation\b', r'\btour\b', r'\bdestination\b'],
            Category.COOKING: [r'\bcooking\b', r'\brecipe\b', r'\bkitchen\b', r'\bbaking\b', r'\bdish\b'],
            Category.GAMING: [r'\bgame\b', r'\bgamer\b', r'\bconsole\b', r'\bpc game\b', r'\besports\b'],
            Category.PHOTOGRAPHY: [r'\bphoto\b', r'\bphotography\b', r'\bcamera\b', r'\bsnapshot\b', r'\bportrait\b'],
            Category.FITNESS: [r'\bfitness\b', r'\bworkout\b', r'\btraining\b', r'\bexercise\b', r'\bhealth\b'],
            Category.FASHION: [r'\bfashion\b', r'\bstyle\b', r'\bclothes\b', r'\boutfit\b'],
            Category.FILMS: [r'\bmovie\b', r'\bmovies\b', r'\bfilm\b', r'\bcinema\b', r'\bactor\b', r'\bstar\b']
        }

        # Scoring
        THRESHOLD = 2
        scores = {category: 0 for category in Category}

        for category, regex_list in patterns.items():
            for pattern in regex_list:
                matches = re.findall(pattern, text)
                scores[category] += len(matches)  # count matches

        # Assign categories passing threshold
        self.categories = [category for category, score in scores.items() if score >= THRESHOLD]

    # ===== Reactions =====

    def add_like(self, user_id: int) -> None:
        """
        Add a like to the post

        Args:
            user_id: ID of the user who liked the post
        """
        self.like_count += 1
        self.score += 1

    def add_dislike(self, user_id: int) -> None:
        """
        Add a dislike to the post

        Args:
            user_id: ID of the user who disliked the post
        """
        self.dislike_count += 1
        self.score -= 1

    def add_comment(self, user_id: int, comment: str) -> None:
        """
        Add a comment to the post

        Args:
            user_id: ID of the user who commented
            comment: The comment text
        """
        self.comment_count += 1

    # ===== Scoring =====

    def update_score(self) -> int:
        """
        Update and return the post score based on popularity and time decay

        The score calculation uses:
        - Popularity score: likes * 5 + comments * 10 - dislikes * 5
        - Time decay: exponential decay based on post age

        Returns:
            The updated score
        """
        # Calculate popularity score
        popularity_score = (self.like_count * 5) + \
                           (self.comment_count * 10) - \
                           (self.dislike_count * 5)

        # Get current time
        now = datetime.now()

        # Calculate duration in hours
        duration = (now - self.timestamp).total_seconds() / 3600

        # Calculate time score with exponential decay
        # Avoid division by zero by adding 1
        # Use 1000 as a constant to ensure recent posts appear at top
        # Square the duration for faster drop-off (exponential decay)
        time_score = 1000 / math.pow(duration + 1, 2)

        # Update and return the final score
        self.score = int(time_score + popularity_score)
        return self.score

    # ===== Utility Methods =====

    def to_dict(self) -> dict:
        """
        Convert POST object to dictionary for database storage or serialization

        Returns:
            Dictionary representation of the post
        """
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
        """
        Create a POST object from a dictionary

        Args:
            data: Dictionary containing post data

        Returns:
            POST object initialized with the data
        """
        post = cls(
            user_id=data.get('user_id', 0),
            content=data.get('content', '')
        )

        post.set_post_id(data.get('post_id', 0))
        post.set_score(data.get('score', 0))

        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], datetime):
                post.set_timestamp(data['timestamp'])
            elif isinstance(data['timestamp'], str):
                # Parse string timestamp if needed
                try:
                    post.set_timestamp(datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S"))
                except ValueError:
                    pass

        # Convert category strings back to enum
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
        """String representation of the post"""
        return f"POST(id={self.post_id}, user={self.user_id}, content='{self.content[:50]}...', score={self.score})"

    def __repr__(self) -> str:
        """Developer-friendly representation of the post"""
        return f"POST(post_id={self.post_id}, user_id={self.user_id}, score={self.score}, " \
               f"likes={self.like_count}, dislikes={self.dislike_count}, comments={self.comment_count})"