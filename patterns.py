from algebradata import AlgebraData as Ad


class Patterns:
    # private variables
    # variables for any expressions
    __left_br, __right_br = Ad.LEFT_BRACKET, Ad.RIGHT_BRACKET
    __minus, __plus = Ad.MINUS, Ad.PLUS
    __left_part: str = rf"^\{__left_br}*[\{__minus}\{__plus}]*"
    __right_part: str = rf"\{__right_br}*$"
    __left_part_without_signs: str = rf"^\{__left_br}*"
    __wrapped_numeric_strings: str = ""
    for special_string in Ad.SPECIAL_NUMERIC_STRINGS:
        __wrapped_numeric_strings += rf"{__left_part}{special_string}{__right_part}|"
    __wrapped_numeric_strings = __wrapped_numeric_strings[:-1]
    # characters for numeric expressions
    __special_strings_divided_by_or: str = __left_br + "|".join(Ad.SPECIAL_NUMERIC_STRINGS) + __right_br
    __numeric_allowed_backslash_characters: tuple = (
        __left_br, __right_br, Ad.PLUS, Ad.MINUS, Ad.MULTIPLY, Ad.DIV, Ad.POWER, Ad.ROOT, Ad.DECIMAL_POINT)
    __numeric_allowed_other_characters: tuple = (Ad.IMAG_UNIT,)
    __numeric_allowed_characters: tuple = __numeric_allowed_backslash_characters + __numeric_allowed_other_characters
    # characters for variable expressions
    __variable_allowed_names: str = "a-zA-Z"
    __variable_allowed_backslash_characters: tuple = (
        __left_br, __right_br, Ad.LEFT_IMMUTABLE_BRACKET, Ad.RIGHT_IMMUTABLE_BRACKET, Ad.PLUS, Ad.MINUS, Ad.MULTIPLY,
        Ad.DIV, Ad.POWER, Ad.ROOT, Ad.DECIMAL_POINT)
    __variable_allowed_other_characters: tuple = (__variable_allowed_names,)
    __variable_allowed_characters: tuple = __variable_allowed_backslash_characters + __variable_allowed_other_characters

    # public variables
    FLOAT_NUMBER: str = rf"{__left_part}\d+\{Ad.DECIMAL_POINT}\d+{__right_part}"
    INTEGER: str = rf"{__left_part}\d+{__right_part}|{__left_part}{Ad.IMAG_UNIT}{__right_part}"
    SPECIAL_NUMERIC_STRING: str = __wrapped_numeric_strings
    ALLOWED_VAR_CHARS: str = __variable_allowed_names
    ALLOWED_VAR_CHARS_WITHOUT_IMAG_UNIT: str = rf"(?!{Ad.IMAG_UNIT})[{ALLOWED_VAR_CHARS}]"
    ALLOWED_NUMERIC_ATOMIC_CONTENT: str = rf"{FLOAT_NUMBER}|{INTEGER}|{SPECIAL_NUMERIC_STRING}"
    ALLOWED_NUMERIC_COMPOSITE_CONTENT: str = "^[\\" + "\\".join(__numeric_allowed_backslash_characters) + "".join(
        __numeric_allowed_other_characters) + rf"\d\s]+$"
    ALLOWED_SIMPLE_VARIABLE_ATOMIC_CONTENT: str = rf"{__left_part_without_signs}{ALLOWED_VAR_CHARS_WITHOUT_IMAG_UNIT}{__right_part}"
    ALLOWED_VARIABLE_COMPOSITE_CONTENT: str = "^[\\" + "\\".join(__variable_allowed_backslash_characters) + "".join(
        __variable_allowed_other_characters) + rf"\d\s]+$"
    RESTRICTED_NUMERIC_COMPOSITE_CONTENT: str = rf"{ALLOWED_VAR_CHARS_WITHOUT_IMAG_UNIT}{__special_strings_divided_by_or}|{__special_strings_divided_by_or}{ALLOWED_VAR_CHARS_WITHOUT_IMAG_UNIT}"
    WHITE_SPACES: str = r"\s+"
