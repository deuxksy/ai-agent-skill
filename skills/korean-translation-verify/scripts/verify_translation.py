#!/usr/bin/env python3
"""
GL.iNet 한국어 번역 검증 스크립트

Gemma-3-27b-it API를 사용하여 번역 품질을 검증합니다.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import time


class TranslationVerifier:
    """한국어 번역 검증 클래스"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMMA_API_KEY")
        if not self.api_key:
            raise ValueError("""
GEMMA_API_KEY가 필요합니다.

설정 방법:
1. 환경 변수 설정:
   export GEMMA_API_KEY="your_api_key_here"

2. 또는 소스 코드에 직접 설정:
   verifier = TranslationVerifier(api_key="your_api_key_here")

API 키는 Tailscale Aperture에서 발급받을 수 있습니다.
""")

        self.api_url = "https://ai.bun-bull.ts.net/v1beta/models/gemma-3-27b-it:generateContent"
        self.headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

        self.system_prompt = """당신은 한국어 기술 문서 번역 전문가입니다.
GL.iNet 라우터 펌웨어 문서의 한국어 번역을 검증해주세요.

검증 기준:
1. 자연스러운 한국어 표현
2. 기술 용어의 적절한 번역 (영어 병기 허용)
3. 문장의 간결성과 명확성
4. 기계 번역투의 어색한 표현 없는지
5. 마크다운 형식 준수

피드백 형식:
- 통과: 번역이 적절함
- ISSUE: [구체적인 문제점과 개선 제안]

한국어로 답변해주세요."""

    def _prepare_payload(self, content: str) -> Dict:
        escaped_content = json.dumps(content, ensure_ascii=False)
        user_message = f"""다음 한국어 번역을 검증해주세요:

{escaped_content}

위 번역의 품질을 평가하고 문제가 있다면 구체적으로 지적해주세요."""

        return {
            "contents": [{"parts": [{"text": user_message}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048
            }
        }

    def _call_api(self, payload: Dict) -> Optional[Dict]:
        try:
            response = requests.post(
                self.api_url, headers=self.headers,
                json=payload, timeout=60
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API 오류: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return None

    def _extract_feedback(self, response: Dict) -> str:
        try:
            candidates = response.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return "피드백 추출 실패"
        except Exception as e:
            return f"피드백 추출 오류: {e}"

    def _parse_feedback_status(self, feedback: str) -> tuple[bool, str]:
        feedback_lower = feedback.lower()
        if "issue" in feedback_lower or "문제" in feedback_lower or "어색" in feedback_lower:
            return False, feedback
        elif "통과" in feedback or "적절" in feedback or "잘됨" in feedback:
            return True, feedback
        else:
            return False, feedback

    def verify_file(self, file_path: str, max_length: int = 3000) -> Dict:
        path = Path(file_path)
        if not path.exists():
            return {"file": str(file_path), "status": "error", "message": "파일을 찾을 수 없습니다"}

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if len(content) > max_length:
                content = content[:max_length] + "\n\n...(내용 생략)..."

            payload = self._prepare_payload(content)
            response = self._call_api(payload)

            if not response:
                return {"file": str(file_path), "status": "error", "message": "API 호출 실패"}

            feedback = self._extract_feedback(response)
            passed, parsed_feedback = self._parse_feedback_status(feedback)

            return {
                "file": str(file_path),
                "status": "passed" if passed else "needs_review",
                "feedback": parsed_feedback
            }
        except Exception as e:
            return {"file": str(file_path), "status": "error", "message": f"검증 중 오류: {e}"}

    def verify_batch(self, file_paths: List[str], delay: float = 1.0,
                     progress_callback: Optional[callable] = None) -> List[Dict]:
        results = []
        total = len(file_paths)

        for i, file_path in enumerate(file_paths, 1):
            if progress_callback:
                progress_callback(i, total, file_path)

            result = self.verify_file(file_path)
            results.append(result)

            if i < total:
                time.sleep(delay)

        return results

    def save_results(self, results: List[Dict], output_path: str):
        passed = sum(1 for r in results if r.get("status") == "passed")
        needs_review = sum(1 for r in results if r.get("status") == "needs_review")
        errors = sum(1 for r in results if r.get("status") == "error")

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total": len(results),
                "passed": passed,
                "needs_review": needs_review,
                "errors": errors
            },
            "results": results
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n=== 검증 완료 ===")
        print(f"전체 파일: {len(results)}")
        print(f"통과: {passed}")
        print(f"검증 필요: {needs_review}")
        print(f"오류: {errors}")


def find_korean_md_files(base_dir: str) -> List[str]:
    base_path = Path(base_dir)
    if not base_path.exists():
        raise ValueError(f"디렉토리를 찾을 수 없습니다: {base_dir}")

    ko_docs = base_path / "docs" / "ko" / "docs"
    if not ko_docs.exists():
        raise ValueError(f"한국어 문서 디렉토리를 찾을 수 없습니다: {ko_docs}")

    return sorted([str(f) for f in ko_docs.rglob("*.md")])


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GL.iNet 한국어 번역 검증 도구")
    parser.add_argument("--dir", default=".", help="프로젝트 루트 디렉토리")
    parser.add_argument("--file", help="단일 파일 검증")
    parser.add_argument("--output", default="verification_results.json", help="결과 출력 파일")
    parser.add_argument("--delay", type=float, default=1.0, help="API 호출 간 지연 시간")

    args = parser.parse_args()

    try:
        verifier = TranslationVerifier()

        if args.file:
            result = verifier.verify_file(args.file)
            print(f"\n=== {args.file} ===")
            print(f"상태: {result['status']}")
            print(f"피드백: {result.get('feedback', result.get('message', ''))}")
        else:
            files = find_korean_md_files(args.dir)
            print(f"총 {len(files)}개 파일을 검증합니다...")

            def progress_callback(current, total, file_path):
                print(f"진행: {current}/{total}")

            results = verifier.verify_batch(files, delay=args.delay,
                                            progress_callback=progress_callback)
            verifier.save_results(results, args.output)

    except Exception as e:
        print(f"오류: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
