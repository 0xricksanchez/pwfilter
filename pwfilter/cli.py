import argparse
import sys
from .presets import (
    PRESETS,
    ALL_PRESET_CHOICES,
    get_preset_by_name_or_id,
)
from .core import filter_passwords
from . import __version__


def list_presets_info():
    """Prints available presets with their IDs, names, and descriptions."""
    print("Available presets (--presets ID_OR_NAME ...):")
    print(f"{'ID':<8} {'Name':<30} {'Description'}")
    print(f"{'-' * 7} {'-' * 29} {'-' * 40}")
    for name, details in PRESETS.items():
        print(f"{details['id']:<8} {name:<30} {details['description']}")


def main():
    if sys.argv[1] == "--version":
        print(f"pwfilter version {__version__}")
        sys.exit(0)
    if sys.argv[1] == "--list-presets":
        list_presets_info()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Filter a wordlist based on combined presets or a custom regex.",
        epilog="Example: pwfilter rockyou.txt --presets s8all -o strong_pass.txt\n"
        "         pwfilter rockyou.txt --presets ml12 upper digit --invert-match",
    )
    parser.add_argument(
        "wordlist",
        type=argparse.FileType("r", encoding="utf-8", errors="ignore"),
        help="Path to the wordlist/password list file.",
        default="",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--presets",
        nargs="+",  # Accepts one or more arguments
        choices=ALL_PRESET_CHOICES,
        metavar="PRESET_ID_OR_NAME",
        help="One or more preset IDs or names to apply. Passwords must match ALL specified presets.",
    )
    group.add_argument(
        "--regex",
        type=str,
        help="Custom regex pattern to filter passwords. Mutually exclusive with --presets.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w", encoding="utf-8"),
        default=sys.stdout,
        help="Output file to save filtered passwords (default: stdout).",
    )
    parser.add_argument(
        "-v",
        "--invert-match",
        action="store_true",
        help="Invert the sense of matching, to select non-matching lines (like grep -v).",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Perform case-insensitive matching for regexes and dictionary checks.",
    )
    parser.add_argument(
        "--dictionary-file",
        type=argparse.FileType("r", encoding="utf-8", errors="ignore"),
        help="Path to a dictionary file (required if 'in_dictionary' or 'dict' preset is used).",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List all available presets and exit.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if args.list_presets:
        list_presets_info()
        sys.exit(0)
    if not args.wordlist:
        print("")
        sys.exit(1)

    active_regex_patterns = []
    active_dictionary_file = (
        None  # Will be args.dictionary_file if 'in_dictionary' is active
    )

    if args.presets:
        chosen_preset_full_names = []
        uses_in_dictionary_preset = False

        for preset_identifier in args.presets:
            full_name = get_preset_by_name_or_id(preset_identifier)
            if not full_name:
                # Argparse choices should prevent this, but as a safeguard:
                parser.error(f"Unknown preset identifier: {preset_identifier}")
            if full_name not in chosen_preset_full_names:  # Avoid duplicate processing
                chosen_preset_full_names.append(full_name)

            if full_name == "in_dictionary":
                uses_in_dictionary_preset = True

        if uses_in_dictionary_preset and not args.dictionary_file:
            parser.error(
                "--dictionary-file is required when using the 'in_dictionary' (or 'dict') preset."
            )

        if uses_in_dictionary_preset:
            active_dictionary_file = args.dictionary_file
        elif (
            args.dictionary_file
        ):  # Dictionary file provided but 'in_dictionary' not selected
            print(
                "Warning: --dictionary-file is provided but 'in_dictionary' (or 'dict') preset is not selected. The dictionary file will be ignored.",
                file=sys.stderr,
            )

        for full_name in chosen_preset_full_names:
            preset_obj = PRESETS[full_name]
            if preset_obj[
                "regex"
            ]:  # Add regex if it's not None (i.e., not 'in_dictionary')
                active_regex_patterns.append(preset_obj["regex"])

        if not active_regex_patterns and not uses_in_dictionary_preset:
            # This case should ideally not happen if presets are defined correctly
            # (e.g. if 'in_dictionary' was the only one selected, regex_patterns would be empty but dict_file would be active)
            print(
                "Warning: No effective filter criteria selected from presets.",
                file=sys.stderr,
            )

    elif args.regex:  # Custom regex mode
        active_regex_patterns.append(args.regex)
        if args.dictionary_file:
            print(
                "Warning: --dictionary-file is ignored when using custom --regex.",
                file=sys.stderr,
            )

    if not active_regex_patterns and not active_dictionary_file:
        parser.error("No filtering criteria specified. Use --presets or --regex.")

    filter_passwords(
        wordlist_file=args.wordlist,
        output_file=args.output,
        regex_patterns=active_regex_patterns,  # Pass list of patterns
        dictionary_file=active_dictionary_file,  # Pass dictionary file if 'in_dictionary' active
        invert_match=args.invert_match,
        ignore_case=args.ignore_case,
    )


if __name__ == "__main__":
    main()
