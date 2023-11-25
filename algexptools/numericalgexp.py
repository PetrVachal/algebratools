from abc import ABC, abstractmethod
from typing import Any

from algexptools import AlgExp


class NumericAlgExp(AlgExp, ABC):
    """
    Abstract class for algebraic expressions that contain only specific complex numbers.
    - NumericAtomicAlgExp       numeric expression without operations
    - NumericCompositeAlgExp    numeric expression with operations
    """

    def __init__(self, expression: Any):
        super().__init__(expression)

    @abstractmethod
    def is_natural(self) -> bool:
        """
        Returns True if expression is natural.
        Otherwise, returns False.
        :return: see doc
        """
        return NotImplemented

    @abstractmethod
    def is_integer(self) -> bool:
        """
        Returns True if expression is integer.
        Otherwise, returns False.
        :return: see doc
        """
        return NotImplemented

    @abstractmethod
    def is_rational(self) -> bool:
        """
        Returns True if expression is rational.
        Otherwise, returns False.
        :return: see doc
        """
        return NotImplemented

    @abstractmethod
    def is_real(self) -> bool:
        """
        Returns True if expression is real.
        Otherwise, returns False.
        :return: see doc
        """
        return NotImplemented

    @abstractmethod
    def is_complex(self) -> bool:
        """
        Returns True if expression is complex.
        Otherwise, returns False.
        :return: see doc
        """
        return NotImplemented

    @abstractmethod
    def _create_content_from_complex(self, expression: complex):
        """
        Creates specific structure (named as content) from an expression complex.
        :param expression: any algebraic expression
        :return: None
        """
        return NotImplemented

    @abstractmethod
    def _create_content_from_float(self, expression: float):
        """
        Creates specific structure (named as content) from an expression float.
        :param expression: any algebraic expression
        :return: None
        """
        return NotImplemented

    @property
    @abstractmethod
    def value(self) -> complex:
        """
        Returns value of algebraic expression like a complex number.
        :return: see doc
        """
        return NotImplemented

    def __abs__(self):
        return abs(self.value)

    def __bool__(self):
        return bool(self.value)

    def __complex__(self):
        return self.value

    def __eq__(self, other: Any):
        if isinstance(other, (complex, float, int)):
            return self.value == other
        return self.value == other.value

    def __ne__(self, other: Any):
        return not self.__eq__(other)

    def _init_check(self, expression: Any, variables_domains: dict = None) -> None:
        new_allowed_types: dict = {complex: self._create_content_from_complex, float: self._create_content_from_float}
        self._allowed_types.update(new_allowed_types)
        super()._init_check(expression)
