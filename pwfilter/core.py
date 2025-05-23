import re
import sys


def filter_passwords(
    wordlist_file,
    output_file,
    regex_patterns=None,
    dictionary_file=None,
    invert_match=False,
    ignore_case=False,
):
    """
    Filters passwords from wordlist_file based on the given criteria.
    Empty lines in the wordlist are ignored.

    Args:
        wordlist_file: An open file object for the input wordlist.
        output_file: An open file object for the output.
        regex_patterns: A list of regex pattern strings. Can be empty or None.
        dictionary_file: An open file object for the dictionary (if 'in_dictionary' preset used).
        invert_match: If True, keep passwords that *don't* meet all criteria.
        ignore_case: If True, perform case-insensitive matching for regex and dictionary.
    """
    compiled_regexes = []
    if regex_patterns:
        for pattern_str in regex_patterns:
            try:
                flags = re.IGNORECASE if ignore_case else 0
                compiled_regexes.append(re.compile(pattern_str, flags))
            except re.error as e:
                print(
                    f"Error: Invalid regex pattern '{pattern_str}': {e}",
                    file=sys.stderr,
                )
                sys.exit(1)

    dictionary_words = set()
    is_dictionary_filter_active = dictionary_file is not None

    if is_dictionary_filter_active:
        for line in dictionary_file:
            word = line.strip()
            if not word:
                continue
            if ignore_case:
                dictionary_words.add(word.lower())
            else:
                dictionary_words.add(word)
        if dictionary_file:
            dictionary_file.close()

    count_matched = 0
    count_total_processed_lines = 0
    count_valid_passwords = 0

    for raw_line in wordlist_file:
        count_total_processed_lines += 1
        password = raw_line.strip()

        if not password:
            continue

        count_valid_passwords += 1

        all_criteria_met = True

        if is_dictionary_filter_active:
            password_to_check_in_dict = password.lower() if ignore_case else password
            if password_to_check_in_dict not in dictionary_words:
                all_criteria_met = False

        if all_criteria_met and compiled_regexes:
            for comp_rx in compiled_regexes:
                if not comp_rx.search(password):
                    all_criteria_met = False
                    break

        if invert_match:
            if not all_criteria_met:
                output_file.write(password + "\n")
                count_matched += 1
        else:
            if all_criteria_met:
                output_file.write(password + "\n")
                count_matched += 1

    if wordlist_file:
        wordlist_file.close()

    if output_file is not sys.stdout:
        if output_file:
            output_file.close()
        print(
            f"Processed {count_valid_passwords} valid passwords from {count_total_processed_lines} total lines. "
            f"Filtered {count_matched} to {output_file.name}",
            file=sys.stderr,
        )
    else:
        print(
            f"Processed {count_valid_passwords} valid passwords from {count_total_processed_lines} total lines. "
            f"Matched: {count_matched}.",
            file=sys.stderr,
        )
