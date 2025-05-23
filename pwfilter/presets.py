SPECIAL_CHARS_REGEX = r'[!@#$%^&*()_+\-=[\]{};\':"\\|,.<>/?~`]'

PRESETS = {
    "min_length_8": {
        "id": "ml8",
        "regex": r"^.{8,}$",
        "description": "Passwords with a minimum length of 8 characters.",
    },
    "min_length_12": {
        "id": "ml12",
        "regex": r"^.{12,}$",
        "description": "Passwords with a minimum length of 12 characters.",
    },
    "has_uppercase": {
        "id": "upper",
        "regex": r"[A-Z]",
        "description": "Passwords containing at least one uppercase letter.",
    },
    "has_lowercase": {
        "id": "lower",
        "regex": r"[a-z]",
        "description": "Passwords containing at least one lowercase letter.",
    },
    "has_digit": {
        "id": "digit",
        "regex": r"[0-9]",
        "description": "Passwords containing at least one digit.",
    },
    "has_special_char": {
        "id": "special",
        "regex": SPECIAL_CHARS_REGEX,
        "description": f"Passwords containing at least one special character ({SPECIAL_CHARS_REGEX}).",
    },
    "has_consecutive_repeated_chars": {
        "id": "consec",
        "regex": r"(.)\1",
        "description": "Passwords with consecutive repeated characters (use --invert to exclude these).",
    },
    "contains_common_pattern_password": {
        "id": "cmnpwd",
        "regex": r"password",  # User should use --ignore-case for 'Password', 'PASSWORD'
        "description": "Passwords containing the substring 'password' (use --invert and --ignore-case to exclude).",
    },
    "in_dictionary": {  # This is a special preset marker
        "id": "dict",
        "regex": None,  # Handled by specific logic
        "description": "Passwords found in a provided dictionary file (use --invert to exclude, requires --dictionary-file).",
    },
    "strong_8_plus_all_types": {
        "id": "s8all",
        "regex": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*"
        + SPECIAL_CHARS_REGEX
        + r").{8,}$",
        "description": "Min 8 chars, 1 lower, 1 upper, 1 digit, 1 special.",
    },
    "strong_12_plus_all_types": {
        "id": "s12all",
        "regex": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*"
        + SPECIAL_CHARS_REGEX
        + r").{12,}$",
        "description": "Min 12 chars, 1 lower, 1 upper, 1 digit, 1 special.",
    },
    "strong_10_plus_3_of_4_types_LUD": {  # LUD = Lower, Upper, Digit
        "id": "s10lud",
        "regex": r"^(?=(?:.*[a-z]){1,})(?=(?:.*[A-Z]){1,})(?=(?:.*[0-9]){1,}).{10,}$",
        "description": "Min 10 chars, at least 1 lower, 1 upper, 1 digit.",
    },
    "only_lowercase": {
        "id": "onlylow",
        "regex": r"^[a-z]+$",
        "description": "Passwords consisting only of lowercase letters.",
    },
    "only_uppercase": {
        "id": "onlyup",
        "regex": r"^[A-Z]+$",
        "description": "Passwords consisting only of uppercase letters.",
    },
    "only_digits": {
        "id": "onlydig",
        "regex": r"^[0-9]+$",
        "description": "Passwords consisting only of digits.",
    },
    "only_alphabetic": {
        "id": "onlyalpha",
        "regex": r"^[a-zA-Z]+$",
        "description": "Passwords consisting only of alphabetic characters.",
    },
    "only_alphanumeric": {
        "id": "onlyalnum",
        "regex": r"^[a-zA-Z0-9]+$",
        "description": "Passwords consisting only of alphanumeric characters.",
    },
    "starts_with_letter": {
        "id": "startlet",
        "regex": r"^[a-zA-Z]",
        "description": "Passwords starting with an alphabetic character.",
    },
    "ends_with_digit": {
        "id": "enddig",
        "regex": r"[0-9]$",
        "description": "Passwords ending with a digit.",
    },
    "no_digits": {
        "id": "nodig",
        "regex": r"^[^0-9]*$",
        "description": "Passwords containing no digits.",
    },
    "no_letters": {
        "id": "nolet",
        "regex": r"^[^a-zA-Z]*$",
        "description": "Passwords containing no letters (alphabetic characters).",
    },
}

# Create helper maps for resolving IDs and for argparse choices
PRESET_ID_TO_NAME_MAP = {details["id"]: name for name, details in PRESETS.items()}
ALL_PRESET_CHOICES = list(PRESETS.keys()) + list(PRESET_ID_TO_NAME_MAP.keys())


def get_preset_by_name_or_id(identifier):
    """Returns the preset name if identifier is a valid name or ID."""
    if identifier in PRESETS:
        return identifier  # It's a full name
    if identifier in PRESET_ID_TO_NAME_MAP:
        return PRESET_ID_TO_NAME_MAP[identifier]  # It's an ID, return full name
    return None
