import os
import tempfile
from universal.files import DirActions

def test_exists():
    with tempfile.TemporaryDirectory() as temp_dir:
        assert DirActions.exists(temp_dir)
        assert not DirActions.exists(os.path.join(temp_dir, "non_existent"))


def test_create_delete():
    with tempfile.TemporaryDirectory() as temp_dir:
        new_dir = os.path.join(temp_dir, "new_dir")
        assert not DirActions.exists(new_dir)
        assert DirActions.create(new_dir)
        assert DirActions.exists(new_dir)
        assert DirActions.delete(new_dir)
        assert not DirActions.exists(new_dir)

def test_list():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "test_file.txt"), "w") as f:
            f.write("Hello, World!")
        dir_contents = DirActions.list(temp_dir)
        assert len(dir_contents) == 1
        assert os.path.join(temp_dir, "test_file.txt") in dir_contents.keys()

def test_copy():
    with tempfile.TemporaryDirectory() as temp_dir_source:
        with tempfile.TemporaryDirectory() as temp_dir_dest:
            with open(os.path.join(temp_dir_source, "test_file.txt"), "w") as f:
                f.write("Hello, World!")
            assert DirActions.copy(temp_dir_source, temp_dir_dest)
            assert os.path.exists(os.path.join(temp_dir_dest, "test_file.txt"))

def test_remove():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "keep.txt"), "w") as f:
            f.write("Keep me!")
        with open(os.path.join(temp_dir, "remove.txt"), "w") as f:
            f.write("Remove me!")
        assert DirActions.remove(temp_dir, ["keep.txt"])
        assert not os.path.exists(os.path.join(temp_dir, "remove.txt"))
        assert os.path.exists(os.path.join(temp_dir, "keep.txt"))
