"""
Claude API 클라이언트
보고서 내용을 생성하기 위한 Claude API 통신 모듈
"""
import os
import logging
from typing import Dict
from anthropic import Anthropic

# shared.constants를 import하면 자동으로 sys.path 설정됨
from shared.constants import ClaudeConfig
from app.utils.prompts import FINANCIAL_REPORT_SYSTEM_PROMPT

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClaudeClient:
    """Claude API를 사용하여 보고서 내용을 생성하는 클라이언트"""

    def __init__(self):
        """Claude 클라이언트 초기화"""
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", ClaudeConfig.MODEL)
        self.max_tokens = ClaudeConfig.MAX_TOKENS

        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY 환경 변수가 설정되지 않았습니다.")

        self.client = Anthropic(api_key=self.api_key)

        # 토큰 사용량 추적
        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_total_tokens = 0

    def generate_report(self, topic: str) -> str:
        """주제를 받아 금융 업무보고서 내용을 Markdown 형식으로 생성합니다.

        Args:
            topic: 보고서 주제

        Returns:
            str: Markdown 형식의 보고서 텍스트

        Examples:
            >>> client = ClaudeClient()
            >>> md_content = client.generate_report("디지털뱅킹 트렌드")
            >>> md_content.startswith("# ")
            True
        """
        user_message = f"다음 주제로 금융 업무보고서를 작성해주세요:\n\n{topic}"

        try:
            logger.info(f"Claude API 호출 시작 - 주제: {topic}")
            logger.info(f"사용 모델: {self.model}")
            logger.info(f"최대 토큰: {self.max_tokens}")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=FINANCIAL_REPORT_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # 응답 텍스트 (Markdown)
            logger.info(f"Claude API 응답 객체 정보 (생성 모드):")
            logger.info(f"  - stop_reason: {getattr(message, 'stop_reason', 'N/A')}")
            logger.info(f"  - content 개수: {len(message.content) if message.content else 0}")

            if not message.content:
                # content가 비어있을 때 상세 정보 로깅
                logger.error(f"Claude API content가 비어있습니다! (생성 모드)")
                logger.error(f"  - stop_reason: {getattr(message, 'stop_reason', 'N/A')}")
                logger.error(f"  - usage.input_tokens: {getattr(message.usage, 'input_tokens', 'N/A')}")
                logger.error(f"  - usage.output_tokens: {getattr(message.usage, 'output_tokens', 'N/A')}")
                logger.error(f"  - model: {getattr(message, 'model', 'N/A')}")

                raise ValueError(
                    f"Claude API 응답이 비어있습니다 (생성 모드). "
                    f"stop_reason={getattr(message, 'stop_reason', 'N/A')}, "
                    f"output_tokens={getattr(message.usage, 'output_tokens', 'N/A')}"
                )

            # text 타입의 content 추출 (tool_use 등 다른 타입 제외)
            text_content = None
            for content_block in message.content:
                if hasattr(content_block, 'text'):
                    text_content = content_block.text
                    break

            if not text_content:
                raise ValueError(f"Claude API 응답에서 텍스트 컨텐츠를 찾을 수 없습니다. Content types: {[type(c).__name__ for c in message.content]}")

            content = text_content

            logger.info("=" * 80)
            logger.info("Claude API 응답 내용 (Markdown):")
            logger.info("=" * 80)
            logger.info(content)
            logger.info("=" * 80)

            logger.info(f"응답 길이: {len(content)} 문자")
            logger.info(f"토큰 사용량 - Input: {message.usage.input_tokens}, Output: {message.usage.output_tokens}")

            # 토큰 사용량 저장
            self.last_input_tokens = message.usage.input_tokens
            self.last_output_tokens = message.usage.output_tokens
            self.last_total_tokens = self.last_input_tokens + self.last_output_tokens

            # Markdown 텍스트 그대로 반환 (파싱은 호출자가 수행)
            return content

        except Exception as e:
            logger.error(f"Claude API 호출 중 오류 발생: {str(e)}")
            raise Exception(f"Claude API 호출 중 오류 발생: {str(e)}")


    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        system_prompt: str = None,
        isWebSearch: bool = False
    ) -> tuple[str, int, int]:
        """Chat-based completion for conversational report generation.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
                     Example: [{"role": "user", "content": "Write a report"}]
            system_prompt: Optional system prompt (default: financial report writer)
            isWebSearch: Whether to enable web search (default: False)

        Returns:
            Tuple of (response_content, input_tokens, output_tokens)

        Raises:
            Exception: If API call fails

        Examples:
            >>> client = ClaudeClient()
            >>> messages = [{"role": "user", "content": "디지털뱅킹 트렌드 보고서 작성"}]
            >>> response, input_tokens, output_tokens = client.chat_completion(messages)
            >>> print(response[:100])
            # 디지털뱅킹 트렌드 분석 보고서

## 요약

2025년 디지털뱅킹 산업은...

            >>> # 웹 검색 활성화
            >>> response, input_tokens, output_tokens = client.chat_completion(
            ...     messages, isWebSearch=True
            ... )
        """
        # Default system prompt for financial reports
        if system_prompt is None:
            system_prompt = FINANCIAL_REPORT_SYSTEM_PROMPT

        try:
            logger.info(f"Claude chat completion 시작 - 메시지 수: {len(messages)}")
            logger.info(f"사용 모델: {self.model}")
            logger.info(f"최대 토큰: {self.max_tokens}")
            logger.info(f"웹 검색 사용: {isWebSearch}")

            # API call 파라미터 구성
            api_params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": messages
            }

            # 웹 검색 활성화 시 tools 추가
            if isWebSearch:
                api_params["tools"] = [
                    {
                        "type": "web_search_20250131"
                    }
                ]
                logger.info("웹 검색 도구 활성화됨")

            # API call with optional web search
            response = self.client.messages.create(**api_params)

            # Extract response content with detailed logging
            logger.info(f"Claude API 응답 객체 정보:")
            logger.info(f"  - stop_reason: {getattr(response, 'stop_reason', 'N/A')}")
            logger.info(f"  - content 개수: {len(response.content) if response.content else 0}")
            logger.info(f"  - model: {getattr(response, 'model', 'N/A')}")

            # 응답 객체 전체 구조 확인
            try:
                import json
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
                logger.info(f"응답 JSON: {json.dumps(response_dict, default=str, indent=2)}")
            except Exception as e:
                logger.error(f"응답 JSON 변환 실패: {str(e)}")
                logger.error(f"응답 객체 타입: {type(response)}")
                logger.error(f"응답 객체 속성: {dir(response)}")

            if response.content:
                for i, content_block in enumerate(response.content):
                    logger.info(f"  - content[{i}] 타입: {type(content_block).__name__}")
                    if hasattr(content_block, 'text'):
                        logger.info(f"    - text 길이: {len(content_block.text)}")
                    if hasattr(content_block, 'type'):
                        logger.info(f"    - type 속성: {content_block.type}")

            if not response.content:
                # content가 비어있을 때 상세 정보 로깅
                logger.error(f"Claude API content가 비어있습니다!")
                logger.error(f"  - stop_reason: {getattr(response, 'stop_reason', 'N/A')}")
                logger.error(f"  - usage.input_tokens: {getattr(response.usage, 'input_tokens', 'N/A')}")
                logger.error(f"  - usage.output_tokens: {getattr(response.usage, 'output_tokens', 'N/A')}")
                logger.error(f"  - model: {getattr(response, 'model', 'N/A')}")
                logger.error(f"  - id: {getattr(response, 'id', 'N/A')}")

                # API 메시지 내용 확인 (디버깅용)
                logger.error(f"  - 요청한 메시지 개수: {len(messages)}")
                logger.error(f"  - 시스템 프롬프트 길이: {len(system_prompt) if system_prompt else 0}")

                raise ValueError(
                    f"Claude API 응답이 비어있습니다. "
                    f"stop_reason={getattr(response, 'stop_reason', 'N/A')}, "
                    f"output_tokens={getattr(response.usage, 'output_tokens', 'N/A')}"
                )

            # text 타입의 content 추출 (tool_use 등 다른 타입 제외)
            text_content = None
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    text_content = content_block.text
                    break

            if not text_content:
                raise ValueError(f"Claude API 응답에서 텍스트 컨텐츠를 찾을 수 없습니다. Content types: {[type(c).__name__ for c in response.content]}")

            content = text_content

            logger.info("=" * 80)
            logger.info("Claude API 응답 (채팅 모드):")
            logger.info("=" * 80)
            logger.info(content[:500] + "..." if len(content) > 500 else content)
            logger.info("=" * 80)

            logger.info(f"응답 길이: {len(content)} 문자")
            logger.info(f"토큰 사용량 - Input: {response.usage.input_tokens}, Output: {response.usage.output_tokens}")

            # Track token usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            self.last_input_tokens = input_tokens
            self.last_output_tokens = output_tokens
            self.last_total_tokens = input_tokens + output_tokens

            return content, input_tokens, output_tokens

        except Exception as e:
            logger.error(f"Claude chat completion 중 오류 발생: {str(e)}")
            raise Exception(f"Claude chat completion 중 오류 발생: {str(e)}")

    def get_token_usage(self) -> Dict[str, int]:
        """Gets the last API call's token usage.

        Returns:
            Dictionary with input_tokens, output_tokens, total_tokens

        Examples:
            >>> client = ClaudeClient()
            >>> client.chat_completion([{"role": "user", "content": "Test"}])
            >>> usage = client.get_token_usage()
            >>> print(usage["total_tokens"])
            1250
        """
        return {
            "input_tokens": self.last_input_tokens,
            "output_tokens": self.last_output_tokens,
            "total_tokens": self.last_total_tokens
        }
