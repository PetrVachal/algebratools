from enum import Enum


class Intersections(Enum):
    EMPTY = 0  # (...) (...) | (...)(...) | (...)[...) | (...](...) ok
    ONE_NUMBER = 1  # (...][...) ok
    PARTIAL_OVERLAP = 2  # (..(.)..) ok
    INNER_LEFT_OVERLAP_WITHOUT_LOWER = 3  # ((...)...) | ([...)...) | [(...)...) ok
    INNER_LEFT_OVERLAP = 4  # [[...)...) ok
    INNER_OVERLAP = 5  # (...(...)...) ok
    EQUALITY_WITHOUT_LIMITS = 6  # ((...)) | ((...)] | ((...]) | ([...)) | ([...)] | ([...]) | [(...)) | [(...)] | [(...]) ok
    EQUALITY_WITHOUT_LOWER = 7  # ((...]] | ([...]] | [(...]] ok
    EQUALITY_WITHOUT_UPPER = 8  # [[...)) | [[...)] | [[...]) ok
    EQUALITY = 9  # [[...]] ok
    INNER_RIGHT_OVERLAP_WITHOUT_UPPER = 10  # (...(...)) | (...(...)] | (...(...]) ok
    INNER_RIGHT_OVERLAP = 11  # (...(...]] ok
    UNKNOWN_INTERSECTION = -1  # ???
