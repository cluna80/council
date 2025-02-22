import time
import random
from typing import List, Any, Callable, Optional, Protocol

from council.agents import Agent, AgentResult
from council.contexts import AgentContext, ScoredChatMessage, SkillContext, ChatMessage
from council.llm import LLMBase, LLMMessage, LLMessageTokenCounterBase, LLMTokenLimitException, LLMResult, LLMException
from council.runners import Budget
from council.scorers import ScorerBase
from council.skills import SkillBase


class LLMMessagesToStr(Protocol):
    def __call__(self, messages: List[LLMMessage]) -> List[str]:
        ...


def llm_message_content_to_str(messages: List[LLMMessage]) -> List[str]:
    return [msg.content for msg in messages]


class MockTokenCounter(LLMessageTokenCounterBase):
    def __init__(self, limit: int = -1):
        self._limit = limit

    def count_messages_token(self, messages: List[LLMMessage]) -> int:
        result = 0
        for msg in messages:
            result += len(msg.content)

        if 0 < self._limit < result:
            raise LLMTokenLimitException(token_count=result, limit=self._limit, model="mock")
        return result


class MockSkill(SkillBase):
    def __init__(self, name: str = "mock", action: Optional[Callable[[SkillContext, Budget], ChatMessage]] = None):
        super().__init__(name)
        self._action = action if action is not None else self.empty_message

    def execute(self, context: SkillContext, budget: Budget) -> ChatMessage:
        return self._action(context, budget)

    def empty_message(self, context: SkillContext, budget: Budget):
        return self.build_success_message("")

    def set_action_custom_message(self, message: str) -> None:
        self._action = lambda context, budget: self.build_success_message(message)


class MockLLM(LLMBase):
    def __init__(self, action: Optional[LLMMessagesToStr] = None, token_limit: int = -1):
        super().__init__(token_counter=MockTokenCounter(token_limit))
        self._action = action

    def _post_chat_request(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResult:
        if self._action is not None:
            return LLMResult(choices=self._action(messages))
        return LLMResult(choices=[f"{self.__class__.__name__}"])

    @staticmethod
    def from_responses(responses: List[str]) -> "MockLLM":
        return MockLLM(action=(lambda x: responses))

    @staticmethod
    def from_response(response: str) -> "MockLLM":
        return MockLLM(action=(lambda x: [response]))

    @staticmethod
    def from_multi_line_response(responses: List[str]) -> "MockLLM":
        response = "\n".join(responses)
        return MockLLM(action=(lambda x: [response]))


class MockErrorLLM(LLMBase):
    def __init__(self, exception: LLMException = LLMException()):
        super().__init__()
        self.exception = exception

    def _post_chat_request(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResult:
        raise self.exception


class MockErrorSimilarityScorer(ScorerBase):
    def __init__(self, exception: Exception = Exception()):
        self.exception = exception

    def _score(self, message: ChatMessage) -> float:
        raise self.exception


class MockAgent(Agent):
    # noinspection PyMissingConstructor
    def __init__(
        self,
        message: str = "agent message",
        data: Any = None,
        score: float = 1.0,
        sleep: float = 0.2,
        sleep_interval: float = 0.1,
    ):
        self.message = message
        self.data = data
        self.score = score
        self.sleep = sleep
        self.sleep_interval = sleep_interval

    def execute(self, context: AgentContext, budget: Optional[Budget] = None) -> AgentResult:
        time.sleep(random.uniform(self.sleep, self.sleep + self.sleep_interval))
        return AgentResult([ScoredChatMessage(ChatMessage.agent(self.message, self.data), score=self.score)])


class MockErrorAgent(Agent):
    # noinspection PyMissingConstructor
    def __init__(self, exception: Exception = Exception()):
        self.exception = exception

    def execute(self, context: AgentContext, budget: Optional[Budget] = None) -> AgentResult:
        raise self.exception
