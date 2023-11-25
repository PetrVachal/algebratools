from algebradata import AlgebraData as Ad


class ErrorMessages:
    __sub_chr: str = Ad.SUBSTITUTION_CHARACTER
    AT_LEAST_TWO_SETS_FOR_INTERSECTION: str = "At least two sets must be entered to find their intersection"
    AT_LEAST_TWO_SETS_FOR_UNION: str = "At least two sets must be entered to find their union"
    AT_LEAST_TWO_SETS_IN_UNION: str = "Number of sets in UnionAlgSet must be at least 2"
    CANNOT_COMPUTE_VALUE_UNKNOWN_OPERATOR: str = f"Cannot compute value with unknown '{__sub_chr}1' operator"
    CANNOT_DETERMINE_DOMAIN: str = f"Cannot determine number system domain for expression '{__sub_chr}1'"
    CANNOT_DIV_BY_ZERO: str = "Cannot be divided by zero"
    CANNOT_IMAG_IN_INTERVAL: str = "Interval must not contain any complex numbers with a non-zero imaginary unit"
    CANNOT_NAN_IN_INTERVAL: str = "Interval must not contain nan"
    WRONG_NUMBERS_ORDERING_INTERVAL: str = f"Ordering of the numbers does not follow the interval rules in interval {__sub_chr}1"
    EXP_NOT_IN_SET: str = f"Expression '{__sub_chr}1' is not in set {__sub_chr}2"
    INTERSECTION_NOT_RECOGNIZED: str = f"Intersection of intervals {__sub_chr}1 and {__sub_chr}2 not recognized"
    INTERVAL_MUST_BE_CLOSED: str = f"Interval {__sub_chr}1 must be closed"
    IS_NOT_EXP: str = f"Expression '{__sub_chr}1' is not in the correct form for {__sub_chr}2"
    LEN_INTERVAL_MUST_BE_2: str = "Length of interval must be 2"
    MUST_BE_ATOMIC_VARIABLE: str = "Expression must be a variable without any operations and signs (see doc)"
    MUST_BE_INSTANCE: str = f"{__sub_chr}1 must be instance of {__sub_chr}2"
    MUST_BE_INTEGER: str = "Number for substitution must be an integer"
    MUST_CONTAIN_VARIABLE: str = "VariableComposite expression must contain any variable"
    NUMBER_IS_NOT_IN_VARIABLE_DOMAIN: str = f"Number {__sub_chr}1 is not in variable domain {__sub_chr}2 of expression '{__sub_chr}3'"
    TYPE_FOR_ITEM_IN_CONTAINS: str = "item must be instance of int or str"
    UNION_MUST_CONTAIN_INTERVAL: str = "UnionAlgSet must contain any interval"
    VAR_HAS_EMPTY_SET_DOMAIN: str = f"Domain of a variable '{__sub_chr}1' is an empty set"

    @staticmethod
    def replace(message: str, *args) -> str:
        sub: str = ErrorMessages.__sub_chr
        replaced_string: str = message
        for i, string_to_replace in enumerate(args):
            replaced_string = replaced_string.replace(f"{sub}{i + 1}", str(string_to_replace))
        return replaced_string
    