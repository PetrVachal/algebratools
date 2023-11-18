from typing import Any
import re

from algebradata import AlgebraData as Ad
from algexptools import AlgExp, CompositeAlgExp, NumericAtomicAlgExp, NumericCompositeAlgExp, VariableAlgExp, \
    VariableAtomicAlgExp
from errormessages import ErrorMessages
from patterns import Patterns


class VariableCompositeAlgExp(VariableAlgExp, CompositeAlgExp):
    """
    Contains variable with at least one operation.
    """

    _PREFIX: str = "VariableCompositeAlgExp"
    _ERR: str = f"{_PREFIX}Error: "

    # other variables
    _allowed_content_pattern = re.compile(Patterns.ALLOWED_VARIABLE_COMPOSITE_CONTENT)

    def __init__(self, expression: Any, variables_domains: dict = None):
        self._correction_methods = (self._add_multiply_operators, self._replace_minuses)
        VariableAlgExp.__init__(self, expression, variables_domains)

    def _create_content_from_str(self, expression: str) -> None:
        corrected_expression: str = self._correction(expression)
        self._content = self._alg_exp_structure(corrected_expression, is_variable_exp=True)

    def _found_and_get_all_variables(self) -> list:
        variables: list = []
        for inner_alg_exp in self._content:
            if isinstance(inner_alg_exp, VariableAlgExp):
                variables += inner_alg_exp._found_and_get_all_variables()
        return list(set(variables))

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        is_variable_exp: bool = False
        try:
            AlgExp.initializer(expression, (NumericAtomicAlgExp, NumericCompositeAlgExp, VariableAtomicAlgExp))
        except ValueError:
            is_variable_exp = True
        self._allowed_types = {}
        self._asserts = [
            (
                not isinstance(expression, str) or Ad.LEFT_IMMUTABLE_BRACKET in expression or re.search(
                    self._allowed_content_pattern, self._replace_immutable_areas(expression)),
                "Expression must be a variable without any operations (see doc)"),
            (
                is_variable_exp,
                "Expression must be a variable without any operations (see doc)")
        ]
        super()._init_check(expression)

    @staticmethod
    def _substitute(alg_exp, variable: str, number: Any):
        super()._substitute(alg_exp, variable, number)
        number_string: str = str(number)
        assert re.search(rf"{Ad.MINUS}?\d+", number_string), f"{AlgExp._ERR}{ErrorMessages.MUST_BE_INTEGER}"
        if isinstance(alg_exp, VariableCompositeAlgExp):
            for inner_exp in alg_exp.content:
                if isinstance(inner_exp, VariableAlgExp):
                    changed_inner_exp = type(inner_exp)._substitute(inner_exp, variable, number_string)
                    inner_exp._content = changed_inner_exp.content
        return alg_exp


if __name__ == '__main__':
    while True:
        alg_exp_input: str = input(": ")
        if alg_exp_input == "exit":
            break
        try:
            alg_exp_outer: VariableCompositeAlgExp = VariableCompositeAlgExp(alg_exp_input)
            print(f"exp: {alg_exp_outer}")
            print(f"variables: {alg_exp_outer.variables}")
            print(f"variables_domains: {alg_exp_outer.variables_domains}")
            print(f"immutable_contents: {alg_exp_outer.immutable_contents}")
        except Exception as err:
            print(err)
