from typing import Any
import re

import algexptools
from algebradata import AlgebraData as Ad
from errormessages import ErrorMessages
from algexptools import AtomicAlgExp, NumericAlgExp
from patterns import Patterns


class NumericAtomicAlgExp(NumericAlgExp, AtomicAlgExp):
    """
    Contains a real number without any operations or 'i' / '-i'.
    """

    # other variables
    _allowed_content_pattern = re.compile(Patterns.ALLOWED_NUMERIC_ATOMIC_CONTENT)

    def __init__(self, expression: Any = 0):
        self._correction_methods = (self._remove_zeros,)
        NumericAlgExp.__init__(self, expression)

    @property
    def value(self) -> complex:
        i, minus_i = Ad.IMAG_UNIT, f"{Ad.MINUS}{Ad.IMAG_UNIT}"
        if self._content in (i, minus_i):
            return complex(self._content.replace(i, Ad.IMAG_UNIT_BUILT_IN))
        return complex(self._content)

    def is_natural(self) -> bool:
        return not self.has_imag() and self.value.real > 0

    def is_integer(self) -> bool:
        return not self.has_imag()

    def is_rational(self) -> bool:
        return not self.has_imag()

    def is_real(self) -> bool:
        return not self.has_imag()

    def is_complex(self) -> bool:
        return True

    def _create_content_from_complex(self, expression: complex) -> None:
        is_not_atomic: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, AtomicAlgExp.__name__)
        assert expression.real == 0 or expression.imag == 0, is_not_atomic
        if expression.real:  # further, the creation is delegated to the float method
            self._create_content_from_float(expression.real)
        else:  # multiple of imag unit must be -1, 0 or 1
            assert expression.imag in (-1, 0, 1), is_not_atomic
            match expression.imag:
                case -1:
                    self._content = f"{Ad.MINUS}{Ad.IMAG_UNIT}"
                case 0:
                    self._content = "0"
                case 1:
                    self._content = Ad.IMAG_UNIT

    def _create_content_from_float(self, expression: float) -> None:
        is_not_atomic: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, AtomicAlgExp.__name__)
        for special_string in Ad.SPECIAL_NUMERIC_STRINGS:
            if str(expression) in (special_string, f"{Ad.MINUS}{special_string}"):
                self._content = str(expression)
                return
        assert expression % 1 == 0, is_not_atomic  # expression must be an integer
        self._content = str(expression)[:-2]

    def _create_content_from_str(self, expression: str) -> None:
        corrected_expression: str = self._correction(expression)
        is_not_atomic: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, AtomicAlgExp.__name__)
        assert re.search(self._allowed_content_pattern, corrected_expression), is_not_atomic
        if re.search(Patterns.FLOAT_NUMBER, corrected_expression):
            self._create_content_from_float(float(corrected_expression))
        else:
            self._content = corrected_expression

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        i, minus_i = Ad.IMAG_UNIT, f"{Ad.MINUS}{Ad.IMAG_UNIT}"
        clean_expression: str
        if isinstance(expression, str):
            clean_expression = self._remove_white_spaces(expression)
        else:
            clean_expression = expression
        self._allowed_types = {int: self.__create_content_from_int}
        self._asserts = [
            (
                not isinstance(expression, str) or re.search(self._allowed_content_pattern, clean_expression),
                f"Expression must be a real number without operations or '{i}' / '{minus_i}' (see doc)")
        ]
        super()._init_check(expression)

    def __create_content_from_int(self, expression: int) -> None:
        """
        Creates specific structure (named as content) from an expression int.
        :param expression: any algebraic expression
        :return: None
        """
        self._content = str(expression)

    def _substitute_all_special_numeric_strings(self, expression: str, reverse: bool = False) -> str:
        subs_chr, subs_index = Ad.SUBSTITUTION_CHARACTER, self._substitution_index
        substitutions: dict = self._special_numeric_strings_substitutions
        replaced_expression: str = expression
        if reverse:
            for special_string in substitutions:
                replaced_expression = replaced_expression.replace(substitutions[special_string], special_string)
            return replaced_expression
        for special_string in Ad.SPECIAL_NUMERIC_STRINGS:
            if special_string in replaced_expression:
                replaced_expression = replaced_expression.replace(special_string, f"{subs_chr}{subs_index}")
                self._special_numeric_strings_substitutions[special_string] = f"{subs_chr}{subs_index}"
                break
        return replaced_expression


if __name__ == '__main__':
    while True:
        alg_exp_input: str = input(": ")
        if alg_exp_input == "exit":
            break
        try:
            alg_exp: NumericAtomicAlgExp = NumericAtomicAlgExp(alg_exp_input)
            print(f"exp: {alg_exp}")
            print(f"value: {alg_exp.value}")
        except (algexptools.AlgExpError, AssertionError) as err:
            print(err)
