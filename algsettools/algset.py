from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, List

from algexptools import AlgExp, NumericAlgExp, NumericAtomicAlgExp, NumericCompositeAlgExp
from errormessages import ErrorMessages


class AlgSet(ABC):
    """
    Abstract class for all kinds of sets:

    - DiscreteAlgSet    set with finitely many numbers
    - IntervalAlgSet    set of all numbers between two limits (infinitely many numbers)
    - UnionAlgSet       combination of Discrete and Interval (must contain at least two subsets)
    """
    _PREFIX: str = "AlgSet"
    _ERR: str = f"{_PREFIX}Error: "

    # common variables
    _content: list | tuple = None

    # other variables
    _allowed_types: tuple = None
    _asserts: list = None

    def __init__(self, alg_set: Any):
        self._init_check(alg_set)
        self._create_content(alg_set)

    @abstractmethod
    def __contains__(self, item):
        return NotImplemented

    @abstractmethod
    def __repr__(self):
        return NotImplemented

    @abstractmethod
    def __str__(self):
        return NotImplemented

    @abstractmethod
    def _correct_content(self, set_content: list | tuple):
        """
        Checks and, if necessary, simplifies set_content.
        :param set_content: content of the given set
        :return: reviewed and possibly modified set_content
        """
        return NotImplemented

    @abstractmethod
    def _create_content(self, alg_set: Any):
        """
        Creates content of the given alg_set.
        :param alg_set: given set
        :return: None
        """
        return NotImplemented

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def content(self):
        return self._content

    def _filter_number(self, number: Any) -> NumericAlgExp:
        """
        Checks if given number is suitable for insertion into self-set.
        :param number: any number suitable for self-set
        :return: instance of NumericAlgExp created from number
        """
        if isinstance(number, NumericAlgExp):
            return number
        return AlgExp.initializer(number, (NumericAtomicAlgExp, NumericCompositeAlgExp))

    def _init_check(self, alg_set: Any) -> None:
        """
        Sniper filter for throwing an exception if the parameters are invalid.
        :param alg_set: given set
        :return: None
        """
        self._allowed_types += (self.__class__, tuple)
        types_string: str = "(" + ", ".join([x.__name__ for x in self._allowed_types]) + ")"
        new_asserts: list = [
            (isinstance(alg_set, self._allowed_types),
             f"set must be in {types_string}"),
        ]
        self._asserts += new_asserts
        for condition, err_message in self._asserts:
            assert condition, f"{self._ERR}{err_message}"

    @staticmethod
    def intersect(*args):
        """
        Returns the intersection of any number of sets.
        :param args: any instances of AlgSet
        :return: intersection of all args
        """
        assert len(args) >= 2, f"{AlgSet._ERR}{ErrorMessages.AT_LEAST_TWO_SETS_FOR_INTERSECTION}"
        result_set = AlgSet.__intersect(args[0], args[1])
        for actual_set in args[2:]:
            result_set = AlgSet.__intersect(result_set, actual_set)
        return result_set

    @staticmethod
    def union(*args):
        """
        Returns the union of any number of sets.
        :param args: any instances of AlgSet
        :return: union of all args
        """
        assert len(args) >= 2, f"{AlgSet._ERR}{ErrorMessages.AT_LEAST_TWO_SETS_FOR_UNION}"
        result_set = AlgSet.__union(args[0], args[1])
        if len(args) > 2:
            for actual_set in args[2:]:
                result_set = AlgSet.__union(result_set, actual_set)
        return result_set

    @staticmethod
    def _union_of_intersectioned_intervals(interval1, interval2):
        """
        Returns union of two intervals with non-empty intersection.
        :param interval1: interval set
        :param interval2: interval set
        :return: see doc
        """
        from algsettools import Intersections, IntervalAlgSet
        l1, u1 = interval1.lower_limit.value.real, interval1.upper_limit.value.real
        l2, u2 = interval2.lower_limit.value.real, interval2.upper_limit.value.real
        l1_closed, u1_closed = interval1.is_left_closed(), interval1.is_right_closed()
        l2_closed, u2_closed = interval2.is_left_closed(), interval2.is_right_closed()
        l1_or_l2_closed: bool = l1_closed or l2_closed
        u1_or_u2_closed: bool = u1_closed or u2_closed
        intersection_type: Intersections = AlgSet._intersection_type(interval1, interval2)
        match intersection_type:
            case Intersections.ONE_NUMBER:
                if u1 == l2:  # (l1, u2)
                    return IntervalAlgSet(l1, u2, l1_closed, u2_closed)
                if u2 == l1:  # (l2, u1)
                    return IntervalAlgSet(l2, u1, l2_closed, u1_closed)
            case Intersections.PARTIAL_OVERLAP:
                if l1 < l2 < u1 < u2:  # (l1, u2)
                    return IntervalAlgSet(l1, u2, l1_closed, u2_closed)
                if l2 < l1 < u2 < u1:  # (l2, u1)
                    return IntervalAlgSet(l2, u1, l2_closed, u1_closed)
            case Intersections.INNER_LEFT_OVERLAP_WITHOUT_LOWER:
                if u1 < u2:  # (l1, u2)
                    return IntervalAlgSet(l1, u2, l1_or_l2_closed, u2_closed)
                if u2 < u1:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, l1_or_l2_closed, u1_closed)
            case Intersections.INNER_LEFT_OVERLAP:
                if u1 < u2:  # [l1, u2)
                    return IntervalAlgSet(l1, u2, True, u2_closed)
                if u2 < u1:  # [l1, u1)
                    return IntervalAlgSet(l1, u1, True, u1_closed)
            case Intersections.INNER_OVERLAP:
                if l1 < l2 and u1 > u2:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, l1_closed, u1_closed)
                if l2 < l1 and u2 > u1:  # (l2, u2)
                    return IntervalAlgSet(l2, u2, l2_closed, u2_closed)
            case Intersections.EQUALITY_WITHOUT_LIMITS:  # (l1, u1)
                return IntervalAlgSet(l1, u1, l1_or_l2_closed, u1_or_u2_closed)
            case Intersections.EQUALITY_WITHOUT_LOWER:  # (l1, u1]
                return IntervalAlgSet(l1, u1, l1_or_l2_closed, True)
            case Intersections.EQUALITY_WITHOUT_UPPER:  # [l1, u1)
                return IntervalAlgSet(l1, u1, True, u1_or_u2_closed)
            case Intersections.EQUALITY:  # [l1, u1]
                return IntervalAlgSet(l1, u1, True, True)
            case Intersections.INNER_RIGHT_OVERLAP_WITHOUT_UPPER:
                if l1 < l2:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, l1_closed, u1_or_u2_closed)
                if l2 < l1:  # (l2, u1)
                    return IntervalAlgSet(l2, u1, l2_closed, u1_or_u2_closed)
            case Intersections.INNER_RIGHT_OVERLAP:
                if l1 < l2:  # (l1, u1]
                    return IntervalAlgSet(l1, u1, l1_closed, True)
                if l2 < l1:  # (l2, u1]
                    return IntervalAlgSet(l2, u1, l2_closed, True)
            case _:
                intersection_not_recognized: str = ErrorMessages.replace(ErrorMessages.INTERSECTION_NOT_RECOGNIZED,
                                                                         interval1, interval2)
                raise ValueError(f"{AlgSet._ERR}{intersection_not_recognized}")

    @staticmethod
    def _include_numbers_from_discrete_set_into_intervals(alg_set: list) -> None:
        """
        Inserts, if possible, numbers from DiscreteSet into one of the intervals in alg_set.
        These inserted numbers are then removed from discreteSet.
        :param alg_set: list of any sets
        :return: None
        """
        from algsettools import DiscreteAlgSet, IntervalAlgSet
        inner_discrete: DiscreteAlgSet = DiscreteAlgSet()
        for inner_set in alg_set:
            if isinstance(inner_set, DiscreteAlgSet):
                inner_discrete = inner_set
                break
        if not inner_discrete:
            return
        remove_indexes: List[int] = []
        for inner_set in alg_set:
            if isinstance(inner_set, IntervalAlgSet):
                for i, number in enumerate(inner_discrete):
                    if number in inner_set or number in (inner_set.lower_limit, inner_set.upper_limit):
                        if number in inner_set:
                            pass
                        elif number == inner_set.lower_limit:
                            inner_set.add_lower_limit()
                        elif number == inner_set.upper_limit:
                            inner_set.add_upper_limit()
                        if i not in remove_indexes:
                            remove_indexes.append(i)
        # indexes must be sorted and reversed for removing loop. There is a good reason for that.
        # Imagine what would have happened if this had not been used... :^)
        for remove_index in reversed(sorted(remove_indexes)):
            del inner_discrete.content[remove_index]
        if not inner_discrete:
            alg_set.remove(inner_discrete)

    @staticmethod
    def _intersection_type(interval1, interval2):
        """
        Returns type of intersection of given intervals.
        :param interval1: intervalSet
        :param interval2: intervalSet
        :return: see doc
        """
        from algsettools import Intersections
        l1_closed: bool = True if interval1.is_left_closed() else False
        u1_closed: bool = True if interval1.is_right_closed() else False
        l2_closed: bool = True if interval2.is_left_closed() else False
        u2_closed: bool = True if interval2.is_right_closed() else False
        l1, u1 = interval1.lower_limit.value.real, interval1.upper_limit.value.real
        l2, u2 = interval2.lower_limit.value.real, interval2.upper_limit.value.real
        if u1 < l2 or u2 < l1:
            return Intersections.EMPTY
        if u1 == l2 or u2 == l1:
            if (u1 == l2 and u1_closed and l2_closed) or (u2 == l1 and u2_closed and l1_closed):
                return Intersections.ONE_NUMBER
            return Intersections.EMPTY
        if l1 == u1 or l2 == u2:
            return Intersections.ONE_NUMBER
        if (l1 < l2 and u1 > u2) or (l2 < l1 and u2 > u1):
            return Intersections.INNER_OVERLAP
        if (l1 < l2 < u1 < u2) or (l2 < l1 < u2 < u1):
            return Intersections.PARTIAL_OVERLAP
        if (l1 == l2 and u1 < u2) or (l2 == l1 and u2 < u1):
            if l1_closed and l2_closed:
                return Intersections.INNER_LEFT_OVERLAP
            return Intersections.INNER_LEFT_OVERLAP_WITHOUT_LOWER
        if l1 == l2 and u1 == u2:
            if l1_closed and l2_closed:
                if u1_closed and u2_closed:
                    return Intersections.EQUALITY
                return Intersections.EQUALITY_WITHOUT_UPPER
            if u1_closed and u2_closed:
                return Intersections.EQUALITY_WITHOUT_LOWER
            return Intersections.EQUALITY_WITHOUT_LIMITS
        if (l1 < l2 and u1 == u2) or (l2 < l1 and u2 == u1):
            if u1_closed and u2_closed:
                return Intersections.INNER_RIGHT_OVERLAP
            return Intersections.INNER_RIGHT_OVERLAP_WITHOUT_UPPER
        return Intersections.UNKNOWN_INTERSECTION

    @staticmethod
    def _single_digit_intervals_to_discrete_sets(alg_set: list) -> None:
        """
        Converts intervals [x, x] to a number x, which it stores in discreteSet.
        :param alg_set: list of any sets
        :return: None
        """
        from algsettools import DiscreteAlgSet, IntervalAlgSet
        remove_indexes: List[int] = []
        numbers: list = []
        for i, inner_set in enumerate(alg_set):
            if isinstance(inner_set, IntervalAlgSet) and inner_set.is_one_number():
                numbers.append(inner_set.lower_limit)
                remove_indexes.append(i)
        for remove_index in reversed(remove_indexes):
            del alg_set[remove_index]
        if remove_indexes:
            alg_set.insert(0, DiscreteAlgSet(*numbers))

    @staticmethod
    def _union_discrete_sets(discrete1, discrete2):
        """
        Returns the union of two discreteSets.
        :param discrete1: discreteSet
        :param discrete2: discreteSet
        :return: union of two given discreteSets
        """
        from algsettools import DiscreteAlgSet
        smaller_discrete, greater_discrete = sorted((discrete1, discrete2), key=len)
        union_discrete: DiscreteAlgSet = deepcopy(greater_discrete)
        for inner_alg_exp in smaller_discrete:
            union_discrete.add(inner_alg_exp)
        return union_discrete

    @staticmethod
    def __get_set_based_on_intersection_size(intersection_result):
        """
        Returns a set based on the type of intersection result.
        :param intersection_result: result of intersection of any sets
        :return: see doc
        """
        from algsettools import DiscreteAlgSet, IntervalAlgSet, UnionAlgSet
        if len(intersection_result) == 1:
            if isinstance(intersection_result[0], DiscreteAlgSet):
                return DiscreteAlgSet(*intersection_result)
            return IntervalAlgSet(*intersection_result)
        return UnionAlgSet(*intersection_result)

    @staticmethod
    def __intersect(alg_set1, alg_set2):
        """
        Returns the intersection of two sets based on more specific methods, where the method
        to calculate the intersection is determined by the types of our two sets.
        :param alg_set1: given set
        :param alg_set2: given set
        :return: intersection of two given sets
        """
        from algsettools import DiscreteAlgSet, IntervalAlgSet, UnionAlgSet
        methods_for_type_combinations: dict = {  # all different pairs of types
            (DiscreteAlgSet, DiscreteAlgSet): AlgSet.__intersect_discrete_sets,
            (DiscreteAlgSet, IntervalAlgSet): AlgSet.__intersect_discrete_interval,
            (DiscreteAlgSet, UnionAlgSet): AlgSet.__intersect_discrete_union,
            (IntervalAlgSet, IntervalAlgSet): AlgSet.__intersect_intervals,
            (IntervalAlgSet, UnionAlgSet): AlgSet.__intersect_interval_union,
            (UnionAlgSet, UnionAlgSet): AlgSet.__intersect_unions,
        }
        if (alg_set1.__class__, alg_set2.__class__) in methods_for_type_combinations:
            return methods_for_type_combinations[(alg_set1.__class__, alg_set2.__class__)](alg_set1, alg_set2)
        return methods_for_type_combinations[(alg_set2.__class__, alg_set1.__class__)](alg_set2, alg_set1)

    @staticmethod
    def __intersect_discrete_sets(discrete1, discrete2):
        """
        Returns the intersection of two discreteSets.
        :param discrete1: discreteSet
        :param discrete2: discreteSet
        :return: intersection of two given discreteSets
        """
        smaller_discrete, greater_discrete = sorted((discrete1, discrete2), key=len)
        new_smaller = deepcopy(smaller_discrete)
        exps_for_remove: list = []
        for inner_alg_exp in new_smaller:
            if inner_alg_exp not in greater_discrete:
                exps_for_remove.append(inner_alg_exp)
        for exp_for_remove in exps_for_remove:
            new_smaller.remove(exp_for_remove)
        return new_smaller

    @staticmethod
    def __intersect_discrete_interval(alg_set1, alg_set2):
        """
        Returns the intersection of discreteSet and interval.
        :param alg_set1: discreteSet or interval
        :param alg_set2: interval or discreteSet
        :return: intersection of given sets: discreteSet and interval
        """
        from algsettools import DiscreteAlgSet
        new_discrete, interval_set = AlgSet.__pair_sets(alg_set1, alg_set2, DiscreteAlgSet)
        new_discrete = deepcopy(new_discrete)
        exps_for_remove: list = []
        for inner_alg_exp in new_discrete:
            if inner_alg_exp not in interval_set:
                exps_for_remove.append(inner_alg_exp)
        for exp_for_remove in exps_for_remove:
            new_discrete.remove(exp_for_remove)
        return new_discrete

    @staticmethod
    def __intersect_discrete_union(alg_set1, alg_set2):
        """
        Returns the intersection of discreteSet and unionSet.
        :param alg_set1: discreteSet or unionSet
        :param alg_set2: unionSet or discreteSet
        :return: intersection of given sets: discreteSet and unionSet
        """
        from algsettools import DiscreteAlgSet
        discrete_set, union_set = AlgSet.__pair_sets(alg_set1, alg_set2, DiscreteAlgSet)
        intersection_result: DiscreteAlgSet = DiscreteAlgSet()
        if union_set.discrete_set:
            intersection_result = AlgSet.__intersect_discrete_sets(discrete_set, *union_set.discrete_set)
        for interval in union_set.intervals:
            new_intersection = AlgSet.__intersect_discrete_interval(discrete_set, interval)
            intersection_result = AlgSet._union_discrete_sets(intersection_result, new_intersection)
        return intersection_result

    @staticmethod
    def __intersect_intervals(interval1, interval2):
        """
        Returns the intersection of two intervals.
        :param interval1: intervalSet
        :param interval2: intervalSet
        :return: intersection of two intervals
        """
        from algsettools import DiscreteAlgSet, Intersections, IntervalAlgSet
        l1, u1 = interval1.lower_limit.value.real, interval1.upper_limit.value.real
        l2, u2 = interval2.lower_limit.value.real, interval2.upper_limit.value.real
        l1_closed, u1_closed = interval1.is_left_closed(), interval1.is_right_closed()
        l2_closed, u2_closed = interval2.is_left_closed(), interval2.is_right_closed()
        intersection_type: Intersections = AlgSet._intersection_type(interval1, interval2)
        match intersection_type:
            case Intersections.EMPTY:  # {}
                return DiscreteAlgSet()
            case Intersections.ONE_NUMBER:
                if interval1.is_one_number():  # {l1}
                    return DiscreteAlgSet(l1)
                if interval2.is_one_number():  # {l2}
                    return DiscreteAlgSet(l2)
                if u1 == l2:  # {u1}
                    return DiscreteAlgSet(u1)
                if u2 == l1:  # {l1}
                    return DiscreteAlgSet(l1)
            case Intersections.PARTIAL_OVERLAP:
                if l1 < l2 < u1 < u2:  # (l2, u1)
                    return IntervalAlgSet(l2, u1, l2_closed, u1_closed)
                if l2 < l1 < u2 < u1:  # (l1, u2)
                    return IntervalAlgSet(l1, u2, l1_closed, u2_closed)
            case Intersections.INNER_LEFT_OVERLAP_WITHOUT_LOWER:
                if u1 < u2:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, False, u1_closed)
                if u2 < u1:  # (l1, u2)
                    return IntervalAlgSet(l1, u2, False, u2_closed)
            case Intersections.INNER_LEFT_OVERLAP:
                if u1 < u2:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, True, u1_closed)
                if u2 < u1:  # (l1, u2)
                    return IntervalAlgSet(l1, u2, True, u2_closed)
            case Intersections.INNER_OVERLAP:
                if l1 < l2 and u1 > u2:  # (l2, u2)
                    return IntervalAlgSet(l2, u2, l2_closed, u2_closed)
                if l2 < l1 and u2 > u1:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, l1_closed, u1_closed)
            case Intersections.EQUALITY_WITHOUT_LIMITS:  # (l1, u1)
                return IntervalAlgSet(l1, u1, False, False)
            case Intersections.EQUALITY_WITHOUT_LOWER:  # (l1, u1)
                return IntervalAlgSet(l1, u1, False, True)
            case Intersections.EQUALITY_WITHOUT_UPPER:
                return IntervalAlgSet(l1, u1, True, False)
            case Intersections.EQUALITY:  # (l1, u1)
                return IntervalAlgSet(l1, u1, True, True)
            case Intersections.INNER_RIGHT_OVERLAP_WITHOUT_UPPER:
                if l1 < l2:  # (l2, u1)
                    return IntervalAlgSet(l2, u1, l2_closed, False)
                if l2 < l1:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, l1_closed, False)
            case Intersections.INNER_RIGHT_OVERLAP:
                if l1 < l2:  # (l2, u1)
                    return IntervalAlgSet(l2, u1, l2_closed, True)
                if l2 < l1:  # (l1, u1)
                    return IntervalAlgSet(l1, u1, l1_closed, True)
            case _:
                intersection_not_recognized: str = ErrorMessages.replace(ErrorMessages.INTERSECTION_NOT_RECOGNIZED,
                                                                         interval1, interval2)
                raise ValueError(f"{AlgSet._ERR}{intersection_not_recognized}")

    @staticmethod
    def __intersect_interval_union(alg_set1, alg_set2):
        """
        Returns the intersection of interval and unionSet.
        :param alg_set1: interval or unionSet
        :param alg_set2: unionSet or interval
        :return: intersection of given sets: interval and unionSet
        """
        from algsettools import DiscreteAlgSet, Intersections, IntervalAlgSet
        interval_set, union_set = AlgSet.__pair_sets(alg_set1, alg_set2, IntervalAlgSet)
        intersection_result: list = []
        discrete_result: DiscreteAlgSet = DiscreteAlgSet()
        intervals_result: list = []
        if union_set.discrete_set:
            discrete_result = AlgSet.__intersect_discrete_interval(*union_set.discrete_set, interval_set)
        for inner_interval in union_set.intervals:
            if AlgSet._intersection_type(interval_set, inner_interval) != Intersections.EMPTY:
                intervals_intersection = AlgSet.__intersect_intervals(inner_interval, interval_set)
                if isinstance(intervals_intersection, DiscreteAlgSet):
                    discrete_result = AlgSet._union_discrete_sets(discrete_result, intervals_intersection)
                else:
                    intervals_result.append(intervals_intersection)
        if discrete_result:
            intersection_result.append(discrete_result)
        intersection_result += intervals_result
        return AlgSet.__get_set_based_on_intersection_size(intersection_result)

    @staticmethod
    def __intersect_unions(union_set1, union_set2):
        """
        Returns the intersection of two unionSets.
        :param union_set1: unionSet
        :param union_set2: unionSet
        :return: intersection of two unionSets
        """
        from algsettools import DiscreteAlgSet, Intersections
        intersection_result: list = []
        discrete_result: DiscreteAlgSet = DiscreteAlgSet()
        intervals_result: list = []
        if union_set1.discrete_set:
            new_discrete = AlgSet.__intersect_discrete_union(*union_set1.discrete_set, union_set2)
            discrete_result = AlgSet._union_discrete_sets(discrete_result, new_discrete)
        if union_set2.discrete_set:
            new_discrete = AlgSet.__intersect_discrete_union(*union_set2.discrete_set, union_set1)
            discrete_result = AlgSet._union_discrete_sets(discrete_result, new_discrete)
        for inner_interval1 in union_set1.intervals:
            for inner_interval2 in union_set2.intervals:
                if AlgSet._intersection_type(inner_interval1, inner_interval2) != Intersections.EMPTY:
                    intervals_intersection = AlgSet.__intersect_intervals(inner_interval1, inner_interval2)
                    if isinstance(intervals_intersection, DiscreteAlgSet):
                        discrete_result = AlgSet._union_discrete_sets(discrete_result, intervals_intersection)
                    else:
                        intervals_result.append(intervals_intersection)
        if discrete_result:
            intersection_result.append(discrete_result)
        intersection_result += intervals_result
        return AlgSet.__get_set_based_on_intersection_size(intersection_result)

    @staticmethod
    def __min_max_from_intervals(intervals: list, key_function):
        """
        Returns the interval with the smallest lower limit / largest upper limit.
        The variants depend on key_function.
        :param intervals: any intervals
        :param key_function: min or max to find wanted limit extreme
        :return: see doc
        """
        if key_function == min:
            all_lower_limits: list = [interval.lower_limit.value.real for interval in intervals]
            min_number = min(all_lower_limits)
            for interval in intervals:
                if interval.lower_limit == min_number:
                    return interval
        all_upper_limits: list = [interval.upper_limit.value.real for interval in intervals]
        max_number = max(all_upper_limits)
        for interval in intervals:
            if interval.upper_limit == max_number:
                return interval

    @staticmethod
    def __pair_sets(alg_set1, alg_set2, first_type):
        """
        Returns the correct super trouper combination so that first set in returned tuple
        must be an instance of first_type.
        :param alg_set1: given set
        :param alg_set2: given set
        :param first_type: wanted type for first set in a returned pair of sets
        :return: see doc
        """
        if isinstance(alg_set1, first_type):
            return alg_set1, alg_set2
        return alg_set2, alg_set1

    @staticmethod
    def __union(alg_set1, alg_set2):
        """
        Returns the union of two sets based on more specific methods, where the method
        to calculate the union is determined by the types of our two sets.
        :param alg_set1: given set
        :param alg_set2: given set
        :return: union of two given sets
        """
        from algsettools import DiscreteAlgSet, IntervalAlgSet, UnionAlgSet
        methods_for_type_combinations: dict = {  # all different pairs of types
            (DiscreteAlgSet, DiscreteAlgSet): AlgSet._union_discrete_sets,
            (DiscreteAlgSet, IntervalAlgSet): AlgSet.__union_discrete_interval,
            (DiscreteAlgSet, UnionAlgSet): AlgSet.__union_discrete_union,
            (IntervalAlgSet, IntervalAlgSet): AlgSet.__union_intervals,
            (IntervalAlgSet, UnionAlgSet): AlgSet.__union_interval_union,
            (UnionAlgSet, UnionAlgSet): AlgSet.__union_unions,
        }
        if (alg_set1.__class__, alg_set2.__class__) in methods_for_type_combinations:
            return methods_for_type_combinations[(alg_set1.__class__, alg_set2.__class__)](alg_set1, alg_set2)
        return methods_for_type_combinations[(alg_set2.__class__, alg_set1.__class__)](alg_set2, alg_set1)

    @staticmethod
    def __union_discrete_interval(alg_set1, alg_set2):
        """
        Returns the union of discreteSet and interval.
        :param alg_set1: discreteSet or interval
        :param alg_set2: interval or discreteSet
        :return: union of given sets: discreteSet and interval
        """
        from algsettools import DiscreteAlgSet, IntervalAlgSet, UnionAlgSet
        discrete_set, interval_set = AlgSet.__pair_sets(alg_set1, alg_set2, DiscreteAlgSet)
        set_content: list = [deepcopy(discrete_set), deepcopy(interval_set)]
        AlgSet._single_digit_intervals_to_discrete_sets(set_content)
        if all([isinstance(inner_set, DiscreteAlgSet) for inner_set in set_content]):
            return AlgSet._union_discrete_sets(*set_content)
        AlgSet._include_numbers_from_discrete_set_into_intervals(set_content)
        if len(set_content) == 1:
            return IntervalAlgSet(set_content[0])
        return UnionAlgSet(*set_content)

    @staticmethod
    def __union_discrete_union(alg_set1, alg_set2):
        """
        Returns the union of discreteSet and unionSet.
        :param alg_set1: discreteSet or unionSet
        :param alg_set2: unionSet or discreteSet
        :return: union of given sets: discreteSet and unionSet
        """
        from algsettools import DiscreteAlgSet, IntervalAlgSet, UnionAlgSet
        discrete_set, union_set = AlgSet.__pair_sets(alg_set1, alg_set2, DiscreteAlgSet)
        discrete_set, union_set = deepcopy(discrete_set), deepcopy(union_set)
        if union_set.discrete_set:
            union_set.discrete_set[0] = AlgSet._union_discrete_sets(union_set.discrete_set[0], discrete_set)
            return union_set
        try:
            return UnionAlgSet(discrete_set, *union_set.intervals)
        except AssertionError:
            # special case - numbers from discrete set may unite disjoint intervals into a single one
            # {1} U (0, 1) U (1, 2) <=> (0, 2) ... And interval (0, 2) is no longer UnionAlgSet
            min_interval = AlgSet.__min_max_from_intervals(union_set.intervals, min)
            max_interval = AlgSet.__min_max_from_intervals(union_set.intervals, max)
            return IntervalAlgSet(min_interval.lower_limit, max_interval.upper_limit, min_interval.is_left_closed(),
                                  max_interval.is_right_closed())

    @staticmethod
    def __union_intervals(interval1, interval2):
        """
        Returns the union of two intervals.
        :param interval1: intervalSet
        :param interval2: intervalSet
        :return: union of two intervals
        """
        from algsettools import Intersections, UnionAlgSet
        intersection_type: Intersections = AlgSet._intersection_type(interval1, interval2)
        if intersection_type == Intersections.EMPTY:
            return UnionAlgSet(interval1, interval2)
        return AlgSet._union_of_intersectioned_intervals(interval1, interval2)

    @staticmethod
    def __union_interval_union(alg_set1, alg_set2):
        """
        Returns the union of interval and unionSet.
        :param alg_set1: interval or unionSet
        :param alg_set2: unionSet or interval
        :return: union of given sets: interval and unionSet
        """
        from algsettools import IntervalAlgSet, UnionAlgSet
        interval_set, union_set = AlgSet.__pair_sets(alg_set1, alg_set2, IntervalAlgSet)
        return UnionAlgSet(*union_set.content, interval_set)

    @staticmethod
    def __union_unions(union_set1, union_set2):
        """
        Returns the union of two unions.
        :param union_set1: unionSet
        :param union_set2: unionSet
        :return: union of two unionSets
        """
        from algsettools import UnionAlgSet
        union_set1, union_set2 = deepcopy(union_set1), deepcopy(union_set2)
        return UnionAlgSet(*union_set1.content, *union_set2.discrete_set, *union_set2.intervals)


if __name__ == '__main__':
    pass
