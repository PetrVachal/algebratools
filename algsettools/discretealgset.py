from copy import deepcopy
from typing import Any, List

from algebradata import AlgebraData as Ad
from algexptools import NumericAlgExp
from algsettools import AlgSet
from errormessages import ErrorMessages


class DiscreteAlgSet(AlgSet):
    """
    Contains one discrete set that contains a finite number of any NumericAlgExp instances.\n
    A call with no parameters creates an empty set.\n
    """
    _PREFIX: str = "DiscreteAlgSet"
    _ERR: str = f"{_PREFIX}Error: "

    # common variables
    _content: list = None

    def __init__(self, *args):
        discrete_set: tuple = deepcopy(args)
        if not discrete_set:
            discrete_set = ()
        if len(args) == 1 and isinstance(args[0], self.__class__):
            super().__init__(args[0])
        else:
            super().__init__(discrete_set)

    def __bool__(self):
        return not self.is_empty()

    def __contains__(self, item):
        try:
            item = self._filter_number(item)
        except (AssertionError, ValueError):
            return False
        for inner_alg_exp in self:
            if inner_alg_exp == item:
                return True
        return False

    def __eq__(self, other):
        eq: bool = super().__eq__(other)
        if not eq:
            return False
        if len(self) != len(other):
            return False
        # lengths are equal
        self_exp_values: List[complex] = [inner_alg_exp.value for inner_alg_exp in self._content]
        other_exp_values: List[complex] = [inner_alg_exp.value for inner_alg_exp in other.content]
        while self_exp_values:
            actual_value: complex = self_exp_values[0]
            if actual_value not in other_exp_values:
                return False
            self_exp_values.remove(actual_value)
            other_exp_values.remove(actual_value)
        return True

    def __iter__(self):
        return iter(self._content)

    def __len__(self):
        return len(self._content)

    def __repr__(self):
        return f"DiscreteSet({self})"

    def __str__(self):
        content_str = Ad.LEFT_SET_BRACKET
        for inner_alg_exp in self._content:
            content_str += str(inner_alg_exp) + Ad.SET_SEPARATOR
        if len(content_str) > 1:
            content_str = content_str[:-1]
        content_str += Ad.RIGHT_SET_BRACKET
        return content_str

    def add(self, number: complex | float | int | NumericAlgExp) -> None:
        """
        Adds a number to self-set.
        :param number: any NumericAlgExp instance
        :return: None
        """
        if number not in self._content:
            self._content.append(self._filter_number(number))

    def is_empty(self):
        return self._content == []

    def remove(self, number: complex | float | int | NumericAlgExp) -> None:
        """
        Removes number from self-set if set contains it.
        Otherwise, throws an exception.
        :param number: any NumericAlgExp instance
        :return: None
        """
        exp_not_in_set: str = ErrorMessages.replace(ErrorMessages.EXP_NOT_IN_SET, number, self)
        wanted_number_index: int = self.__first_index_of_number(number)
        if wanted_number_index == -1:
            raise ValueError(f"{self._ERR}{exp_not_in_set}")
        del self._content[wanted_number_index]

    def _correct_content(self, set_content: list) -> list:
        indexes_for_remove: List[int] = []
        actual_index: int = 0
        while actual_index < len(set_content) - 1:
            compare_exp_index: int = actual_index + 1
            while compare_exp_index < len(set_content):
                if set_content[actual_index] == set_content[compare_exp_index]:
                    if compare_exp_index not in indexes_for_remove:
                        indexes_for_remove.append(compare_exp_index)
                compare_exp_index += 1
            actual_index += 1
        # indexes must be sorted and reversed for removing loop. There is a good reason for that.
        # Imagine what would have happened if this had not been used... :^)
        for remove_index in reversed(sorted(indexes_for_remove)):
            del set_content[remove_index]
        return set_content

    def _create_content(self, alg_set: Any) -> None:
        if isinstance(alg_set, self.__class__):
            self._content = deepcopy(alg_set.content)
            return
        pre_content: list = []
        for number in alg_set:
            pre_content.append(self._filter_number(number))
        self._content = self._correct_content(pre_content)

    def _init_check(self, alg_set: Any):
        self._allowed_types = (list, set)
        self._asserts = []
        super()._init_check(alg_set)

    def __first_index_of_number(self, wanted_number: complex | float | int | NumericAlgExp) -> int:
        """
        Returns first index of wanted number.
        If wanted number is not found, returns -1.
        :param wanted_number: number for which I want to know the first occurrence index
        :return: see doc
        """
        for (i, inner_alg_exp) in enumerate(self):
            if inner_alg_exp == wanted_number:
                return i
        return -1


if __name__ == '__main__':
    pass
