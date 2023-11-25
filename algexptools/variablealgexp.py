from abc import ABC, abstractmethod
from copy import copy, deepcopy
from functools import singledispatchmethod
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
    _variables: list = None
    _variables_domains: dict = None

    def __init__(self, expression: Any, variables_domains: dict = None):
        super().__init__(expression)
        if variables_domains is None:
            self.__create_variables_domains(expression)
        else:
            self.__create_variables_domains(variables_domains)
        self.__create_immutable_contents(expression)

    @property
    def variables(self):
        return self._variables

    @property
    def variables_domains(self) -> dict:
        return self._variables_domains

    @abstractmethod
    def substitute(self, arg: Any):
        """
        Substitutes variables for numbers in all occurrences of the given variables.
        :param arg: substitution dictionary | number for substitution (depends on the instance type)
        :return: new substituted instance of self-expression
        """
        return NotImplemented

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
        self._variables = expression.variables[:]

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

    def _substitute_check(self, variable, number) -> bool:
        """
        Checks whether:
            1) it is possible to create NumericAlgExp instance from number
            --
            2) number is in variable domain of the variable
            for which is substituted
            --
            3) variable exist in self-expression
        Throws exception if point 1 is false or point 2 is false.
        Returns True if point 3 is true, otherwise returns False.
        :param variable: any VariableAtomicAlgExp instance or string content of this
        :param number: any number for NumericAlgExp initialization
        :return: True if point 3 is True, otherwise False
        """
        from algexptools import NumericAlgExp, NumericAtomicAlgExp, NumericCompositeAlgExp
        number_must_be_instance: str = ErrorMessages.replace(ErrorMessages.MUST_BE_INSTANCE,
                                                             "Expression for substitution", NumericAlgExp.__name__)
        exp_number = number
        if not isinstance(exp_number, (NumericAtomicAlgExp, NumericCompositeAlgExp)):
            try:
                exp_number = AlgExp.initializer(number, NumericAtomicAlgExp, NumericCompositeAlgExp)
            except (AssertionError, ValueError):
                raise ValueError(f"{self._ERR}{number_must_be_instance}")
        # exp_number is an instance of NumericAlgExp
        if (isinstance(variable, VariableAlgExp) and variable not in self._variables) or variable not in self:
            return False
        # variable is in self
        instance_variable = self._variable_by_content(variable.content) if isinstance(
            variable, VariableAlgExp) else self._variable_by_content(variable)
        number_is_not_in_variables_domains: str = ErrorMessages.replace(
            ErrorMessages.NUMBER_IS_NOT_IN_VARIABLE_DOMAIN, exp_number, self._variables_domains[instance_variable],
            self)
        assert exp_number in self._variables_domains[
            instance_variable], f"{self._ERR}{number_is_not_in_variables_domains}"
        return True

    def _variable_by_content(self, content: str):
        """
        Returns variable from self.variables with same content like content.
        :param content: string content of variable
        :return: found variable from self.variables
        """
        for variable in self._variables:
            if variable.content == content:
                return variable

    def __correct_variables_domains(self, variables_domains: dict) -> dict:
        """
        Stores variable instances in variables_domains keys instead of content strings.
        Further sets Interval(-inf, inf) as the default domain for variables
        without a specified domain.
        :param variables_domains: domains for all variables of self-expression
        :return: corrected variables domains
        """
        from algsettools import IntervalAlgSet
        new_variables_domains: dict = {}
        # storing instances in variables_domains keys
        for variable in variables_domains:
            if isinstance(variable, str):
                for instance_variable in self._variables:
                    if instance_variable.content == variable:
                        new_variables_domains[instance_variable] = variables_domains[variable]
                        break
        found: bool
        # occasional default domain assignment: Interval(-inf, inf)
        for variable_from_all in self._variables:
            found = False
            for variable_from_new_domains in new_variables_domains:
                if variable_from_new_domains.content == variable_from_all.content:
                    found = True
                    break
            if not found:
                new_variables_domains[variable_from_all] = IntervalAlgSet()
        return new_variables_domains

    def __create_immutable_contents(self, expression: Any) -> None:
        """
        Creates substitution dictionary named as immutable_contents for all immutable
        contents of expression and stores this dictionary in self variable.
        :param expression: any algebraic expression
        :return: None
        """
        if isinstance(expression, VariableAlgExp):
            self._immutable_contents = deepcopy(expression._immutable_contents)
            return
        self._immutable_contents = deepcopy(self.__found_and_get_immutable_contents(expression))

    @singledispatchmethod
    def __create_variables_domains(self, something):
        pass

    @__create_variables_domains.register(object)
    def _1(self, expression: Any) -> None:
        """
        Creates variable domains for all variable in expression.
        :param expression: any algebraic expression
        :return: None
        """
        if isinstance(expression, str):
            self._variables_domains = self.__generate_default_variables_domains()
            self.__refresh_variables_domains(self)
        elif isinstance(expression, VariableAlgExp):
            self._variables_domains = copy(expression.variables_domains)

    @__create_variables_domains.register(dict)
    def _2(self, variables_domains: dict) -> None:
        """
        Creates variable domains for all variable in expression.
        :param variables_domains: predefined domains
        :return: None
        """
        self.__check_variables_domains(variables_domains)
        new_variables_domains: dict = self.__correct_variables_domains(variables_domains)
        self._variables_domains = new_variables_domains
        self.__refresh_variables_domains(self)

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
        return {variable: IntervalAlgSet() for variable in self._variables}

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
                    is_not_variable: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression,
                                                                 VariableAlgExp.__name__)
                    raise ValueError(f"{self._ERR}{is_not_variable}")
                if start_index <= end_index:
                    areas.append((start_index, end_index))
                is_deep_level = False
                continue
        return areas

    def __check_variables_domains(self, variables_domains: dict) -> None:
        """
        Checks if all variables domains are instances of AlgSet.
        Further, checks whether any set from variable domains is not an empty set.
        If such a set is found, it throws an exception.
        :param variables_domains: variable domains for all variables in expression
        :return: None
        """
        from algsettools import AlgSet, DiscreteAlgSet
        must_be_instance: str = ErrorMessages.replace(ErrorMessages.MUST_BE_INSTANCE, "Variable domain",
                                                      AlgSet.__name__)
        for variable, alg_set in variables_domains.items():
            assert isinstance(alg_set, AlgSet), f"{self._ERR}{must_be_instance}"
            if isinstance(alg_set, DiscreteAlgSet):
                var_has_empty_domain: str = ErrorMessages.replace(ErrorMessages.VAR_HAS_EMPTY_SET_DOMAIN, variable)
                assert not alg_set.is_empty(), f"{self._ERR}{var_has_empty_domain}"

    def __refresh_variables_domains(self, alg_exp) -> None:
        """
        Refreshes variables domains in all inner expressions in alg_exp,
        based on self.variables.
        :param alg_exp: any variable algebraic expression
        :return: None
        """
        from algexptools import VariableCompositeAlgExp
        for inner_exp in alg_exp.content:
            if not isinstance(inner_exp, VariableAlgExp):
                continue
            if isinstance(inner_exp, VariableCompositeAlgExp):
                self.__refresh_variables_domains(inner_exp)
            inner_exp._variables_domains = {}
            for global_instance_variable in self._variables:
                if global_instance_variable.content in inner_exp:
                    inner_exp._variables_domains[global_instance_variable] = self._variables_domains[
                        global_instance_variable]

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
    def _found_and_get_all_variables_contents(pre_content: list | str) -> list:
        """
        Returns list of all variables contents in self-expression.
        :return: list of all variables contents in self-expression
        """
        if isinstance(pre_content, str):
            return [pre_content]
        variables: list = []
        for inner_alg_exp in pre_content:
            if isinstance(inner_alg_exp, VariableAlgExp):
                variables += VariableAlgExp._found_and_get_all_variables_contents(inner_alg_exp.content)
        return list(set(variables))
