import os
import pytest
import tempfile
from basicore.files import DirNode
from basicore.files import FileNode

def test_create():
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = os.path.join(temp_dir, "test_dir")
        dir_node = DirNode(dir_path)

        assert dir_node.exists
        assert os.path.isdir(dir_path)


def test_create_existing_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = os.path.join(temp_dir, "test_dir")
        os.mkdir(dir_path)
        dir_node = DirNode(dir_path, create_if_not_exists=False)
        assert os.path.exists(dir_path)


def test_create_not_existing_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = os.path.join(temp_dir, "test_dir")
        with pytest.raises(FileNotFoundError):
            dir_node = DirNode(dir_path, create_if_not_exists=False)


def test_delete():
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = os.path.join(temp_dir, "test_dir")
        os.mkdir(dir_path)
        dir_node = DirNode(dir_path)
        assert os.path.exists(dir_path)
        dir_node.delete()
        assert not os.path.exists(dir_path)


def test_list():
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = os.path.join(temp_dir, "test_dir")
        os.mkdir(dir_path)
        file_path = os.path.join(dir_path, "test_file.txt")
        with open(file_path, "w") as file:
            file.write("Test file content")
        dir_node = DirNode(dir_path)
        directory_contents = dir_node.list()
        assert len(directory_contents) == 1
        assert isinstance(directory_contents[0], FileNode)
        assert directory_contents[0].path == file_path


def test_copy():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir_path = os.path.join(temp_dir, "source_dir")
        os.mkdir(source_dir_path)
        file_path = os.path.join(source_dir_path, "test_file.txt")
        with open(file_path, "w") as file:
            file.write("Test file content")
        dest_dir_path = os.path.join(temp_dir, "dest_dir")
        dir_node = DirNode(source_dir_path)
        dir_node.copy(dest_dir_path)
        assert os.path.exists(dest_dir_path)
        assert os.path.isdir(dest_dir_path)
        copied_file_path = os.path.join(dest_dir_path, "test_file.txt")
        assert os.path.exists(copied_file_path)
        assert os.path.isfile(copied_file_path)


def test_remove():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir_path = os.path.join(temp_dir, "source_dir")
        os.mkdir(source_dir_path)
        file_path = os.path.join(source_dir_path, "test_file.txt")
        with open(file_path, "w") as file:
            file.write("Test file content")
        dir_node = DirNode(source_dir_path)
        dir_node.remove(["test_file.txt"])
        assert os.path.exists(source_dir_path)
        assert os.path.isdir(source_dir_path)
        assert os.path.exists(file_path)
        assert os.path.isfile(file_path)


def test_repr():
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = os.path.join(temp_dir, "test_dir")
        os.mkdir(dir_path)  # Create the directory
        dir_node = DirNode(dir_path)
        assert repr(dir_node) == f"DirInfo({dir_path})"
