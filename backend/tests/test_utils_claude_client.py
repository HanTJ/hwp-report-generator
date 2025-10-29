"""
Claude API 클라이언트 테스트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.utils.claude_client import ClaudeClient


@pytest.fixture
def mock_claude_response():
    """Claude API 응답 mock"""
    mock_response = Mock()
    mock_response.content = [
        Mock(text="""[제목]
디지털 뱅킹 혁신 보고서
[배경제목]
추진 배경
[배경]
최근 디지털 금융 환경의 급격한 변화로 인해 은행들은 새로운 기술 도입이 필수적입니다.
[주요내용제목]
주요 혁신 동향
[주요내용]
1. AI 기반 개인화 서비스
2. 블록체인 기술 활용
3. 모바일 우선 전략
[결론제목]
향후 과제
[결론]
지속적인 기술 투자와 인재 육성이 필요합니다.
[요약제목]
핵심 요약
[요약]
디지털 뱅킹은 AI와 빅데이터를 활용하여 고객 경험을 혁신하고 있습니다.""")
    ]
    mock_response.usage = Mock(
        input_tokens=1500,
        output_tokens=3200
    )
    return mock_response


@pytest.mark.unit
class TestClaudeClientInit:
    """ClaudeClient 초기화 테스트"""

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key', 'CLAUDE_MODEL': 'claude-sonnet-4-5-20250929'})
    def test_init_success(self):
        """정상 초기화 테스트"""
        client = ClaudeClient()

        assert client.api_key == 'test_api_key'
        assert client.model == 'claude-sonnet-4-5-20250929'
        assert client.client is not None
        assert client.last_input_tokens == 0
        assert client.last_output_tokens == 0
        assert client.last_total_tokens == 0

    def test_init_missing_api_key(self, monkeypatch):
        """API 키 누락 시 ValueError 발생"""
        monkeypatch.delenv('CLAUDE_API_KEY', raising=False)

        with pytest.raises(ValueError) as exc_info:
            ClaudeClient()

        assert "CLAUDE_API_KEY" in str(exc_info.value)

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    def test_init_default_model(self, monkeypatch):
        """기본 모델 설정 확인"""
        monkeypatch.delenv('CLAUDE_MODEL', raising=False)

        client = ClaudeClient()

        # 기본값 확인 (main.py나 claude_client.py에서 설정된 기본값)
        assert client.model is not None


@pytest.mark.unit
class TestClaudeClientGenerateReport:
    """보고서 생성 테스트"""

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    @patch('app.utils.claude_client.Anthropic')
    def test_generate_report_success(self, mock_anthropic_class, mock_claude_response):
        """보고서 생성 성공 테스트"""
        # Mock 설정
        mock_client_instance = Mock()
        mock_anthropic_class.return_value = mock_client_instance
        mock_client_instance.messages.create.return_value = mock_claude_response

        client = ClaudeClient()
        result = client.generate_report("2025년 디지털 뱅킹 트렌드")

        # 구조 검증
        assert "title" in result
        assert "summary" in result
        assert "background" in result
        assert "main_content" in result
        assert "conclusion" in result

        # 내용 검증
        assert result["title"] == "디지털 뱅킹 혁신 보고서"
        assert "AI 기반 개인화 서비스" in result["main_content"]

        # API 호출 확인
        mock_client_instance.messages.create.assert_called_once()

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    @patch('app.utils.claude_client.Anthropic')
    def test_generate_report_with_valid_structure(self, mock_anthropic_class, mock_claude_response):
        """반환된 보고서 구조 검증"""
        mock_client_instance = Mock()
        mock_anthropic_class.return_value = mock_client_instance
        mock_client_instance.messages.create.return_value = mock_claude_response

        client = ClaudeClient()
        result = client.generate_report("테스트 주제")

        # 모든 필수 키 존재 확인
        required_keys = [
            "title", "title_background", "background",
            "title_main_content", "main_content",
            "title_conclusion", "conclusion",
            "title_summary", "summary"
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    @patch('app.utils.claude_client.Anthropic')
    def test_generate_report_tracks_token_usage(self, mock_anthropic_class, mock_claude_response):
        """토큰 사용량 추적 테스트"""
        mock_client_instance = Mock()
        mock_anthropic_class.return_value = mock_client_instance
        mock_client_instance.messages.create.return_value = mock_claude_response

        client = ClaudeClient()
        client.generate_report("테스트 주제")

        # 토큰 사용량 확인
        assert client.last_input_tokens == 1500
        assert client.last_output_tokens == 3200
        assert client.last_total_tokens == 4700

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    @patch('app.utils.claude_client.Anthropic')
    def test_generate_report_api_error(self, mock_anthropic_class):
        """API 호출 실패 시 예외 처리"""
        mock_client_instance = Mock()
        mock_anthropic_class.return_value = mock_client_instance
        mock_client_instance.messages.create.side_effect = Exception("API Error")

        client = ClaudeClient()

        with pytest.raises(Exception) as exc_info:
            client.generate_report("테스트 주제")

        assert "API Error" in str(exc_info.value)


@pytest.mark.unit
class TestClaudeClientParseReportContent:
    """보고서 내용 파싱 테스트"""

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    def test_parse_valid_content(self):
        """정상적인 응답 파싱 테스트"""
        client = ClaudeClient()

        content = """[제목]
테스트 보고서
[배경제목]
배경
[배경]
배경 내용입니다.
[주요내용제목]
주요 내용
[주요내용]
주요 내용입니다.
[결론제목]
결론
[결론]
결론 내용입니다.
[요약제목]
요약
[요약]
요약 내용입니다."""

        result = client._parse_report_content(content)

        assert result["title"] == "테스트 보고서"
        assert result["title_background"] == "배경"
        assert result["background"] == "배경 내용입니다."
        assert result["title_main_content"] == "주요 내용"
        assert result["main_content"] == "주요 내용입니다."
        assert result["title_conclusion"] == "결론"
        assert result["conclusion"] == "결론 내용입니다."
        assert result["title_summary"] == "요약"
        assert result["summary"] == "요약 내용입니다."

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    def test_parse_missing_sections(self):
        """일부 섹션 누락 시 기본값 처리"""
        client = ClaudeClient()

        # 결론과 요약 섹션의 내용이 비어있는 경우
        content = """[제목]
테스트 보고서
[배경제목]
배경
[배경]
배경 내용입니다.
[주요내용제목]
주요 내용
[주요내용]
주요 내용입니다.
[결론제목]
결론
[결론]

[요약제목]
요약
[요약]
"""

        result = client._parse_report_content(content)

        # 존재하는 섹션
        assert result["title"] == "테스트 보고서"
        assert result["background"] == "배경 내용입니다."
        assert result["main_content"] == "주요 내용입니다."

        # 누락된 섹션은 기본 메시지 (빈 문자열인 경우)
        assert "(내용이 생성되지 않았습니다" in result["conclusion"]
        assert "(내용이 생성되지 않았습니다" in result["summary"]

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    def test_parse_empty_content(self):
        """빈 응답 처리"""
        client = ClaudeClient()

        result = client._parse_report_content("")

        # 모든 섹션이 기본 메시지
        assert "(내용이 생성되지 않았습니다" in result["title"]
        assert "(내용이 생성되지 않았습니다" in result["background"]
        assert "(내용이 생성되지 않았습니다" in result["main_content"]
        assert "(내용이 생성되지 않았습니다" in result["conclusion"]
        assert "(내용이 생성되지 않았습니다" in result["summary"]

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    def test_parse_malformed_content(self):
        """잘못된 형식의 응답 처리"""
        client = ClaudeClient()

        # 구분자가 없는 내용
        content = "구분자 없는 일반 텍스트입니다."

        result = client._parse_report_content(content)

        # 기본 메시지가 들어가야 함
        assert "(내용이 생성되지 않았습니다" in result["title"]

    @patch.dict('os.environ', {'CLAUDE_API_KEY': 'test_api_key'})
    def test_parse_whitespace_handling(self):
        """공백 처리 테스트"""
        client = ClaudeClient()

        content = """[제목]
   테스트 보고서
[배경제목]
   배경
[배경]
   배경 내용
[주요내용제목]
   주요내용
[주요내용]
   주요 내용
[결론제목]
   결론
[결론]
   결론 내용
[요약제목]
   요약
[요약]
   요약 내용"""

        result = client._parse_report_content(content)

        # 앞뒤 공백이 제거되어야 함
        assert result["title"] == "테스트 보고서"
        assert result["title_background"] == "배경"
        assert result["background"] == "배경 내용"
