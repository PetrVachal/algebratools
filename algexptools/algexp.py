from abc import ABC, abstractmethod
from inspect import isabstract
import re
from typing import Any, Tuple

import algexptools
from algebradata import AlgebraData as Ad
from errormessages import ErrorMessages
from patterns import Patterns


class AlgExp(ABC):
    """
    Abstract class for all kinds of algebraic expressions:

    - NumericAtomicAlgExp     numeric expression without operations
    - NumericCompositeAlgExp  numeric expression with operations
    - VariableAtomicAlgExp    variable expression without operations
    - VariableCompositeAlgExp variable expression with operations
    """

    # common variables
    _content: list | str = None

    # other variables
    _allowed_content_pattern: re = None
    _allowed_types: dict = None
    _asserts: list = None
    _correction_methods: tuple = None
    _special_numeric_strings_substitutions: dict = None
    _substitution_index: int = None

    def __init__(self, expression: Any):
        self._correction_methods = (self._remove_white_spaces, self._remove_redundant_pluses_minuses,
                                    self._remove_outer_brackets) + self._correction_methods
        self._special_numeric_strings_substitutions = {}
        self._substitution_index = 1
        self._init_check(expression)
        self._create_content(expression)

    @abstractmethod
    def __str__(self):
        return NotImplemented

    @abstractmethod
    def has_imag(self) -> bool:
        """
        If expression contains an imaginary unit, returns True.
        Otherwise, returns False.
        :return: see doc
        """
        return NotImplemented

    @abstractmethod
    def _create_content_from_str(self, expression: str):
        """
        Creates specific structure (named as content) from an expression string.
        :param expression: any algebraic expression
        :return: None
        """
        return NotImplemented

    def __add__(self, other):
        return self.__magic_operation_method_result(other, Ad.PLUS)

    def __contains__(self, item):
        from algexptools import AtomicAlgExp
        assert isinstance(item, (int, str, AtomicAlgExp)), ErrorMessages.TYPE_FOR_ITEM_IN_CONTAINS

    def __mul__(self, other):
        return self.__magic_operation_method_result(other, Ad.MULTIPLY)

    def __neg__(self):
        from algexptools import AtomicAlgExp
        if isinstance(self, AtomicAlgExp):
            return AlgExp.initializer(f"{Ad.MINUS}{self}")
        return AlgExp.initializer(f"{Ad.MINUS}{Ad.LEFT_BRACKET}{self}{Ad.RIGHT_BRACKET}")

    def __pos__(self):
        return AlgExp.initializer(self)

    def __pow__(self, power, modulo=None):
        return self.__magic_operation_method_result(power, Ad.POWER)

    def __radd__(self, other):
        return self.__magic_operation_method_r_result(other, AlgExp.__add__)

    def __repr__(self):
        return str(self)

    def __rmul__(self, other):
        return self.__magic_operation_method_r_result(other, AlgExp.__mul__)

    def __rpow__(self, other):
        return self.__magic_operation_method_r_result(other, AlgExp.__pow__)

    def __rsub__(self, other):
        return self.__magic_operation_method_r_result(other, AlgExp.__sub__)

    def __rtruediv__(self, other):
        return self.__magic_operation_method_r_result(other, AlgExp.__truediv__)

    def __sub__(self, other):
        return self.__magic_operation_method_result(other, Ad.MINUS)

    def __truediv__(self, other):
        return self.__magic_operation_method_result(other, Ad.DIV)

    @property
    def content(self):
        return self._content

    def _correction(self, expression: str) -> str:
        """
        With the correction methods given for each instance, it corrects
        the string expression to create content.
        :param expression: any algebraic expression
        :return: string expression in the correct format to create content
        """
        # substitute all special numeric strings
        expression = self._substitute_all_special_numeric_strings(expression)
        original_expression: str = ""
        while expression != original_expression:
            original_expression = expression
            for method in self._correction_methods:
                expression = method(expression)
        # reverse substitute all special numeric strings
        expression = self._substitute_all_special_numeric_strings(expression, reverse=True)
        return expression

    def _create_content(self, expression: Any) -> None:
        """
        Creates content based one the type of an algebraic expression.
        :param expression: any algebraic expression
        :return: None
        """
        self._allowed_types[type(expression)](expression)

    def _create_content_from_other_instance(self, expression) -> None:
        """
        Creates content from other instance of an algebraic expression.
        :param expression: any algebraic expression
        :return: None
        """
        must_be_instance: str = ErrorMessages.replace(ErrorMessages.MUST_BE_INSTANCE, "Expression",
                                                      self.__class__.__name__)
        assert isinstance(expression, self.__class__), must_be_instance
        self._content = expression.content[:]

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        """
        Sniper filter for throwing an exception if the parameters are invalid.
        :param expression: any algebraic expression
        :param variables_domains: definition domains of variables
        :return: None
        """
        left_br, right_br = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET
        new_allowed_types: dict = {str: self._create_content_from_str,
                                   self.__class__: self._create_content_from_other_instance}
        self._allowed_types.update(new_allowed_types)
        types_string: str = "(" + ", ".join([x.__name__ for x in self._allowed_types]) + ")"
        new_asserts: list = [
            (isinstance(expression, tuple(self._allowed_types)),
             f"expression must be in {types_string}"),
            (not isinstance(expression, str) or expression.count(left_br) == expression.count(right_br),
             f"The numbers of '{left_br}' and '{right_br}' brackets must be the same."),
        ]
        self._asserts += new_asserts
        for condition, err_message in self._asserts:
            assert condition, err_message

    def _is_wrapped_in_brackets(self, expression: str, left_br: str = Ad.LEFT_BRACKET,
                                right_br: str = Ad.RIGHT_BRACKET) -> bool:
        """
        Returns True if the whole expression is wrapped in brackets.
        Otherwise, returns False.
        :param expression: any algebraic expression
        :param left_br: some type of left bracket
        :param right_br: some type of right bracket
        :return: see doc
        """
        analyzed_brackets: list = [(left_br, right_br)]
        if len(expression) > 2 and self._bracketing(expression, analyzed_brackets).count(0) == 1:
            return True
        return False

    def _remove_outer_brackets(self, expression: str) -> str:
        """
        Returns an expression without unnecessary brackets.
        :param expression: any algebraic expression
        :return: see doc
        """
        while self._is_wrapped_in_brackets(expression):
            expression = expression[1:-1]
        return expression

    def _substitute_all_special_numeric_strings(self, expression: str, reverse: bool = False) -> str:
        """
        Substitutes all special numeric strings in expression.
        :param expression: any algebraic expression
        :param reverse: flag for reverse substitution
        :return: expression with substituted special numeric strings
        """
        substitutions: dict = self._special_numeric_strings_substitutions
        replaced_string: str = expression
        if reverse:
            for special_string in substitutions:
                wrapped_subs_string: str = f"{Ad.LEFT_BRACKET}{substitutions[special_string]}{Ad.RIGHT_BRACKET}"
                replaced_string = replaced_string.replace(wrapped_subs_string, special_string)
            self._substitution_index = 1
            return replaced_string
        for special_string in Ad.SPECIAL_NUMERIC_STRINGS:
            replaced_string = self.__substitute_special_numeric_string(replaced_string, special_string)
        return replaced_string

    def __magic_operation_method_result(self, other, operator: str):
        left_br, right_br = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET
        exp_other = AlgExp.initializer(other)
        add_result: str = f"{left_br}{self}{right_br}{operator}{left_br}{exp_other}{right_br}"
        return AlgExp.initializer(add_result)

    def __magic_operation_method_r_result(self, other, magic_operation_method):
        exp1 = AlgExp.initializer(other)
        return magic_operation_method(exp1, self)

    def __substitute_special_numeric_string(self, expression: str, special_string: str) -> str:
        """
        Substitutes special numeric string in expression based on allowed patterns in this method.
        After that, returns this substituted expression.
        :param expression: any algebraic expression
        :param special_string: any special string from special numeric strings
        :return: expression with substituted special numeric string
        """
        left_br, right_br, i = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET, Ad.IMAG_UNIT
        subs_chr, subs_index = Ad.SUBSTITUTION_CHARACTER, self._substitution_index
        var_chars, var_chars_without_i = Patterns.ALLOWED_VAR_CHARS, Patterns.ALLOWED_VAR_CHARS_WITHOUT_IMAG_UNIT
        replaced_string: str = expression
        subs_string: str = f"{subs_chr}{subs_index}"
        allowed_patterns: tuple = (
            rf"^({special_string})[^{var_chars}]",
            rf"[^{var_chars}]({special_string})[^{var_chars}]",
            rf"[^{var_chars}]({special_string})$",
            rf"^({special_string}){i}",
            rf"{i}({special_string})$",
            rf"{i}({special_string}){i}",
            rf"{i}({special_string})[^{var_chars}]",
            rf"[^{var_chars}]({special_string}){i}",
        )
        pattern_for_special_string = re.compile("|".join(allowed_patterns))
        founds = re.search(pattern_for_special_string, expression)
        if founds is None:
            return expression
        for founds_index in range(1, len(allowed_patterns) + 1):
            if founds.group(founds_index):
                replaced_string = str(
                    re.subn(founds.group(founds_index), f"{left_br}{subs_string}{right_br}", replaced_string)[0])
        self._special_numeric_strings_substitutions[special_string] = subs_string
        self._substitution_index += 1
        return replaced_string

    @staticmethod
    def initializer(expression: Any = 0, *args):
        """
        Returns an instance of AlgExp based on classes for initialization.
        :param expression: any algebraic expression
        :param args: classes given to create an instance of AlgExp
        :return: instance of AlgExp
        """
        def __all_subclasses(top_cls, allow_abstract: bool = False) -> tuple:
            """
            Returns all subclasses of top class.
            If allow_abstract is set on True, then abstract classes are also returned.
            Otherwise, only concrete classes are returned.
            :param top_cls: class from which its subclasses are searched
            :param allow_abstract: flag for abstract classes [False]
            :return: all subclasses of top class (with/without abstract classes depending on allow_abstract)
            """
            actual_cls = top_cls
            all_subclasses: tuple = (actual_cls,)
            for cls in actual_cls.__subclasses__():
                all_subclasses += __all_subclasses(cls)
            if not allow_abstract:
                all_subclasses = tuple(cls for cls in all_subclasses if not isabstract(cls))
            return all_subclasses

        classes_for_init = args
        if classes_for_init == ():
            classes_for_init = __all_subclasses(AlgExp)
        for actual_class in classes_for_init:
            try:
                return actual_class(expression)
            except (algexptools.AlgExpError, AssertionError):
                pass
        is_not_alg_exp: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, AlgExp.__name__)
        raise algexptools.AlgExpError(is_not_alg_exp)

    @staticmethod
    def _bracketing(expression: str, analyzed_brackets: list = None) -> list:
        """
        Returns brackets structure in expression like string.
        Each character is analyzed for its brackets deep level and each such level as a number
        is stored in the bracketing list. Finally, this list is returned.
        e.g. "a*(b+c)" => [0, 0, 1, 1, 1, 1, 0]
        e.g. "2*(1+3)+4*(5-(6+7))" => [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 1, 0]
        :param expression: any algebraic expression
        :param analyzed_brackets: brackets that are analyzed during bracketing
        :return: list of brackets deep levels for each character in expression string
        """
        if analyzed_brackets is None:
            analyzed_brackets = [(Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET)]
        analyzed_left_brackets: Tuple[str] = tuple(brackets_pair[0] for brackets_pair in analyzed_brackets)
        analyzed_right_brackets: Tuple[str] = tuple(brackets_pair[1] for brackets_pair in analyzed_brackets)
        bracketing: list = []
        brackets_level: int = 0
        for character in expression:
            if character in analyzed_left_brackets:
                brackets_level += 1
            elif character in analyzed_right_brackets:
                brackets_level -= 1
            bracketing.append(brackets_level)
        return bracketing

    @staticmethod
    def _remove_redundant_pluses_minuses(expression: str) -> str:
        """
        Removes redundant pluses and minuses based on pattern and replace table in this method.
        Finally, the method removes unnecessary pluses from the beginning of the string
        and all pluses that follow the left bracket.
        :param expression: any algebraic expression
        :return: expression string without redundant pluses and minuses
        """
        minus, plus = Ad.MINUS, Ad.PLUS
        left_br: str = Ad.LEFT_BRACKET
        pattern_redundant_pluses_minuses = re.compile("[" + minus + plus + "]{2}")
        replace_table: dict = {f"{minus}{minus}": plus, f"{minus}{plus}": minus, f"{plus}{minus}": minus,
                               f"{plus}{plus}": plus}
        while re.findall(pattern_redundant_pluses_minuses, expression):
            for redundant_string in replace_table:
                expression = expression.replace(redundant_string, replace_table[redundant_string])
        if expression.startswith(plus):
            expression = expression[1:]
        expression = expression.replace(left_br + plus, left_br)
        return expression

    @staticmethod
    def _remove_white_spaces(expression: str) -> str:
        """
        Removes all white spaces from expression string and after that this replaced string is returned.
        :param expression: any algebraic expression
        :return: expression string without any white spaces
        """
        pattern_white_spaces = re.compile(Patterns.WHITE_SPACES)
        return re.sub(pattern_white_spaces, "", expression)
