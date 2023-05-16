import re


def first_word(line: str) -> str:
    """Return the first non-space word in a string.

    Args:
        line (str): An str to extract the first word from.

    Returns:
        str: The first word in the string, after removing leading whitespace and replacing non-word characters with spaces.

    Example:
        > first_word("  Hello, world!")
        > 'Hello'
    """
    if line.strip():
        return line.lstrip().split()[0]
    return ""


def first_line(lines: str) -> str:
    """Return the first line up to <newline> '\n'

    Args:
        lines (str): An str to extract the first line from.

    Returns:
        str: the first line up to <newline>

    Example:
        > first_line("Hello\nworld!")
        > 'Hello'
    """
    if lines is not None:
        return lines.splitlines()[0]
    return ""


def last_line(lines: str) -> str:
    """Return the last line after <newline> '\n'

    Args:
        lines (str): An str to extract the last line from.

    Returns:
        str: the last line after <newline>

    Example:
        > first_line("Hello\nworld!")
        > 'Hello'
    """
    if lines is not None:
        return lines.splitlines()[-1]
    return ""


def first_char(line: str) -> str:
    """Return the first non-space char in a string.

    Args:
        line (str): An str to extract the first char from.

    Returns:
        str: The first char in the string, after removing leading whitespace and replacing non-word characters with spaces.

    Example:
        > str_first_char("  Hello, world!")
        > 'H'
    """
    word = first_word(line)
    return word[0] if len(word)>0 else ""


def replace_with_spaces(match: re.Match) -> str:
    """Replace a regex match with a string of spaces.

    Args:
        match (re.Match): A regex match object.

    Returns:
        str: A string of spaces with the same length as the matched string.

    Raises:
        TypeError: If the argument is not a regex match object.

    Example:
        > import re
        > match = re.search(r'\d+', 'abc123def')
        > replace_with_spaces(match)
        > '   '
    """
    if not isinstance(match, re.Match):
        raise TypeError('Argument must be a regex match object')
    return ' ' * len(match.group(0))


def count_lspaces(text: str) -> int:
    """
    Count the number of leading spaces in a string.

    Args:
        text (str): The text to count spaces in.

    Returns:
        int: The number of leading spaces in the text.
    """
    tlst = [j for j,t in enumerate(text) if t != " " and t != "\t"]
    return tlst[0] if len(tlst) > 0 else 0


def escape_regex_special_chars(text: str) -> str:
    """
    Escapes all regular expression special characters in a given string.

    Args:
        text (str): The input string to modify.

    Returns:
        str: The modified string with all regular expression special characters escaped.
    """
    # Regular expression special characters
    special_chars = [".", "^", "$", "*", "+", "?", "{", "}", "[", "]", "\\", "|", "(", ")", ":"]

    # Add "\\" in front of any special character
    return "".join(f"\\{char}" if char in special_chars else char for char in text)


def rremove(text: str, char: str = "#") -> str:
    """
    Removes all characters from a given string, including and after the first occurrence of a specified character.

    Args:
        text (str): The input string to modify.
        char (str): The character to search for. All characters including and after the first occurrence of this
            character will be removed. The default value is "#".

    Returns:
        str: The modified string with all characters including and after the first occurrence of the specified
            character removed.
    """
    regex = f"{escape_regex_special_chars(char)}.*"
    if char in text:
        return re.sub(regex, "", text)
    return text


def lremove(text: str, char: str = "#") -> str:
    """
    Removes all characters from a given string, including and before the last occurrence of a specified character.

    Args:
        text (str): The input string to modify.
        char (str): The character to search for. All characters including and before the last occurrence of this
            character will be removed. The default value is "#".

    Returns:
        str: The modified string with all characters including and before the last occurrence of the specified
            character removed.
    """
    regex = f".*{char}"
    text = re.sub(regex, "", text)
    return text


def replace_last(s: str, old: str, new: str) -> str:
    """
    Replace the last occurrence of a substring in a given string.

    Args:
        s (str): The input string to search and replace in.
        old (str): The substring to search for and replace.
        new (str): The replacement string to use for the last occurrence of the old substring.

    Returns:
        str: The modified string with the last occurrence of the old substring replaced by the new substring.
    """
    index = s.rfind(old)
    if index == -1:
        return s  # If the substring is not found, return the original string
    return s[:index] + new + s[index + len(old):]
