from __future__ import annotations

import logging
import os

import httpx
import openai
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

log = logging.getLogger(__name__)


class OpenAIHelper:
    """
    ChatGPT helper class.
    """

    def __init__(self):
        """
        Initializes the OpenAI helper class with the given configuration.
        :param config: A dictionary containing the GPT configuration
        """
        load_dotenv()
        self.OPENAIMODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', '')
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        OPENAI_PROXY = os.environ.get('OPENAI_PROXY', '')
        self.openai_client = OpenAI(timeout=600, api_key=OPENAI_API_KEY, http_client=httpx.Client(
            proxies=OPENAI_PROXY,
            transport=httpx.HTTPTransport(local_address="0.0.0.0"),
        ), )

    def get_chat_response(self, chat_id: int, query: str, prompt: str = None):
        """
        #
        从GPT模型获取完整响应。
        Gets a full response from the GPT model.
        :param model:
        :param maxCount:  最大文字数
        :param prompt: 辅助提示
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used
        """
        plugins_used = ()
        response = self.__common_get_chat_response(chat_id, query, prompt=prompt)
        answer = ''

        if len(response.choices) > 1:
            for index, choice in enumerate(response.choices):
                content = choice['message']['content'].strip()
                answer += f'{index + 1}\u20e3\n'
                answer += content
                answer += '\n\n'
        else:
            answer = response.choices[0].message.content.strip()
        return answer

    @retry(
        reraise=True,
        retry=retry_if_exception_type(openai.RateLimitError),
        wait=wait_fixed(20),
        stop=stop_after_attempt(3)
    )
    def __common_get_chat_response(self, chat_id: int, query: str, prompt=None):

        """
        todo async
        Request a response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used
        """
        try:
            conversations = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]
            common_args = {
                'model': self.OPENAIMODEL,
                'messages': conversations,
                'temperature': 1.0,
                'n': 1,
                'max_tokens': 50,
                'presence_penalty': 0.0,
                'frequency_penalty': 0.0,
                'stream': False,
                'response_format':{"type": "json_object"}
            }
            return self.openai_client.chat.completions.create(**common_args)
        except openai.RateLimitError as e:
            raise e
        except Exception as e:
            raise e
