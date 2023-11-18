class AlgebraData:
    """
    Data for work with algebra.
    Contains strings for:
    number system domains, interval and set brackets, operators
    """
    # common brackets
    LEFT_BRACKET: str = "("
    RIGHT_BRACKET: str = ")"
    # interval brackets
    LEFT_INTERVAL_OPEN: str = "("
    RIGHT_INTERVAL_OPEN: str = ")"
    LEFT_INTERVAL_CLOSED: str = "["
    RIGHT_INTERVAL_CLOSED: str = "]"
    INTERVAL_SEPARATOR: str = ","
    # set brackets
    LEFT_SET_BRACKET: str = "{"
    RIGHT_SET_BRACKET: str = "}"
    SET_SEPARATOR: str = ";"
    # AlgExp operators
    PLUS: str = "+"
    MINUS: str = "-"
    MULTIPLY: str = "*"
    DIV: str = "/"
    POWER: str = "^"
    ROOT: str = "§"
    # AlgSet operators
    UNION: str = "U"
    # decimal point
    DECIMAL_POINT: str = "."
    # characters for immutable content
    SUBSTITUTION_CHARACTER: str = "#"
    LEFT_IMMUTABLE_BRACKET: str = "{"
    RIGHT_IMMUTABLE_BRACKET: str = "}"
    # operators in tuple
    OPERATORS: tuple = (
        PLUS, MINUS, MULTIPLY, DIV, POWER, ROOT)  # depends on the order! (from the lowest priority to highest)
    # special characters
    IMAG_UNIT: str = "i"
    IMAG_UNIT_BUILT_IN: str = "j"
    # special numeric strings
    SPECIAL_NUMERIC_STRINGS: tuple = ("inf", "nan")
