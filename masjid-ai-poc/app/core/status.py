from enum import Enum


class Status(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
