from abc import ABC
from typing import List, Tuple
import re

from algebradata import AlgebraData as Ad
from algexptools import AlgExp
from errormessages import ErrorMessages
from patterns import Patterns


class CompositeAlgExp(AlgExp, ABC):
    """
    Abstract class for composite algebraic expressions <=> expressions with at least one operation.
    - NumericCompositeAlgExp   complex number with operations
    - VariableCompositeAlgExp  variables with operations
    """
    _PREFIX: str = "CompositeAlgExp"
    _ERR: str = f"{_PREFIX}Error: "

    # common variables
    _content: list = None
    _operator: str = None
    _simplified: bool = False

    def __contains__(self, item):
        super().__contains__(item)
        string_item: str = str(item)
        for inner_exp in self._content:
            if string_item in inner_exp:
                return True
        return False

    def __str__(self):
        left_br, right_br = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET
        operators: tuple = Ad.OPERATORS
        composite_string_content: str = ""
        for inner_alg_exp in self._content:
            if not isinstance(inner_alg_exp, CompositeAlgExp) and isinstance(inner_alg_exp, AlgExp):
                if inner_alg_exp.content.startswith(Ad.MINUS):
                    composite_string_content += f"{left_br}{inner_alg_exp}{right_br}{self._operator}"
                else:
                    composite_string_content += f"{inner_alg_exp}{self._operator}"
            # inner_alg_exp is composite
            elif operators.index(self._operator) > operators.index(inner_alg_exp.operator):
                composite_string_content += f"{left_br}{inner_alg_exp}{right_br}{self._operator}"
            elif self._operator == inner_alg_exp.operator == Ad.DIV:
                composite_string_content += f"{left_br}{inner_alg_exp}{right_br}{self._operator}"
            else:  # self._operator has lower priority than inner_alg_exp.operator
                composite_string_content += f"{inner_alg_exp}{self._operator}"
        return composite_string_content[:-1]

    @property
    def operator(self):
        return self._operator

    @property
    def simplified(self):
        return self._simplified

    def has_imag(self) -> bool:
        for inner_alg_exp in self._content:
            if inner_alg_exp.has_imag():
                return True
        return False

    def _alg_exp_structure(self, expression: str, is_variable_exp: bool) -> list:
        """
        Creates specific structure (named as content) for self instance from actual
        expression string.
        If content is to be created for a variable type, flag is_variable_exp is set
        to True. Otherwise, it is set to False.
        :param expression: any algebraic expression
        :param is_variable_exp: flag for structure for variable expression
        :return: specific structure named as content for actual expression string
        """
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
        if not contains_variable and is_variable_exp:
            raise ValueError(f"{self._ERR}{ErrorMessages.MUST_CONTAIN_VARIABLE}")
        self._operator = operator_for_split
        return expression_parts

    def _create_content_from_other_instance(self, expression):
        super()._create_content_from_other_instance(expression)
        self._operator = expression.operator

    def _check_content(self) -> None:
        """
        Searches in expression all inner expressions and checks in each of them
        whether it is divisible by zero. If so, it throws an exception.
        :return: None
        """
        for inner_alg_exp in self._content[1:]:
            if self._operator == Ad.DIV and inner_alg_exp.content == "0":
                raise ZeroDivisionError(f"{self._ERR}: {ErrorMessages.CANNOT_DIV_BY_ZERO}")
            if isinstance(inner_alg_exp, CompositeAlgExp):
                inner_alg_exp._check_content()

    def _replace_minuses(self, expression: str) -> str:
        """
        Using the method to find replaceable minuses, it replaces these minuses
        with the string "+(-1)*".
        :param expression: any algebraic expression
        :return: expression string with some minuses replaced
        """
        minus, plus = Ad.MINUS, Ad.PLUS
        left_br, right_br = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET
        multiply = Ad.MULTIPLY
        replace_string: str = f"{plus}{left_br}{minus}1{right_br}{multiply}"  # == "+(-1)*"
        for index_allowed in reversed(self.__indexes_of_minuses_for_replace(expression)):
            expression = expression[:index_allowed] + replace_string + expression[index_allowed + 1:]
        if expression.startswith(plus):
            expression = expression[1:]
        expression = expression.replace(left_br + plus, left_br)
        return expression

    def __indexes_of_minuses_for_replace(self, expression: str) -> list:
        """
        Returns a list of indexes intended for substitution for another string.
        :param expression: any algebraic expression
        :return: see doc
        """
        minus: str = Ad.MINUS
        left_br, right_br = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        indexes_allowed: list = []
        indexes_restricted: list = []
        minus_one_in_brackets: str = rf"\{left_br}{minus}1\{right_br}"
        pattern_minus_one_in_brackets = re.compile(minus_one_in_brackets)
        if minus not in expression:
            return []
        if self._is_wrapped_in_brackets(expression, left_imm_br, right_imm_br):
            return []
        if expression == f"{minus}1":
            return []
        for found in re.finditer(pattern_minus_one_in_brackets, expression):
            indexes_restricted.append(found.start() + minus_one_in_brackets.index(minus) - 1)
        for i, character in enumerate(expression):
            if character == minus and i not in indexes_restricted:
                indexes_allowed.append(i)
        return indexes_allowed

    @staticmethod
    def _add_multiply_operators(expression: str) -> str:
        """
        In places determined by combinations of characters, it inserts *
        between these two characters, in all their occurrences.
        :param expression: any algebraic expression
        :return: expression string with the character "*" completed in the given places
        """
        variable: str = rf"[{Patterns.ALLOWED_VAR_CHARS}]"
        digit: str = r"\d"
        left_br: str = "\\" + Ad.LEFT_BRACKET
        right_br: str = "\\" + Ad.RIGHT_BRACKET
        left_imm_br: str = "\\" + Ad.LEFT_IMMUTABLE_BRACKET
        right_imm_br: str = "\\" + Ad.RIGHT_IMMUTABLE_BRACKET
        combinations_for_multiply = (
            digit + variable,  # 2x
            digit + left_br,  # 2(
            digit + left_imm_br,  # 2{
            variable + digit,  # x2
            variable + variable,  # xx
            variable + left_br,  # x(
            variable + left_imm_br,  # x{
            right_br + digit,  # )2
            right_br + variable,  # )x
            right_br + left_br,  # )(
            right_br + left_imm_br,  # ){
            right_imm_br + digit,  # }2
            right_imm_br + variable,  # }x
            right_imm_br + left_br,  # }(
            right_imm_br + left_imm_br,  # }{
        )
        pattern_combinations_for_multiply = re.compile("|".join(combinations_for_multiply))
        while re.findall(pattern_combinations_for_multiply, expression):
            for found_string in re.findall(pattern_combinations_for_multiply, expression):
                expression = expression.replace(found_string, found_string[0] + Ad.MULTIPLY + found_string[1])
        return expression
