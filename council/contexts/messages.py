from enum import Enum
from typing import Any


class ChatMessageKind(str, Enum):
    """
    Enum representing the kinds or categories of chat messages within a chat system or application.
    """

    User = "USER"
    """
    Represents a chat message from the user.
    """

    Agent = "AGENT"
    """
    Represents a chat message from the agent or customer support representative.
    """

    Chain = "CHAIN"
    """
    Represents a chat message from a chain
    """

    Skill = "SKILL"
    """
    Represents a chat message generated by a specific skill or functionality within the chat system.
    """

    def __str__(self):
        return f"{self.value}"


class ChatMessage:
    """
    Represents a chat message.
    """

    _message: str
    _kind: ChatMessageKind
    _data: Any
    _is_error: bool
    _source: str

    def __init__(self, message: str, kind: ChatMessageKind, data: Any = None, source: str = "", is_error: bool = False):
        """
        Initialize a new instance

        Parameters:
            message(str): the message content as readable text
            kind(ChatMessageKind): the kind of message
            data(Any): structured data associated with the message, if any
            source(str): the source of the message, when it is generated by Council
            is_error(bool): is the message considered an error
        """
        self._message = message
        self._kind = kind
        self._data = data
        self._source = source
        self._is_error = is_error

    @staticmethod
    def agent(message: str, data: Any = None, source: str = "", is_error: bool = False) -> "ChatMessage":
        """
        Helper function to create message of kind :attr:`ChatMessageKind.Agent`.
          See :meth:`ChatMessage.__init__` for details
        """
        return ChatMessage(message, ChatMessageKind.Agent, data, source, is_error)

    @staticmethod
    def user(message: str, data: Any = None, source: str = "", is_error: bool = False) -> "ChatMessage":
        """
        Helper function to create message of kind :attr:`ChatMessageKind.User`.
          See :meth:`ChatMessage.__init__` for details
        """
        return ChatMessage(message, ChatMessageKind.User, data, source, is_error)

    @staticmethod
    def skill(message: str, data: Any = None, source: str = "", is_error: bool = False) -> "ChatMessage":
        """
        Helper function to create message of kind :attr:`ChatMessageKind.Skill`.
          See :meth:`ChatMessage.__init__` for details
        """
        return ChatMessage(message, ChatMessageKind.Skill, data, source, is_error)

    @staticmethod
    def chain(message: str, data: Any = None, source: str = "", is_error: bool = False) -> "ChatMessage":
        """
        Helper function to create message of kind :attr:`ChatMessageKind.Chain`.
          See :meth:`ChatMessage.__init__` for details
        """
        return ChatMessage(message, ChatMessageKind.Chain, data, source, is_error)

    @property
    def message(self) -> str:
        """
        The readable text message

        Returns:
            str:
        """
        return self._message

    @property
    def kind(self) -> ChatMessageKind:
        """
        The kind of message

        Returns:
            ChatMessageKind:
        """
        return self._kind

    @property
    def is_kind_skill(self) -> bool:
        """
        `True` if the kind is :attr:`ChatMessageKind.Skill`, otherwise `False`

        Returns:
            bool:
        """
        return self._kind == ChatMessageKind.Skill

    @property
    def is_kind_agent(self) -> bool:
        """
        `True` if the kind is :attr:`ChatMessageKind.Agent`, otherwise `False`

        Returns:
            bool:
        """
        return self._kind == ChatMessageKind.Agent

    @property
    def is_kind_chain(self) -> bool:
        """
        `True` if the kind is :attr:`ChatMessageKind.Chain`, otherwise `False`

        Returns:
            bool:
        """
        return self._kind == ChatMessageKind.Chain

    @property
    def is_kind_user(self) -> bool:
        """
        `True` if the kind is :attr:`ChatMessageKind.User`, otherwise `False`

        Returns:
            bool:
        """
        return self._kind == ChatMessageKind.User

    @property
    def data(self) -> Any:
        """
        Returns the data, if any, associated with the message.

        Returns:
            Any:
        """
        return self._data

    @property
    def source(self) -> str:
        """
        Returns the source of the message

        Returns:
            str:
        """
        return self._source

    @property
    def is_ok(self) -> bool:
        """
        Returns `True` if the message is ok (not an error), `False` otherwise

        Returns:
            bool:
        """
        return not self._is_error

    @property
    def is_error(self) -> bool:
        """
        Returns `True` if the message is an error, `False` otherwise

        Returns:
            bool:
        """
        return self._is_error

    def is_of_kind(self, kind: ChatMessageKind) -> bool:
        """
        Returns `True` if the message is of the given kind, otherwise `False`

        Returns:
            bool:
        """
        return self._kind == kind

    def is_from_source(self, source: str) -> bool:
        """
        Returns `True` if the message is of the given source, otherwise `False`

        Args:
            source:

        Returns:

        """
        return self._source == source

    def __str__(self):
        max_length = 50
        message = self.message[:max_length] + "..." if len(self.message) > max_length else self.message
        return f"Message of kind {self.kind}: {message}"


class ScoredChatMessage:
    """
    an :class:`ChatMessage` with a scored, as returned by an :class:`~.EvaluatorBase`

    Attributes:
        message (ChatMessage): an agent message
        score: a score reflecting the quality of the message
    """

    message: ChatMessage
    score: float

    def __init__(self, message: ChatMessage, score: float):
        self.message = message
        self.score = score

    def __gt__(self, other: "ScoredChatMessage"):
        return self.score > other.score

    def __lt__(self, other: "ScoredChatMessage"):
        return self.score < other.score

    def __ge__(self, other: "ScoredChatMessage"):
        return self.score >= other.score

    def __le__(self, other: "ScoredChatMessage"):
        return self.score <= other.score

    def __str__(self):
        return f"{self.score}"
