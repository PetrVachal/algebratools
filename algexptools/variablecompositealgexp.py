from typing import Any, List, Tuple
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

    def _alg_exp_structure(self, expression: str) -> list:
        from algexptools import VariableAlgExp
        left_br, right_br = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        analyzed_brackets: List[Tuple[str, str]] = [(left_br, right_br), (left_imm_br, right_imm_br)]
        is_not_composite: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, CompositeAlgExp.__name__)
        split_indexes: dict = {operator: [] for operator in Ad.OPERATORS}
        expression_parts: list = []
        operator_for_split: str = ""
        contains_variable: bool = False
        bracketing: list = self._bracketing(expression, analyzed_brackets)
        for i, deep_level in enumerate(bracketing):
            if deep_level == 0 and expression[i] in Ad.OPERATORS:
                actual_operator: str = expression[i]
                split_indexes[actual_operator].append(i)
        for operator in Ad.OPERATORS:
            if split_indexes[operator]:
                split_indexes[operator].append(len(expression))
                operator_for_split = operator
                start_index: int = 0
                for actual_index in split_indexes[operator_for_split]:
                    inner_alg_exp = AlgExp.initializer(expression[start_index:actual_index])
                    if not contains_variable and isinstance(inner_alg_exp, VariableAlgExp):
                        contains_variable = True
                    expression_parts.append(inner_alg_exp)
                    start_index = actual_index + 1
                break
        if operator_for_split == "":
            raise ValueError(f"{self._ERR}{is_not_composite}")
        if not contains_variable:
            raise ValueError(f"{self._ERR}{ErrorMessages.MUST_CONTAIN_VARIABLE}")
        self._operator = operator_for_split
        return expression_parts

    def _create_content_from_str(self, expression: str) -> None:
        corrected_expression: str = self._correction(expression)
        self._content = self._alg_exp_structure(corrected_expression)

    def _found_and_get_all_variables(self) -> list:
        variables: list = []
        for inner_alg_exp in self._content:
            if isinstance(inner_alg_exp, VariableAlgExp):
                variables += inner_alg_exp._found_and_get_all_variables()
        return list(set(variables))

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        is_variable_exp: bool = False
        try:
            AlgExp.initializer(expression, NumericAtomicAlgExp, NumericCompositeAlgExp, VariableAtomicAlgExp)
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
        except Exception as err:
            print(err)
