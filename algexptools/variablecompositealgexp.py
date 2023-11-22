from inspect import stack
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
        stack_functions: list = [stack_info.function for stack_info in stack()]
        stack_trace_top_level: bool = stack_functions.count(stack_functions[0]) == 1
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
        variables_contents: list = VariableAlgExp._found_and_get_all_variables_contents(expression_parts)
        self._variables = [VariableAtomicAlgExp(exp) for exp in variables_contents]
        if stack_trace_top_level:
            self.__unify_same_variables(expression_parts)
        return expression_parts

    def _create_content_from_str(self, expression: str) -> None:
        corrected_expression: str = self._correction(expression)
        self._content = self._alg_exp_structure(corrected_expression)

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

    def __refresh_variables(self, alg_exp) -> None:
        """
        Refreshes instances of variables for alg_exp based on self.variables.
        :param alg_exp: any variable algebraic expression
        :return: None
        """
        source_indexes: List[int] = []
        for variable in alg_exp.variables:
            for i, global_instance_variable in enumerate(self.variables):
                if variable.content == global_instance_variable.content:
                    source_indexes.append(i)
        alg_exp._variables = []
        for source_index in source_indexes:
            alg_exp._variables.append(self._variables[source_index])

    def __unify_same_variables(self, pre_content: list) -> None:
        """
        Unifies all instances into a single one for the same variables
        in all expressions inside pre_content.
        :param pre_content: inner part of any instance of VariableCompositeAlgExp
        :return: None
        """
        variables_instances_by_content: dict = {variable.content: variable for variable in self._variables}
        substitution_dict: dict = {}
        for i, inner_exp in enumerate(pre_content):
            if isinstance(inner_exp, VariableAlgExp):
                if isinstance(inner_exp, VariableAtomicAlgExp):
                    substitution_dict[i] = variables_instances_by_content[inner_exp.content]
                else:
                    self.__unify_same_variables(inner_exp.content)
                self.__refresh_variables(inner_exp)
        for target_index in substitution_dict:
            pre_content[target_index] = substitution_dict[target_index]

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
