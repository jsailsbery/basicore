import os
import stat
import json
import tempfile
from unittest.mock import patch
from universal.files import FileNode


def test_read():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, 'test_file.txt')
        expected_content = 'Test file contents'
        with open(filepath, 'w') as temp_file:
            temp_file.write(expected_content)

        file_node = FileNode(filepath)
        content = file_node.read()
        assert content == expected_content


def test_write():
    with tempfile.NamedTemporaryFile(mode='w') as temp_file:
        filepath = temp_file.name
        data = 'Test file data'

        file_node = FileNode(filepath)
        file_node.write(data)

        with open(filepath, 'r') as f:
            written_content = f.read()

        assert written_content == data


def test_write_json():
    with tempfile.NamedTemporaryFile(mode='w') as temp_file:
        filepath = temp_file.name
        data = {'key': 'value'}

        file_node = FileNode(filepath)
        file_node.write(json.dumps(data))

        with open(filepath, 'r') as f:
            written_content = f.read()

        assert written_content == '{"key": "value"}'


def test_write_append():
    with tempfile.NamedTemporaryFile(mode='w') as temp_file:
        filepath = temp_file.name
        data = 'Test file data'
        appended_data = 'Appended data'

        file_node = FileNode(filepath)
        file_node.write(data)  # Write initial data
        file_node.write(appended_data, mode='a')  # Append additional data

        with open(filepath, 'r') as f:
            written_content = f.read()

        assert written_content == 'Test file dataAppended data'


def test_write_no_write_permission():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, 'test_file.txt')
        data = 'Test file data'

        file_node = FileNode(filepath)
        with patch('os.access', return_value=False):  # Patch os.access to simulate no write permission
            try:
                file_node.write(data)
                assert False  # The write operation should raise a PermissionError
            except PermissionError:
                assert True


def test_read_nonexistent_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, 'nonexistent_file.txt')

        file_node = FileNode(filepath)
        try:
            file_node.read()
            assert False  # The read operation should raise a FileNotFoundError
        except FileNotFoundError:
            assert True