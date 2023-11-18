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

    @property
    def normalized_variable(self):
        if self._content.startswith(Ad.MINUS):
            return self._content[1:]
        return self._content

    def is_minus_variable(self):
        return self._content.startswith(Ad.MINUS)

    def _create_content_from_str(self, expression: str) -> None:
        minus: str = Ad.MINUS
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        is_not_atomic: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, (expression, AtomicAlgExp.__name__))
        corrected_expression: str = self._correction(expression)
        is_minus: bool = corrected_expression.startswith(f"{minus}{left_imm_br}")
        if is_minus:
            corrected_expression = corrected_expression[1:]
        assert self._is_wrapped_in_brackets(corrected_expression, left_imm_br, right_imm_br) or re.search(
            self._allowed_content_pattern, corrected_expression), f"{self._ERR}{is_not_atomic}"
        if is_minus:
            corrected_expression = f"{minus}{corrected_expression}"
        self._content = corrected_expression

    def _found_and_get_all_variables(self) -> list:
        return [self.normalized_variable]

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        self._allowed_types = {}
        self._asserts = [
            (
                not isinstance(expression, str) or Ad.LEFT_IMMUTABLE_BRACKET in expression or re.search(
                    self._allowed_content_pattern, self._replace_immutable_areas(expression)),
                "Expression must be a variable without any operations and signs (see doc)")
        ]
        super()._init_check(expression)

    @staticmethod
    def _substitute(alg_exp, variable: str, number: Any):
        super()._substitute(alg_exp, variable, number)
        number_string: str = str(number)
        if isinstance(alg_exp, VariableAtomicAlgExp):
            if alg_exp.normalized_variable == variable:
                if alg_exp.is_minus_variable():
                    if number_string.startswith(Ad.MINUS):  # minus and minus is plus
                        alg_exp._content = number_string[1:]
                    else:  # minus and plus is minus
                        alg_exp._content = f"{Ad.MINUS}{number_string}"
                else:
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
            print(f"variables_domains: {alg_exp_outer.variables_domains}")
            print(f"immutable_contents: {alg_exp_outer.immutable_contents}")
        except Exception as err:
            print(err)
