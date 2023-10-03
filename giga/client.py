from pathlib import Path
from typing import Dict, Generator, List

from langchain.chat_models import GigaChat
from langchain.schema import HumanMessage, AIMessage

from .cache import Cache
from .config import cfg

CACHE_LENGTH = int(cfg.get("CACHE_LENGTH"))
CACHE_PATH = Path(cfg.get("CACHE_PATH"))
REQUEST_TIMEOUT = int(cfg.get("REQUEST_TIMEOUT"))
DISABLE_STREAMING = str(cfg.get("DISABLE_STREAMING"))
DEFAULT_MODEL = str(cfg.get("DEFAULT_MODEL"))


class GigaChatClient:
    cache = Cache(CACHE_LENGTH, CACHE_PATH)

    def __init__(self, api_host: str, username: str, password: str) -> None:
        self.api_host = api_host
        self.giga = GigaChat(
            user=username,
            password=password,
            verify_ssl=False,
            oauth_verify_ssl=False,
            api_base_url=api_host,
            model=DEFAULT_MODEL,
        )

    @cache
    def _request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        top_probability: float = 1,
    ) -> Generator[str, None, None]:
        """
        Make request to OpenAI API, read more:
        https://platform.openai.com/docs/api-reference/chat

        :param messages: List of messages {"role": user or assistant, "content": message_string}
        :param temperature: Float in 0.0 - 2.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :return: Response body JSON.
        """
        stream = DISABLE_STREAMING == "false"
        giga_messages = []
        for m in messages:
            if m["role"] == "user":
                giga_messages.append(HumanMessage(content=m["content"]))
            if m["role"] == "assistant":
                giga_messages.append(AIMessage(content=m["content"]))
        res = self.giga(giga_messages).content
        if res.startswith("`") and res.endswith("`"):
            res = res[1:-1]
        if not stream:
            yield str(res)
            return
        else:
            yield str(res)
            return

        # endpoint = f"{self.api_host}/v1/chat/completions"
        # response = requests.post(
        #     endpoint,
        #     # Hide API key from Rich traceback.
        #     headers={
        #         "Content-Type": "application/json",
        #         "Authorization": f"Bearer {self.__api_key}",
        #     },
        #     json=data,
        #     timeout=REQUEST_TIMEOUT,
        #     stream=stream,
        # )
        # response.raise_for_status()
        # # TODO: Optimise.
        # # https://github.com/openai/openai-python/blob/237448dc072a2c062698da3f9f512fae38300c1c/openai/api_requestor.py#L98
        # if not stream:
        #     data = response.json()
        #     yield data["choices"][0]["message"]["content"]  # type: ignore
        #     return
        # for line in response.iter_lines():
        #     data = line.lstrip(b"data: ").decode("utf-8")
        #     if data == "[DONE]":  # type: ignore
        #         break
        #     if not data:
        #         continue
        #     data = json.loads(data)  # type: ignore
        #     delta = data["choices"][0]["delta"]  # type: ignore
        #     if "content" not in delta:
        #         continue
        #     yield delta["content"]

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1,
        top_probability: float = 1,
        caching: bool = True,
    ) -> Generator[str, None, None]:
        """
        Generates single completion for prompt (message).

        :param messages: List of dict with messages and roles.
        :param temperature: Float in 0.0 - 1.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :param caching: Boolean value to enable/disable caching.
        :return: String generated completion.
        """
        yield from self._request(
            messages,
            temperature,
            top_probability,
            caching=caching,
        )
