from abc import ABC, abstractmethod
from copy import deepcopy
import re
from typing import Any, List, Tuple

from algebradata import AlgebraData as Ad
from algexptools import AlgExp
from errormessages import ErrorMessages


class VariableAlgExp(AlgExp, ABC):
    """
    Abstract class for algebraic expressions that contain at least one variable.
    - VariableAtomicAlgExp       variable expression without operations
    - VariableCompositeAlgExp    variable expression with operations
    """
    _PREFIX: str = "VariableAlgExp"
    _ERR: str = f"{_PREFIX}Error: "

    # common variables
    _immutable_contents: dict = None
    _variables_domains: dict = None

    def __init__(self, expression: Any, variables_domains: dict = None):
        super().__init__(expression)
        self.__create_variable_domains(expression, variables_domains)
        self.__create_immutable_contents(expression)

    @abstractmethod
    def _found_and_get_all_variables(self) -> list:
        """
        Returns list of all variables in self-expression.
        :return: list of all variables in self-expression
        """
        return NotImplemented

    @property
    def immutable_contents(self):
        return self._immutable_contents

    @property
    def variables(self):
        return self._found_and_get_all_variables()

    @property
    def variables_domains(self) -> dict:
        return self._variables_domains

    def _correction(self, expression: str) -> str:
        # substitution for immutable contents
        immutable_contents: dict = self.__found_and_get_immutable_contents(expression)
        expression = self.__substitute_immutable_areas(expression, immutable_contents)
        expression = super()._correction(expression)
        # reverse substitution to the original content
        expression = self.__substitute_immutable_areas(expression, immutable_contents, reverse=True)
        return expression

    def _create_content_from_other_instance(self, expression):
        super()._create_content_from_other_instance(expression)

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        new_asserts: list = [
            (isinstance(variables_domains, dict) or variables_domains is None,
             "variables_domains must be dict or None"),
            (not isinstance(expression, str) or expression.count(left_imm_br) == expression.count(right_imm_br),
             f"The numbers of '{left_imm_br}' and '{right_imm_br}' brackets must be the same."),
        ]
        self._asserts += new_asserts
        super()._init_check(expression)

    def _replace_immutable_areas(self, expression: str, replace_character: str = Ad.SUBSTITUTION_CHARACTER) -> str:
        """
        Replaces all characters in immutable areas with replace_character.
        :param expression: any algebraic expression
        :param replace_character: any character [#]
        :return: expression that has all characters in immutable areas replaced
        """
        areas: list = self.__get_immutable_content_areas(expression)
        expression_list: list = list(expression)
        for area in areas:
            start_index, end_index = area
            for i in range(start_index, end_index + 1):
                expression_list[i] = replace_character
        return "".join(expression_list)

    def __create_immutable_contents(self, expression: Any) -> None:
        """
        Creates substitution dictionary named as immutable_contents for all immutable
        contents of expression and stores this dictionary in self variable.
        :param expression: any algebraic expression
        :return: None
        """
        if isinstance(expression, VariableAlgExp):
            self._immutable_contents = deepcopy(expression.immutable_contents)
            return
        self._immutable_contents = deepcopy(self.__found_and_get_immutable_contents(expression))

    def __create_variable_domains(self, expression: Any, variables_domains: dict | None) -> None:
        """
        Creates variable domains for all variable in expression.
        :param expression: any algebraic expression
        :param variables_domains: predefined domains or None
        :return: None
        """
        if variables_domains is None:
            if isinstance(expression, str):
                self._variables_domains = self.__generate_default_variables_domains()
            elif isinstance(expression, VariableAlgExp):
                self._variables_domains = deepcopy(expression.variables_domains)
        else:
            self.__check_variables_domains(variables_domains)
            self._variables_domains = deepcopy(variables_domains)

    def __found_and_get_immutable_contents(self, expression: str) -> dict:
        """
        Creates substitution dictionary for all immutable contents of expression.
        :param expression: any algebraic expression
        :return: substitution dictionary for all immutable contents of expression
        """
        immutable_areas: list = self.__get_immutable_content_areas(expression)
        immutable_contents: dict = {}
        for area in immutable_areas:
            start_index, end_index = area
            actual_content = expression[start_index: end_index + 1]
            if actual_content not in immutable_contents:
                immutable_contents[actual_content] = f"{Ad.SUBSTITUTION_CHARACTER}{self._substitution_index}"
                self._substitution_index += 1
        return immutable_contents

    def __generate_default_variables_domains(self) -> dict:
        """
        Creates default variable domains for all variables in self-expression.
        Default variable domain for every variable is in this case open interval (-inf, inf).
        :return: default variable domains for all variables in self-expression
        """
        from algsettools import IntervalAlgSet
        return {variable: IntervalAlgSet() for variable in self.variables}

    def __get_immutable_content_areas(self, expression: str) -> list:
        """
        Searches immutable content areas in expression and after that, returns these areas.
        This is very dirty work method.
        No grandeur, no abstraction. Just plain prehistoric index butchery.
        This method is in its ground-work, at the very bottom. This method is truly priceless.
        :param expression: any algebraic expression
        :return: all immutable contents areas for expression
        """
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        analyzed_brackets: List[Tuple[str, str]] = [(left_imm_br, right_imm_br)]
        bracketing: list = self._bracketing(expression, analyzed_brackets)
        areas: list = []
        start_index, end_index = -1, -1
        is_deep_level: bool = False
        for i, deep_level in enumerate(bracketing):
            if deep_level == 1 and not is_deep_level:
                # start of new area
                start_index = i + 1
                is_deep_level = True
                continue
            if deep_level == 0 and is_deep_level:
                # end of current area
                end_index = i - 1
                if start_index == -1:
                    is_not_variable: str = ErrorMessages.replace(ErrorMessages.IS_NOT_VARIABLE, expression)
                    raise ValueError(f"{self._ERR}{is_not_variable}")
                if start_index <= end_index:
                    areas.append((start_index, end_index))
                is_deep_level = False
                continue
        return areas

    def __check_variables_domains(self, variables_domains: dict) -> None:
        """
        Checks whether any set from variable domains is not an empty set.
        If such a set is found, it throws an exception.
        :param variables_domains: variable domains for all variables in expression
        :return: None
        """
        from algsettools import DiscreteAlgSet
        for variable, alg_set in variables_domains.items():
            if isinstance(alg_set, DiscreteAlgSet):
                var_has_empty_domain: str = ErrorMessages.replace(ErrorMessages.VAR_HAS_EMPTY_SET_DOMAIN, variable)
                assert not alg_set.is_empty(), f"{self._ERR}{var_has_empty_domain}"

    def __substitute_immutable_areas(self, expression: str, immutable_contents: dict, reverse: bool = False) -> str:
        """
        Substitutes all immutable areas in expression.
        :param expression: any algebraic expression
        :param immutable_contents: all immutable contents of expression
        :param reverse: flag for reverse substitution
        :return: expression with substituted immutable areas
        """
        left_imm_br, right_imm_br = Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET
        if reverse:
            immutable_contents: dict = {sub_id: content for (content, sub_id) in immutable_contents.items()}
            self._substitution_index = 1
        for key in immutable_contents:
            expression = expression.replace(f"{left_imm_br}{key}{right_imm_br}",
                                            f"{left_imm_br}{immutable_contents[key]}{right_imm_br}")
        return expression

    @staticmethod
    def substituted(alg_exp, subs_dict: dict):
        """
        Returns new instance of VariableAlgExp with substituted variables
        based on substitution dictionary.
        :param alg_exp: any variable algebraic expression
        :param subs_dict: dictionary with {key: value} <=> {variable: number to substitute}
        :return: instance of AlgExp
        """
        new_instance = deepcopy(alg_exp)
        must_be_instance: str = ErrorMessages.replace(ErrorMessages.EXP_MUST_BE_INSTANCE, VariableAlgExp.__name__)
        assert isinstance(alg_exp, VariableAlgExp), f"{AlgExp._ERR}{must_be_instance}"
        for variable in subs_dict:
            if variable in new_instance:
                type(new_instance)._substitute(new_instance, variable, subs_dict[variable])
        exp_result = AlgExp.initializer(str(new_instance))
        del new_instance  # this instance may contain conflicting data, it served only for content substitution
        return exp_result

    @staticmethod
    def _substitute(alg_exp, variable: str, number: Any):
        """
        Returns alg_exp with variable substituted for number.
        :param alg_exp: any variable algebraic expression
        :param variable: variable which will be substituted
        :param number: number for substitute
        :return: alg_exp with substituted content
        """
        allowed_subs_types: tuple = (int, str)
        types_names: str = " | ".join([x.__name__ for x in allowed_subs_types])
        must_be_instance: str = ErrorMessages.replace(ErrorMessages.NUMBER_MUST_BE_INSTANCE, types_names)
        assert isinstance(number, allowed_subs_types), f"{VariableAlgExp._ERR}{must_be_instance}"
        if isinstance(number, str):
            assert re.search(rf"{Ad.MINUS}?\d+", number), f"{AlgExp._ERR}{ErrorMessages.MUST_BE_INTEGER}"
