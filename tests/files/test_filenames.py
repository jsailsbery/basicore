import os
import tempfile
from unittest.mock import patch
from basicore.files import Filenames


def test_append():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, 'test_file.txt')
        expected_filepath = os.path.join(temp_dir, 'test_file_appended.txt')
        with open(filepath, 'w') as temp_file:
            temp_file.write('Test file contents')

        appended_filepath = Filenames.append(filepath, 'appended')
        assert appended_filepath == expected_filepath


def test_prepend():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, 'test_file.txt')
        expected_filepath = os.path.join(temp_dir, 'prepended_test_file.txt')
        with open(filepath, 'w') as temp_file:
            temp_file.write('Test file contents')

        prepended_filepath = Filenames.prepend(filepath, 'prepended')
        assert prepended_filepath == expected_filepath


def test_enumerate():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, 'test_file.txt')
        expected_filepath = os.path.join(temp_dir, 'test_file_001.txt')
        with open(filepath, 'w') as temp_file:
            temp_file.write('Test file contents')

        enumerated_filepath = Filenames.enumerate(filepath, 1)
        assert enumerated_filepath == expected_filepath


def test_unique():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, 'test_file.txt')
        expected_filepath = os.path.join(temp_dir, 'test_file_001.txt')
        with open(filepath, 'w') as temp_file:
            temp_file.write('Test file contents')

        with patch('os.path.exists') as mock_exists:
            # Return True on first call, then False on subsequent calls
            mock_exists.side_effect = [True, False]

            unique_filepath = Filenames.unique(filepath)
            assert unique_filepath == expected_filepath