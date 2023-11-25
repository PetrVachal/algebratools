from multipledispatch import dispatch
from typing import Any

from algebradata import AlgebraData as Ad
from algsettools import AlgSet
from algexptools import NumericAlgExp
from errormessages import ErrorMessages


class IntervalAlgSet(AlgSet):
    """
    Contains one interval.\n
    Interval in this class is represented by two limits - lower and upper.\n
    Interval is closed from the left <=> is_left_closed = True\n
    Interval is closed from the right <=> is_right_closed = True\n
    A call with no parameters creates interval (-inf, inf).\n
    """
    _PREFIX: str = "IntervalAlgSet"
    _ERR: str = f"{_PREFIX}Error: "

    # common variables
    _content: tuple = None
    _is_left_closed: bool = None
    _is_right_closed: bool = None
    _lower_limit: NumericAlgExp = None
    _upper_limit: NumericAlgExp = None

    @dispatch(object)
    def __init__(self, alg_set):
        super().__init__(alg_set)

    @dispatch()
    def __init__(self):
        from algexptools import NumericAtomicAlgExp
        self._is_left_closed, self._is_right_closed = False, False
        alg_set = (NumericAtomicAlgExp(f"{Ad.MINUS}inf"), NumericAtomicAlgExp("inf"))
        super().__init__(alg_set)

    @dispatch(object, object)
    def __init__(self, lower_limit, upper_limit):
        self.__init__(lower_limit, upper_limit, False, False)

    @dispatch(object, object, bool)
    def __init__(self, lower_limit, upper_limit, is_left_closed):
        self.__init__(lower_limit, upper_limit, is_left_closed, False)

    @dispatch(object, object, bool, bool)
    def __init__(self, lower_limit, upper_limit, is_left_closed, is_right_closed):
        alg_set = lower_limit, upper_limit
        self._is_left_closed, self._is_right_closed = is_left_closed, is_right_closed
        super().__init__(alg_set)

    def __contains__(self, item):
        try:
            item = self._filter_number(item)
        except (AssertionError, ValueError):
            if isinstance(item, NumericAlgExp):
                assert not item.has_imag(), f"{self._ERR}{ErrorMessages.CANNOT_IMAG_IN_INTERVAL}"
            return False
        if self._lower_limit.value.real < item.value.real < self._upper_limit.value.real:
            return True
        if self._lower_limit == item.value and self._is_left_closed:
            return True
        if self._upper_limit == item.value and self._is_right_closed:
            return True
        return False

    def __eq__(self, other):
        eq: bool = super().__eq__(other)
        if not eq:
            return False
        limits_equals: bool = self._lower_limit == other.lower_limit and self._upper_limit == other.upper_limit
        closed_combinations: bool = (self._is_left_closed, self._is_right_closed) == (
            other.is_left_closed(), other.is_right_closed())
        return limits_equals and closed_combinations

    def __repr__(self):
        return f"Interval{self}"

    def __str__(self):
        sep: str = f"{Ad.INTERVAL_SEPARATOR} "
        left_br: str = Ad.LEFT_INTERVAL_CLOSED if self._is_left_closed else Ad.LEFT_INTERVAL_OPEN
        right_br: str = Ad.RIGHT_INTERVAL_CLOSED if self._is_right_closed else Ad.RIGHT_INTERVAL_OPEN
        return f"{left_br}{self._lower_limit}{sep}{self._upper_limit}{right_br}"

    @property
    def lower_limit(self):
        return self._lower_limit

    @property
    def upper_limit(self):
        return self._upper_limit

    def add_lower_limit(self):
        self._is_left_closed = True

    def add_upper_limit(self):
        self._is_right_closed = True

    def has_no_limits(self):
        return self._lower_limit == complex(f"{Ad.MINUS}inf") and self._upper_limit == complex("inf")

    def is_closed(self):
        return self._is_left_closed and self._is_right_closed

    def is_left_closed(self):
        return self._is_left_closed

    def is_left_open(self):
        return not self._is_left_closed

    def is_one_number(self):
        return self._lower_limit == self._upper_limit

    def is_open(self):
        return self.is_left_open() and self.is_right_open()

    def is_right_closed(self):
        return self._is_right_closed

    def is_right_open(self):
        return not self._is_right_closed

    def _correct_content(self, set_content: tuple) -> tuple:
        assert len(set_content) == 2, f"{self._ERR}{ErrorMessages.LEN_INTERVAL_MUST_BE_2}"
        set_content = tuple(self._filter_number(number) for number in set_content)
        wrong_numbers_ordering: str = ErrorMessages.replace(ErrorMessages.WRONG_NUMBERS_ORDERING_INTERVAL,
                                                            str(set_content))
        must_be_closed: str = ErrorMessages.replace(ErrorMessages.INTERVAL_MUST_BE_CLOSED, str(set_content))
        assert set_content[0].value.real <= set_content[1].value.real, f"{self._ERR}{wrong_numbers_ordering}"
        if set_content[0].value.real == set_content[1].value.real:
            assert self.is_closed(), f"{self._ERR}{must_be_closed}"
        return set_content

    def _create_content(self, alg_set: Any) -> None:
        if isinstance(alg_set, self.__class__):
            self._content = alg_set.content
            self._lower_limit = alg_set.lower_limit
            self._upper_limit = alg_set.upper_limit
            self._is_left_closed = alg_set.is_left_closed()
            self._is_right_closed = alg_set.is_right_closed()
            return
        self._content = self._correct_content(alg_set)
        self._lower_limit, self._upper_limit = self._content

    def _filter_number(self, number: Any) -> NumericAlgExp:
        number = super()._filter_number(number)
        assert self.has_no_limits() or not number.has_imag(), f"{self._ERR}{ErrorMessages.CANNOT_IMAG_IN_INTERVAL}"
        real_value: float = number.value.real
        assert real_value < 0 or real_value >= 0, f"{self._ERR}{ErrorMessages.CANNOT_NAN_IN_INTERVAL}"
        return number

    def _init_check(self, alg_set: Any) -> None:
        self._allowed_types = ()
        self._asserts = []
        super()._init_check(alg_set)


if __name__ == '__main__':
    pass
