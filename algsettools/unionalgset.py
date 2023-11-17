from copy import deepcopy
from typing import Any, List

from algebradata import AlgebraData as Ad
from algsettools import AlgSet, DiscreteAlgSet, IntervalAlgSet
from errormessages import ErrorMessages


class UnionAlgSet(AlgSet):
    """
    Contains a set that is composed of at least two disjoint sets.
    """
    _PREFIX: str = "UnionAlgSet"
    _ERR: str = f"{_PREFIX}Error: "

    _content: list = None

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], self.__class__):
            alg_set = deepcopy(args[0])
        else:
            alg_set = deepcopy(args)
        super().__init__(alg_set)

    def __contains__(self, item):
        for inner_set in self:
            if isinstance(inner_set, item.__class__) and inner_set == item:
                return True
        return False

    def __eq__(self, other):
        eq: bool = super().__eq__(other)
        if not eq:
            return False
        if len(self) != len(other):
            return False
        for inner_set in self:
            if inner_set not in other:
                return False
        return True

    def __iter__(self):
        return iter(self._content)

    def __len__(self):
        return len(self._content)

    def __repr__(self):
        total_discrete_sets: int = len(self.discrete_set)
        total_intervals: int = len(self.intervals)
        if total_discrete_sets:
            return f"UnionSet({total_discrete_sets}D, {total_intervals}I)"
        return f"UnionSet({total_intervals}I)"

    def __str__(self):
        return f" {Ad.UNION} ".join(str(alg_set) for alg_set in self)

    @property
    def discrete_set(self) -> list:
        if isinstance(self._content[0], DiscreteAlgSet):
            return [self._content[0]]
        return []

    @property
    def intervals(self) -> list:
        if isinstance(self._content[0], DiscreteAlgSet):
            return self._content[1:]
        return self._content[:]

    def _correct_content(self, set_content: list | tuple) -> list:
        set_content = list(set_content)
        self._single_digit_intervals_to_discrete_sets(set_content)
        assert any(isinstance(inner_set, IntervalAlgSet) for inner_set in
                   set_content), f"{self._ERR}{ErrorMessages.UNION_MUST_CONTAIN_INTERVAL}"
        self.__simplify_discrete_sets_content(set_content)
        assert len(set_content) > 1, f"{self._ERR}{ErrorMessages.AT_LEAST_TWO_SETS_IN_UNION}"
        self._include_numbers_from_discrete_set_into_intervals(set_content)
        assert len(set_content) > 1, f"{self._ERR}{ErrorMessages.AT_LEAST_TWO_SETS_IN_UNION}"
        # discrete sets processed
        self.__unite_closed_limits(set_content)
        self.__simplify_intervals_content(set_content)
        assert len(set_content) > 1, f"{self._ERR}{ErrorMessages.AT_LEAST_TWO_SETS_IN_UNION}"
        return set_content

    def _create_content(self, alg_set: Any) -> None:
        if isinstance(alg_set, self.__class__):
            self._content = deepcopy(alg_set.content)
            return
        self._content = self._correct_content(alg_set)

    def _init_check(self, alg_set: Any) -> None:
        self._allowed_types = (list,)
        self._asserts = [
            (isinstance(alg_set, self.__class__) or (isinstance(alg_set, (list, tuple)) and len(alg_set) > 1),
             f"{self._ERR}{ErrorMessages.AT_LEAST_TWO_SETS_IN_UNION}")
        ]
        super()._init_check(alg_set)

    def __simplify_intervals_content(self, alg_set: list) -> None:
        """
        Unites all intervals that have a non-empty intersection.
        :param alg_set: list of any sets
        :return: None
        """
        from algsettools import Intersections
        first_index: int = 1 if isinstance(alg_set[0], DiscreteAlgSet) else 0
        while first_index < len(alg_set) - 1:
            interval1: IntervalAlgSet = alg_set[first_index]
            second_index: int = first_index + 1
            while second_index < len(alg_set):
                interval2: IntervalAlgSet = alg_set[second_index]
                intersection_type: Intersections = AlgSet._intersection_type(interval1, interval2)
                if intersection_type != Intersections.EMPTY:
                    union_result = self._union_of_intersectioned_intervals(interval1, interval2)
                    del alg_set[second_index]
                    alg_set[first_index] = union_result
                    self.__simplify_intervals_content(alg_set)
                    return
                second_index += 1
            first_index += 1

    @staticmethod
    def __simplify_discrete_sets_content(alg_set: list) -> None:
        """
        Unites All discrete sets into one.
        :param alg_set: list of any sets
        :return: None
        """
        result_discrete: DiscreteAlgSet = DiscreteAlgSet()
        remove_indexes: List[int] = []
        for i, inner_set in enumerate(alg_set):
            if isinstance(inner_set, DiscreteAlgSet):
                result_discrete = AlgSet._union_discrete_sets(result_discrete, inner_set)
                remove_indexes.append(i)
        for remove_index in reversed(remove_indexes):
            del alg_set[remove_index]
        if result_discrete:
            alg_set.insert(0, result_discrete)

    @staticmethod
    def __unite_closed_limits(alg_set: list) -> None:
        """
        Closes all limits for the number x if x is in alg_set.
        :param alg_set: list of any sets
        :return: None
        """
        closed_limits: list = []
        for inner_set in alg_set:
            if isinstance(inner_set, IntervalAlgSet):
                if inner_set.is_left_closed():
                    closed_limits.append(inner_set.lower_limit)
                elif inner_set.is_right_closed():
                    closed_limits.append(inner_set.upper_limit)
        for inner_set in alg_set:
            if isinstance(inner_set, IntervalAlgSet):
                if inner_set.lower_limit in closed_limits:
                    inner_set.add_lower_limit()
                if inner_set.upper_limit in closed_limits:
                    inner_set.add_upper_limit()


if __name__ == '__main__':
    from algexptools import NumericAtomicAlgExp
    s1 = IntervalAlgSet(5, 7)
    s2 = IntervalAlgSet(1, 2)
    s3 = IntervalAlgSet(NumericAtomicAlgExp("-inf"), 2)
    s4 = DiscreteAlgSet(4, 5, 6)
    s5 = DiscreteAlgSet(6, 4, 5)
    union1 = UnionAlgSet(s1, s2, s3, s4)
    union2 = UnionAlgSet(s1, s1, s2, s2, s4, s4)
    print(union1)
    print(union2)
    print((1, union1, union2))
    print(s4 == s5)
