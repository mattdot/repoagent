from enum import Enum

class CommentCommand(str, Enum):
    APPLY = "/apply"
    REVIEW = "/review"
