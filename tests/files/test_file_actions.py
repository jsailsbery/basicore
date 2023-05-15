import os
import tempfile
from unittest import mock
from universal.files import FileActions


def test_exists():
    with tempfile.NamedTemporaryFile() as temp_file:
        filepath = temp_file.name
        assert FileActions.exists(filepath)


def test_remove():
    with tempfile.NamedTemporaryFile() as temp_file:
        filepath = temp_file.name
        assert os.path.exists(filepath)
        temp_file.close()  # Close the temporary file
        FileActions.remove(filepath)
        assert not os.path.exists(filepath)


def test_read():
    data = ['line 1', 'line 2', 'line 3']
    with tempfile.NamedTemporaryFile(mode='w') as temp_file:
        filepath = temp_file.name
        temp_file.write('\n'.join(data))
        temp_file.flush()

        result = FileActions.read(filepath)
        assert result == "line 1\nline 2\nline 3"


def test_write():
    data = ['line 1', 'line 2', 'line 3']
    with tempfile.NamedTemporaryFile(mode='r') as temp_file:
        filepath = temp_file.name

        FileActions.write(filepath, data)
        result = FileActions.read(filepath)
        assert result == data


def test_write_json():
    data = {'key': 'value'}
    with tempfile.NamedTemporaryFile(mode='r') as temp_file:
        filepath = temp_file.name

        FileActions.write(filepath, data)
        result = FileActions.read(filepath)
        assert result == data


def test_follow_symlink():
    with tempfile.TemporaryDirectory() as temp_dir:
        target_filepath = os.path.join(temp_dir, 'target.txt')
        symlink_filepath = os.path.join(temp_dir, 'symlink.txt')

        with open(target_filepath, 'w') as target_file:
            target_file.write('Hello, world!')

        os.symlink(target_filepath, symlink_filepath)

        result = FileActions.follow_symlink(symlink_filepath)
        assert result == os.path.abspath(target_filepath)


def test_follow_symlink_nonexistent_symlink():
    with tempfile.TemporaryDirectory() as temp_dir:
        symlink_filepath = os.path.join(temp_dir, 'symlink.txt')

        with mock.patch('os.path.exists', return_value=False):
            try:
                FileActions.follow_symlink(symlink_filepath)
            except FileNotFoundError as e:
                assert str(e) == f"Symlink does not exist: {symlink_filepath}"


def test_follow_symlink_not_symlink():
    with tempfile.NamedTemporaryFile() as temp_file:
        filepath = temp_file.name

        with mock.patch('os.path.islink', return_value=False):
            try:
                FileActions.follow_symlink(filepath)
            except ValueError as e:
                assert str(e) == f"The provided path {filepath} is not a symlink."


def test_follow_symlink_broken_symlink():
    with tempfile.TemporaryDirectory() as temp_dir:
        target_filepath = os.path.join(temp_dir, 'target.txt')
        symlink_filepath = os.path.join(temp_dir, 'symlink.txt')

        # Create broken symlink
        os.symlink('/path/to/nonexistent/file.txt', symlink_filepath)

        with mock.patch('os.path.exists', return_value=True):
            result = FileActions.follow_symlink(symlink_filepath)
            assert result == ''


def test_follow_symlink_broken_symlink():
    with tempfile.TemporaryDirectory() as temp_dir:
        target_filepath = os.path.join(temp_dir, 'target.txt')
        symlink_filepath = os.path.join(temp_dir, 'symlink.txt')

        # Create broken symlink
        os.symlink('/path/to/nonexistent/file.txt', symlink_filepath)

        with mock.patch('os.path.exists', return_value=True):
            result = FileActions.follow_symlink(symlink_filepath)
            assert result == '/path/to/nonexistent/file.txt'
