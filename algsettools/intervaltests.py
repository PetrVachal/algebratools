from enum import Enum
from random import choice, randint


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


def get_intersection_type(set1: str, set2: str) -> Intersections:
    left_closed_br, right_closed_br = "[", "]"
    sep: str = ","
    L1_closed: bool = True if set1.startswith(left_closed_br) else False
    R1_closed: bool = True if set1.endswith(right_closed_br) else False
    L2_closed: bool = True if set2.startswith(left_closed_br) else False
    R2_closed: bool = True if set2.endswith(right_closed_br) else False
    L1, R1 = set1[1:-1].split(sep)
    L2, R2 = set2[1:-1].split(sep)
    L1, R1, L2, R2 = int(L1), int(R1), int(L2), int(R2)
    if R1 < L2 or R2 < L1:
        return Intersections.EMPTY
    if R1 == L2 or R2 == L1:
        if (R1 == L2 and R1_closed and L2_closed) or (R2 == L1 and R2_closed and L1_closed):
            return Intersections.ONE_NUMBER
        return Intersections.EMPTY
    if L1 == R1 or L2 == R2:
        return Intersections.ONE_NUMBER
    if (L1 < L2 and R1 > R2) or (L2 < L1 and R2 > R1):
        return Intersections.INNER_OVERLAP
    if (L2 < R1 < R2 and L1 < L2 < R1) or (L1 < R2 < R1 and L2 < L1 < R2):
        return Intersections.PARTIAL_OVERLAP
    if (L1 == L2 and R1 < R2) or (L2 == L1 and R2 < R1):
        if L1_closed and L2_closed:
            return Intersections.INNER_LEFT_OVERLAP
        return Intersections.INNER_LEFT_OVERLAP_WITHOUT_LOWER
    if L1 == L2 and R1 == R2:
        if L1_closed and L2_closed:
            if R1_closed and R2_closed:
                return Intersections.EQUALITY
            return Intersections.EQUALITY_WITHOUT_UPPER
        if R1_closed and R2_closed:
            return Intersections.EQUALITY_WITHOUT_LOWER
        return Intersections.EQUALITY_WITHOUT_LIMITS
    if (L1 < L2 and R1 == R2) or (L2 < L1 and R2 == R1):
        if R1_closed and R2_closed:
            return Intersections.INNER_RIGHT_OVERLAP
        return Intersections.INNER_RIGHT_OVERLAP_WITHOUT_UPPER
    return Intersections.UNKNOWN_INTERSECTION


def generate_interval(mini: int, maxi: int) -> str:
    sep: str = ","
    left_brackets: list = ["(", "["]
    right_brackets: list = [")", "]"]
    lower_limit: int = randint(mini, maxi)
    upper_limit: int = randint(lower_limit, maxi)
    if lower_limit == upper_limit:
        left_bracket, right_bracket = "[", "]"
    else:
        left_bracket: str = choice(left_brackets)
        right_bracket: str = choice(right_brackets)
    return f"{left_bracket}{lower_limit}{sep}{upper_limit}{right_bracket}"


if __name__ == '__main__':
    while True:
        interval1: str = generate_interval(0, 10)
        interval2: str = generate_interval(0, 10)
        try:
            intersection_type = get_intersection_type(interval1, interval2)
            if intersection_type != Intersections.EMPTY:
                reaction: str = input(f"{interval1} && {interval2} <=> {intersection_type}")
                if reaction == "exit":
                    break
        except Exception as err:
            print(err)
