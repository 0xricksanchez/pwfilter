# pwfilter 🛡️

`pwfilter` is a versatile command-line tool written in Python for filtering wordlists and password lists based on various criteria. It allows you to apply predefined password policies (presets) or custom regular expressions to identify passwords that meet specific requirements. This tool is invaluable for password security analysis, penetration testing, CTF challenges, and preparing targeted wordlists.

Managed with `uv`, `pwfilter` is designed to be fast, efficient, and easy to use.

## Features

- **Preset-Based Filtering**: Apply common password policy checks using short, memorable preset IDs or full names (e.g., minimum length, character type inclusion).
- **Custom Regex Filtering**: Define your own complex password patterns using regular expressions.
- **Combine Filters**: Apply multiple presets simultaneously; passwords must satisfy ALL specified criteria.
- **Dictionary Exclusion/Inclusion**: Filter passwords against a separate dictionary file (e.g., to exclude common words or find words _in_ the dictionary).
- **Case-Insensitive Matching**: Option to ignore case for regex and dictionary checks.
- **Invert Matching**: Select passwords that _do not_ match the specified criteria (similar to `grep -v`).
- **Efficient Processing**: Designed to handle large wordlists.
- **Standard I/O**: Reads from files and can output to `stdout` (for piping) or a specified file.
- **Informative Output**: Provides counts of processed and matched passwords.
- **Easy Management**: Utilizes `uv` for environment and dependency management.

## Installation

`pwfilter` is managed using `uv`.

1.  **Clone the repository (if you haven't already):**

    ```bash
    git clone https://github.com/0xricksanchez/pwfilter
    cd pwfilter
    ```

2.  **Create and activate a virtual environment using `uv`:**

    ```bash
    uv venv .venv
    source .venv/bin/activate  # On Linux/macOS
    # .\.venv\Scripts\activate # On Windows (PowerShell/cmd)
    ```

3.  **Install `pwfilter` in editable mode:**
    This makes the `pwfilter` command available in your activated virtual environment.
    ```bash
    uv pip install -e .
    ```

## Usage

The basic command structure is:

```bash
pwfilter [WORDLIST_FILE] --presets [PRESET1] [PRESET2...] [OPTIONS]
pwfilter [WORDLIST_FILE] --regex [REGEX_PATTERN] [OPTIONS]
```

### Available Presets

Run `pwfilter --list-presets` to see the most current list directly from the tool. Common presets include:

- Length: min_length_8 (ml8), min_length_12 (ml12)
- Character Types: has_uppercase (upper), has_lowercase (lower), has_digit (digit), has_special_char (special)
- Patterns: has_consecutive_repeated_chars (consec), contains_common_pattern_password (cmnpwd)
- Dictionary: in_dictionary (dict) - requires --dictionary-file
- Strong Password Combinations: strong_8_plus_all_types (s8all), strong_12_plus_all_types (s12all)
- Exclusivity: only_lowercase (onlylow), only_digits (onlydig), no_digits (nodig)
- ...and more!

### Wordlist Format

`pwfilter` expects one password per line in the input wordlist.
Empty lines (lines containing only whitespace) are automatically skipped.
Lines starting with any character, including #, are treated as potential passwords.

## Contributing

Contributions are welcome! If you have ideas for new presets, features, or improvements, please feel free to open an issue or submit a pull request.

- Fork the repository.
- Create your feature branch (git checkout -b feature/AmazingFeature).
- Commit your changes (git commit -m 'Add some AmazingFeature').
- Push to the branch (git push origin feature/AmazingFeature).
- Open a Pull Request.
