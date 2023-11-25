from typing import Any
import re

from algebradata import AlgebraData as Ad
from algexptools import AlgExp, AtomicAlgExp, VariableAlgExp
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

    def is_immutable_content(self):
        return self._is_wrapped_in_brackets(self._content, Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET)

    def substitute(self, number: Any):
        """
        Returns new NumericAlgExp instance of given number
        :param number: any number for NumericAlgExp initialization
        :return: see doc
        """
        from algexptools import NumericAtomicAlgExp, NumericCompositeAlgExp
        self._substitute_check(self._variables[0], number)
        return AlgExp.initializer(number, NumericAtomicAlgExp, NumericCompositeAlgExp)

    def _create_content_from_str(self, expression: str) -> None:
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        is_not_atomic: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, AtomicAlgExp.__name__)
        corrected_expression: str = self._correction(expression)
        assert not corrected_expression.startswith(
            f"{Ad.MINUS}{left_imm_br}"), f"{self._ERR}{ErrorMessages.MUST_BE_ATOMIC_VARIABLE}"
        assert self._is_wrapped_in_brackets(corrected_expression, left_imm_br, right_imm_br) or re.search(
            self._allowed_content_pattern, corrected_expression), f"{self._ERR}{is_not_atomic}"
        self._variables = [self]
        self._content = corrected_expression

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        self._allowed_types = {}
        self._asserts = [
            (
                not isinstance(expression, str) or Ad.LEFT_IMMUTABLE_BRACKET in expression or re.search(
                    self._allowed_content_pattern, self._replace_immutable_areas(expression)),
                ErrorMessages.MUST_BE_ATOMIC_VARIABLE)
        ]
        super()._init_check(expression)


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
        except Exception as err:
            print(err)
