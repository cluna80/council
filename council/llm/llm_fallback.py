import time

from typing import List, Any

from council.llm import LLMBase, LLMMessage, LLMResult, LLMException, LLMCallException


class LLMFallback(LLMBase):
    """
    A class that combines two language models, using a fallback mechanism upon failure.

    Attributes:
        _llm (LLMBase): The primary language model instance.
        _fallback (LLMBase): The fallback language model instance.
        _retry_before_fallback (int): The number of retry attempts with the primary language model
            before switching to the fallback.

    """

    _llm: LLMBase
    _fallback: LLMBase

    def __init__(self, llm: LLMBase, fallback: LLMBase, retry_before_fallback: int = 2):
        super().__init__()
        self._llm = llm
        self._fallback = fallback
        self._retry_before_fallback = retry_before_fallback

    def _post_chat_request(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResult:
        try:
            return self._llm_call_with_retry(messages, **kwargs)
        except Exception as base_exception:
            try:
                return self._fallback.post_chat_request(messages, **kwargs)
            except Exception as e:
                raise e from base_exception

    def _llm_call_with_retry(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResult:
        retry_count = 0
        while retry_count == 0 or retry_count < self._retry_before_fallback:
            try:
                return self._llm.post_chat_request(messages, **kwargs)
            except LLMCallException as e:
                retry_count += 1
                if self._is_retryable(e.code) and retry_count < self._retry_before_fallback:
                    time.sleep(1.25**retry_count)
                else:
                    raise e
            except Exception:
                raise
        raise LLMException("Main LLM failed")

    @staticmethod
    def _is_retryable(code: int) -> bool:
        return code == 408 or code == 429 or code == 503 or code == 504
