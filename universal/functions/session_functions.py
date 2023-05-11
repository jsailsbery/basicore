import os
import random
import logging
from typing import List

from universal.file_functions import UFile
from universal.task_functions import UTask

logger = logging.getLogger(__name__)

class USession:
    """
    Represents a collection of UTask objects that are used in a single batch processing session.
    """
    task_count_limit = 100000
    task_list_filename = "session_task_list.txt"
    done_list_filename = "session_completed.txt"

    def __init__(self, session_directory: str = "") -> None:
        """
        Initializes a new USession object with the specified directory.

        Parameters:
            session_directory (str): The directory to use for storing session files.

        Returns:
            None
        """
        self.directory = session_directory if session_directory else os.getcwd()

        # Session defined tasks
        self.task_list, self.completed, self.incomplete = [[], [], []]

        # Session Task Files
        self.task_list_file = UFile(directory=session_directory, filename=self.task_list_filename)
        self.done_list_file = UFile(directory=session_directory, filename=self.done_list_filename)

        # Load the tasks
        self.load_task_list()
        self.load_done_list()
        self.load_incomplete()

    def load_task_list(self) -> None:
        """
        Loads the task list from the task_list.txt file.

        Returns:
            None
        """
        self.task_list = []
        ufile = self.task_list_file
        if os.path.exists(ufile.filepath):
            self.task_list = [UTask(**taskdict) for taskdict in ufile.read_list_of_dicts()]

    def load_done_list(self) -> None:
        """
        Loads the list of completed tasks from the completed.txt file.

        Returns:
            None
        """
        self.completed = []
        ufile = self.done_list_file
        if os.path.exists(ufile.filepath):
            self.completed = [int(taskidstr) for taskidstr in ufile.read_list()]

    def load_incomplete(self) -> None:
        """
        Loads the list of incomplete tasks by comparing the task list and completed list.

        Returns:
            None
        """
        self.incomplete = [task for task in self.task_list if task.taskid not in self.completed]

    def save(self):
        """
        Saves the current task list to the task_list_filename
        Saves the completed task list to the done_list_filename
        """
        self.task_list_file.write_list(self.task_list)
        self.done_list_file.write_list(self.completed)

    def defined(self) -> bool:
        """
        Checks whether there are any tasks defined for this batch processing session.

        Returns:
            bool: True if there are one or more tasks defined, False otherwise.
        """
        if len(self.task_list) > 1:
            return True
        return False

    def completed(self) -> bool:
        """
        Checks whether all tasks for this batch processing session have been completed.

        Returns:
            bool: True if all tasks have been completed, False otherwise.
        """
        if self.defined() and len(self.incomplete) == 0:
            return True
        return False

    def new_taskid(self) -> str:
        """
        Generates a new unique task ID for a new UTask object.

        Returns:
            A string representing a unique task ID.
        """
        # Calculate the maximum number of digits needed for the task ID
        maxdigits: int = len(str(self.task_count_limit))

        # Get a list of existing task IDs in the task list
        taskids: List[str] = [task.taskid for task in self.task_list]

        # Generate a random task ID between 0 and the task count limit, and format it with leading zeros
        taskid: str = f"{random.randint(0, self.task_count_limit):0{maxdigits}d}"

        # Check whether the task ID is already in the taskids list
        while taskid in taskids:
            # If the task ID is not unique, generate a new one and check again
            taskid = f"{random.randint(0, self.task_count_limit):0{maxdigits}d}"

        # Return the unique task ID
        return taskid

    def add(self, task: UTask, autosave: bool = True) -> None:
        """
        Adds a new UTask object to the task list for this batch processing session.

        Args:
            task (UTask): The task to add to the task list.
            autosave (bool, optional): Whether to automatically save the task list after adding the task.
                Defaults to True.
        """
        task.taskid = self.new_taskid()
        task.completed_log = self.done_list_file

        self.task_list.append(task)
        self.incomplete.append(task)
        if autosave:
            self.save()

    def add_many(self, tasks: List[UTask]) -> None:
        """
        Adds multiple UTask objects to the task list for this batch processing session.

        Args:
            tasks (List[UTask]): The tasks to add to the task list.
        """
        for task in tasks:
            self.add(task, autosave=False)
        self.save()

    async def run_tasks(self, **kwargs) -> None:
        """
        Sends requests to the OpenAI API for all incomplete tasks in the session.

        This is a placeholder method for child classes to implement.

        Args:
            **kwargs: Additional keyword arguments that can be used by child classes to pass
                any required configuration or authentication parameters.

        Returns:
            None
        """
        self.save()
