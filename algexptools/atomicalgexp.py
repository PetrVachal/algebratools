from abc import ABC
from typing import Any
import re

from algebradata import AlgebraData as Ad
from algexptools import AlgExp


class AtomicAlgExp(AlgExp, ABC):
    """
    Abstract class for atomic algebraic expressions <=> expressions without any operations.
    - NumericAtomicAlgExp   complex number without operations
    - VariableAtomicAlgExp  variable without operations
    """
    _PREFIX: str = "AtomicAlgExp"
    _ERR: str = f"{_PREFIX}Error: "

    # common variables
    _content: str = None

    def __init__(self, expression: Any):
        super().__init__(expression)

    def __contains__(self, item):
        from algexptools import VariableAtomicAlgExp
        super().__contains__(item)
        string_item: str = str(item)
        if self._content == string_item:
            return True
        return False

    def __str__(self):
        return self._content

    def has_imag(self) -> bool:
        return self._content in (Ad.IMAG_UNIT, f"{Ad.MINUS}{Ad.IMAG_UNIT}")

    @staticmethod
    def _remove_zeros(expression: str) -> str:
        """
        Removes redundant zeros from expression string and after that this replaced string is returned.
        :param expression: any algebraic expression
        :return: expression string without redundant zeros
        """
        minus: str = Ad.MINUS
        pattern_zero_and_digit = re.compile(r"^0\d")
        while re.search(pattern_zero_and_digit, expression):
            expression = expression[1:]
        pattern_minus_zero_digit = re.compile(rf"^{minus}0\d")
        while re.search(pattern_minus_zero_digit, expression):
            expression = minus + expression[2:]
        pattern_digit_and_zero = re.compile(r"\d0$")
        while re.search(pattern_digit_and_zero, expression) and Ad.DECIMAL_POINT in expression:
            expression = expression[:-1]
        return expression
