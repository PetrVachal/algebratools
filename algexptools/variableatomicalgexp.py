from typing import Any
import re

from algebradata import AlgebraData as Ad
from algexptools import AtomicAlgExp, VariableAlgExp
from errormessages import ErrorMessages
from patterns import Patterns


class VariableAtomicAlgExp(VariableAlgExp, AtomicAlgExp):
    """
    Contains variable without any operations.
    """

    _PREFIX: str = "VariableAtomicAlgExp"
    _ERR: str = f"{_PREFIX}Error: "

    # other variables
    _allowed_content_pattern = re.compile(Patterns.ALLOWED_SIMPLE_VARIABLE_ATOMIC_CONTENT)

    def __init__(self, expression: Any, variables_domains: dict = None):
        self._correction_methods = ()
        VariableAlgExp.__init__(self, expression, variables_domains)

    def _create_content_from_str(self, expression: str) -> None:
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        is_not_atomic: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, AtomicAlgExp.__name__)
        corrected_expression: str = self._correction(expression)
        assert not corrected_expression.startswith(
            f"{Ad.MINUS}{left_imm_br}"), f"{self._ERR}{ErrorMessages.MUST_BE_ATOMIC_VARIABLE}"
        assert self._is_wrapped_in_brackets(corrected_expression, left_imm_br, right_imm_br) or re.search(
            self._allowed_content_pattern, corrected_expression), f"{self._ERR}{is_not_atomic}"
        self._content = corrected_expression

    def _found_and_get_all_variables(self) -> list:
        return [self]

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        self._allowed_types = {}
        self._asserts = [
            (
                not isinstance(expression, str) or Ad.LEFT_IMMUTABLE_BRACKET in expression or re.search(
                    self._allowed_content_pattern, self._replace_immutable_areas(expression)),
                ErrorMessages.MUST_BE_ATOMIC_VARIABLE)
        ]
        super()._init_check(expression)

    @staticmethod
    def _substitute(alg_exp, variable: str, number: Any):
        super()._substitute(alg_exp, variable, number)
        number_string: str = str(number)
        if isinstance(alg_exp, VariableAtomicAlgExp):
            if alg_exp._content == variable:
                alg_exp._content = number_string
        return alg_exp


if __name__ == '__main__':
    while True:
        alg_exp_input: str = input(": ")
        if alg_exp_input == "exit":
            break
        try:
            alg_exp_outer: VariableAtomicAlgExp = VariableAtomicAlgExp(alg_exp_input)
            print(f"exp: {alg_exp_outer}")
            print(f"variables: {alg_exp_outer.variables}")
            print(f"variables_domains: {alg_exp_outer.variables_domains}")
            print(f"immutable_contents: {alg_exp_outer.immutable_contents}")
        except Exception as err:
            print(err)
