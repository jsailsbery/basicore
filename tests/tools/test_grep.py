import os
import tempfile
import pytest
from basicore.tools import Grep

@pytest.fixture(scope='module')
def test_files():
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = os.path.join(temp_dir, 'file1.txt')
        file2 = os.path.join(temp_dir, 'file2.txt')
        file3 = os.path.join(temp_dir, 'file3.txt')

        # Write some content to the files
        with open(file1, 'w') as f:
            f.write('Hello, World!\nThis is a test file.\n')

        with open(file2, 'w') as f:
            f.write('Testing Grep class\nSearching for patterns\n')

        with open(file3, 'w') as f:
            f.write('This file does not contain the pattern.\n')

        yield [file1, file2, file3]

def test_search_files(test_files):
    # Test search_files method
    directory = os.path.dirname(test_files[0])
    pattern = '*.txt'

    result = list(Grep.search_files(directory, pattern))
    assert len(result) == 3
    assert test_files[0] in result
    assert test_files[1] in result
    assert test_files[2] in result

def test_grep(test_files, caplog):
    # Test grep method
    pattern = 'test'
    files = iter(test_files)

    with caplog.at_level('INFO'):
        lines = Grep.grep(pattern, files)

        assert len(lines) == 2
        assert 'file1.txt:2:This is a test file.' in lines[0]
        assert 'file2.txt:1:Testing Grep class' in lines[1]

def test_grep_all_files(test_files, caplog):
    # Test grep_all_files method
    pattern = 'test'
    directory = os.path.dirname(test_files[0])

    with caplog.at_level('INFO'):
        lines = Grep.grep_all_files(pattern, directory)
        assert len(lines) == 2

        assert 'file1.txt:2:This is a test file.' in lines[0]
        assert 'file2.txt:1:Testing Grep class' in lines[1]
