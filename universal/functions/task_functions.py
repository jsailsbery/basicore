import json
import aiohttp
import logging
from universal import UFile

logger = logging.getLogger(__name__)


class UTask:
    """
    A class representing a task to be completed by a worker.

    Attributes:
        taskid (int): The ID of the task.
    """
    taskid: int = 0
    completed: bool = False
    completed_log: UFile = None

    def __init__(self, **kwargs):
        """
        Initializes a new UTask object.

        Args:
            **kwargs: Arbitrary keyword arguments to set as attributes of the UTask object.
        """
        self.__dict__.update(kwargs)

    def __str__(self) -> str:
        """
        Returns a JSON string representation of the UTask object.

        Returns:
            str: The JSON string representation of the UTask object.
        """
        return str(self.__dict__)


class APITask(UTask):
    """
    A class representing an API task that inherits from the UTask class.

    Attributes:
        api_url (str): The URL of the API endpoint.
        request (dict): The request payload for the API.
        response (dict): The response payload from the API.
    """
    api_url: str = ""
    request: dict = {}
    response: dict = {}
    request_content: str = ""
    response_content: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def send_request(self, auth: aiohttp.BasicAuth) -> None:
        """
        Sends an asynchronous request to the OpenAI API with the given authentication credentials.
        Logs the request and response.

        Args:
            auth (aiohttp.BasicAuth): The authentication credentials for the API request.

        Raises:
            aiohttp.ClientConnectionError: Raised if there is a problem establishing a connection to the server.
            aiohttp.ClientResponseError: Raised if there is a problem with the response from the server, such as an invalid status code.
            aiohttp.ClientPayloadError: Raised if there is an issue with the payload, such as malformed data or encoding issues.
            aiohttp.ClientTimeoutError: Raised if the request times out.
            json.JSONDecodeError: Raised if there is an error decoding the JSON data in the response.

        Returns:
            None
        """
        headers = {"Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession(auth=auth, headers=headers) as session:

                logging.info(f"request: {self.request}")
                async with session.post(
                        self.api_url,
                        json=self.request,
                ) as response:

                    self.response = await response.json()
                    logging.info(f"response: {self.response}")

        except aiohttp.ClientConnectionError as e:
            logging.error(f"Connection error occurred: {e}")
            raise
        except aiohttp.ClientResponseError as e:
            logging.error(f"Response error occurred: {e}")
            raise
        except aiohttp.ClientPayloadError as e:
            logging.error(f"Payload error occurred: {e}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON data: {e}")
            raise
