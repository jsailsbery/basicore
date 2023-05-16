from typing import List


def remove_empty_lines(lines: List[str]) -> List[str]:
    """Remove empty lines from a list of strings.

    Args:
        lines (List[str]): A list of strings.

    Returns:
        List[str]: A new list of strings with empty lines removed.

    Example:
        > lines = ['hello\n', '\n', 'world\n']
        > remove_empty_lines(lines)
        ['hello\n', 'world\n']
    """
    return [line for line in lines if line.strip()]


def strip_lines(lines: List[str], lstrip: bool = True, rstrip: bool = True) -> List[str]:
    """
    Removes leading and/or trailing whitespace from each line in a list of strings.

    Args:
        lines (List[str]): A list of strings to strip.
        lstrip (bool): Whether to remove leading whitespace. The default is True.
        rstrip (bool): Whether to remove trailing whitespace. The default is True.

    Returns:
        List[str]: A list of strings with leading and/or trailing whitespace removed.
    """
    lines = remove_empty_lines(lines)
    if lstrip and rstrip:
        return [line.strip() for line in lines]
    elif lstrip:
        return [line.lstrip() for line in lines]
    else:
        return [line.rstrip() for line in lines]


def separate_lines_in_mixed_list(lines: List[str]) -> List[str]:
    """Separate lines in a mixed list of strings.

    This function takes a list of strings that may contain empty lines and combines all non-empty
    lines into a single string separated by newline characters. The resulting string is then split
    on all newline characters to create a list of strings with one line per item.

    Args:
        lines (List[str]): A list of strings to process.

    Returns:
        List[str]: A new list of strings with one line per item.

    Example:
        > lines = ['hello\n', '\n', 'world\n']
        > separate_lines_in_mixed_list(lines)
        > ['hello', 'world']
    """
    result = remove_empty_lines(lines)
    result_str = "\n".join(result)
    return result_str.splitlines()


def window(lines: List[str], window_size: int = 1, step: int = 1) -> List[str]:
    """
    Returns a list of concatenated strings of `window_size` lines each from `lines`
    with a step of `step` lines between each window. If the lines do not evenly
    divide into windows, the remaining lines are concatenated into an additional
    window.

    Args:
    - lines (List[str]): A list of strings representing the lines to be split into windows.
    - window_size (int): An integer representing the number of lines in each window.
        Default value is 1.
    - step (int): An integer representing the number of lines to skip between windows.
        Default value is 1.

    Returns:
    - windowed_lines (List[str]): A list of concatenated strings of `window_size` lines each
        with a step of `step` lines between each window.
    """
    windowed_lines = []

    # Define the start and end indices of each window
    window_start, window_end = [0, window_size]

    # Loop through the lines and create windows
    while window_end <= len(lines):
        # Create a window of lines
        window_subset = lines[window_start:window_end]

        # Concatenate the lines into a single string and add it to the list
        windowed_lines.append('\n'.join(window_subset))

        # Update the start and end indices for the next window
        window_start += step
        window_end += step

    # Yield the remaining lines if any
    if window_start < len(lines):
        remaining_subset = lines[window_start:]
        windowed_lines.append('\n'.join(remaining_subset))

    # Return the list of concatenated strings representing the windows
    return windowed_lines
