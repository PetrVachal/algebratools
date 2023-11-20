from fractions import Fraction
from typing import Any
import re

from algebradata import AlgebraData as Ad
from errormessages import ErrorMessages
from algexptools import AlgExp, AtomicAlgExp, CompositeAlgExp, NumericAlgExp, NumericAtomicAlgExp
from patterns import Patterns


class NumericCompositeAlgExp(NumericAlgExp, CompositeAlgExp):
    """
    Contains algebraic expression:
        1) without variables
        2) with at least one operation
    """
    _PREFIX: str = "NumericCompositeAlgExp"
    _ERR: str = f"{_PREFIX}Error: "

    # other variables
    _allowed_content_pattern = re.compile(Patterns.ALLOWED_NUMERIC_COMPOSITE_CONTENT)

    def __init__(self, expression: Any):
        self._correction_methods = (self._add_multiply_operators, self._replace_minuses)
        NumericAlgExp.__init__(self, expression)

        # other variables
        self.__cannot_determine_domain: str = ErrorMessages.replace(ErrorMessages.CANNOT_DETERMINE_DOMAIN, str(self))

    @property
    def value(self):
        match self._operator:
            case Ad.PLUS:
                result: complex = complex(0, 0)
                for inner_alg_exp in self._content:
                    result += inner_alg_exp.value
            case Ad.MINUS:
                result: complex = self._content[0].value
                for inner_alg_exp in self._content[1:]:
                    result -= inner_alg_exp.value
            case Ad.MULTIPLY:
                result: complex = complex(1, 0)
                for inner_alg_exp in self._content:
                    result *= inner_alg_exp.value
            case Ad.DIV:
                result: complex = self._content[0].value
                for inner_alg_exp in self._content[1:]:
                    if inner_alg_exp.value == 0:
                        raise ZeroDivisionError(f"{self._ERR}: {ErrorMessages.CANNOT_DIV_BY_ZERO}")
                    result /= inner_alg_exp.value
            case Ad.POWER:
                result: complex = complex(1, 0)
                for inner_alg_exp in self._content[::-1]:
                    result = inner_alg_exp.value ** result
            case Ad.ROOT:
                result: complex = self._content[0].value
                for inner_alg_exp in self._content[1:]:
                    result = result ** (1 / inner_alg_exp.value)
            case _:
                cannot_compute_value: str = ErrorMessages.replace(ErrorMessages.CANNOT_COMPUTE_VALUE_UNKNOWN_OPERATOR,
                                                                  self._operator)
                raise ValueError(f"{self._ERR}{cannot_compute_value}")
        return complex(result)

    def is_natural(self) -> bool:
        if self._simplified:
            return False
        raise ValueError(f"{self._ERR}{self.__cannot_determine_domain}")

    def is_integer(self) -> bool:
        return self.is_natural()

    def is_rational(self) -> bool:
        if self.has_imag():
            if self._simplified:
                return False
            raise ValueError(f"{self._ERR}{self.__cannot_determine_domain}")
        if all((len(self._content) == 2, self._operator == Ad.DIV, isinstance(self._content[0], AtomicAlgExp),
                isinstance(self._content[1], AtomicAlgExp))):
            return True
        if self._simplified:
            return False
        raise ValueError(f"{self._ERR}{self.__cannot_determine_domain}")

    def is_real(self) -> bool:
        if self.has_imag():
            if self._simplified:
                return False
            raise ValueError(f"{self._ERR}{self.__cannot_determine_domain}")
        return True

    def is_complex(self) -> bool:
        return True  # every NumericAlgExp is a complex number

    def _alg_exp_structure(self, expression: str) -> list:
        is_not_composite: str = ErrorMessages.replace(ErrorMessages.IS_NOT_EXP, expression, CompositeAlgExp.__name__)
        split_indexes: dict = {operator: [] for operator in Ad.OPERATORS}
        expression_parts: list = []
        operator_for_split: str = ""
        bracketing: list = self._bracketing(expression)
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
                    inner_alg_exp = AlgExp.initializer(expression[start_index:actual_index], NumericAtomicAlgExp,
                                                       NumericCompositeAlgExp)
                    expression_parts.append(inner_alg_exp)
                    start_index = actual_index + 1
                break
        if operator_for_split == "":
            raise ValueError(f"{self._ERR}{is_not_composite}")
        self._operator = operator_for_split
        return expression_parts

    def _create_content_from_complex(self, expression: complex) -> None:
        self._operator = Ad.PLUS
        exp_from_real: NumericAtomicAlgExp = NumericAtomicAlgExp(expression.real)
        exp_from_imag: NumericAlgExp
        if expression.imag in (-1, 0, 1):
            exp_from_imag = NumericAtomicAlgExp(complex(0, expression.imag))
        else:
            exp_from_imag = NumericCompositeAlgExp(f"{expression.imag}{Ad.MULTIPLY}{Ad.IMAG_UNIT}")
        self._content = [exp_from_real, exp_from_imag]

    def _create_content_from_float(self, expression: float) -> None:
        self._operator = Ad.DIV
        string_expression: str = str(expression)
        numerator: int = int("".join(string_expression.split(Ad.DECIMAL_POINT)))
        denominator: int = 10 ** len(string_expression.split(Ad.DECIMAL_POINT)[1])
        frac: Fraction = Fraction(numerator, denominator)
        self._content = [NumericAtomicAlgExp(number) for number in str(frac).split("/")]

    def _create_content_from_other_instance(self, expression) -> None:
        CompositeAlgExp._create_content_from_other_instance(self, expression)

    def _create_content_from_str(self, expression: str) -> None:
        corrected_expression: str = self._correction(expression)
        if re.search(Patterns.FLOAT_NUMBER, corrected_expression):
            self._create_content_from_float(float(corrected_expression))
        else:
            self._content = self._alg_exp_structure(corrected_expression)
            self._check_content()

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        clean_expression: str
        replaced_expression: str
        if isinstance(expression, str):
            replaced_expression = expression
            for special_string in Ad.SPECIAL_NUMERIC_STRINGS:
                # imaginary unit is chosen here as a numerical representative - it has no other special meaning
                # imaginary unit is very useful here precisely because it is both a number and a letter
                # the killer bloody combinations that occur here give us only very limited options - trust me!
                # Couldn't it be done in a simpler way? NOPE.
                replaced_expression = replaced_expression.replace(special_string, Ad.IMAG_UNIT)
            clean_expression = self._remove_white_spaces(replaced_expression)
        else:
            clean_expression, replaced_expression = expression, expression
        must_be_numeric_composite: str = "Expression must be a complex number with at least one operation (see doc)"
        self._allowed_types = {}
        self._asserts = [
            (
                not isinstance(expression, str) or not re.search(Patterns.RESTRICTED_NUMERIC_COMPOSITE_CONTENT,
                                                                 expression),
                must_be_numeric_composite),
            (
                not isinstance(expression, str) or re.search(self._allowed_content_pattern, replaced_expression),
                must_be_numeric_composite),
            (
                not isinstance(expression, str) or not re.search(Patterns.INTEGER, clean_expression),
                must_be_numeric_composite)
        ]
        super()._init_check(expression)


if __name__ == '__main__':
    while True:
        alg_exp_input: str = input(": ")
        if alg_exp_input == "exit":
            break
        try:
            alg_exp: NumericCompositeAlgExp = NumericCompositeAlgExp(alg_exp_input)
            print(f"exp: {alg_exp}")
            print(f"value: {alg_exp.value}")
        except Exception as err:
            print(err)
