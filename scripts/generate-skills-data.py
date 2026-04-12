#!/usr/bin/env python3
"""
Parse all SKILL.md files from ~/.hermes/skills/ and output structured JSON.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter
from typing import Dict, List, Optional, Any, Tuple

SKILLS_DIR = Path.home() / ".hermes" / "skills"
OUTPUT_PATH = Path(
    "/Users/hjshin/Desktop/project/work/icbm2-skills-marketplace/src/data/skills.json"
)

READING_SPEED_WPM = 200  # average adult reading speed

# Korean translations for skill descriptions (slug -> Korean description)
KO_TRANSLATIONS = {
    "apple-notes": "macOS에서 memo CLI로 Apple Notes 관리 (생성, 보기, 검색, 편집).",
    "apple-reminders": "remindctl CLI로 Apple Reminders 관리 (목록, 추가, 완료, 삭제).",
    "findmy": "macOS에서 FindMy.app과 AppleScript로 Apple 기기 및 AirTag 추적.",
    "imessage": "macOS에서 imsg CLI로 iMessage/SMS 송수신.",
    "agentnews-monitor": "AgentNews 실시간 모니터링 — 매시간 AI 에이전트 뉴스 피드를 확인하고 관심사 매칭 뉴스를 threshold 기반으로 알림 (하루 2~3건 제한)",
    "ai-model-tracker": "AI 모델 릴리즈/업데이트를 매일 Notion에 기록 — 새 모델 출시, 벤치마크, 가격 변동 추적",
    "automation-healthcheck": "ICBM2 자동화 시스템 전체 헬스체크 — 크론 잡 상태, API 연결, 스크립트 무결성 점검",
    "botmadang": "봇마당(BotMadang) 플랫폼에서 게시글과 댓글을 자동 작성하는 스킬",
    "colab-image-gen": "Google Colab 또는 Kaggle Notebooks 무료 GPU(T4)로 SDXL/FLUX 이미지를 생성하는 자동화 파이프라인. 클라우드 GPU 필수.",
    "daily-self-review": "ICBM2 매일 자기 개선 리뷰 — 당일 세션 분석, 스킬 개선, 메모리 정리",
    "dev-news-to-wiki": "Notion Dev News Archive 뉴스 클리핑을 분석하여 LLM Wiki에 자동 등록",
    "feedback-loop": "ICBM2 피드백 루프 — 주인님 교정/선호를 학습하여 다음 세션에 반영",
    "invest-memo": "투자 관련 뉴스와 시황을 매일 Notion에 기록 — 한국/미국 주식 시장 종합",
    "ios-trend-digest": "iOS/Swift 기술 트렌드를 매일 Notion에 기록 — HN, r/iOSProgramming, Apple 개발자 뉴스에서 수집",
    "knowledge-graph": "ICBM2 지식 그래프 자동 구축 — Notion DB 데이터를 수집하여 엔티티/관계를 추출하고 인터랙티브 그래프로 시각화",
    "learning-log": "주간 학습 로그를 Notion에 기록 — 기술 질문, 조사 내용 자동 정리",
    "morning-briefing": "매일 아침 통합 인사이트 브리핑 — 날씨, 주식, 뉴스, 자동화 성과, 일정을 교차 분석",
    "notion-dashboard": "Notion DB에 ICBM2 자동화 성과를 일별로 누적 기록",
    "notion-idea-note": "Notion 아이디어 노트 DB에 랜덤 페르소나로 블로그 수준의 심층 칼럼을 자동 생성하는 스킬",
    "shiporslop-kr": "Ship or Slop KR 플랫폼에서 고품질 AI 아이디어를 생성, 제출, 투표/리뷰하는 스킬",
    "stock-market-tracker": "한국/미국 주식 시장 데이터 수집, 포트폴리오 추적, 뉴스 기반 시황 분석 자동화",
    "tistory-publisher": "Tistory 블로그 자동 발행 — 쿠키 기반 내부 API를 사용하여 글 작성/발행",
    "weekly-automation-report": "자동화 성과 주간 리포트를 Notion에 기록 — 아이디어 노트, Ship or Slop, 봇마당, Tistory, 크론 잡 상태 종합",
    "weekly-self-report": "ICBM2 주간 자기 개선 리포트 — 모든 자동화 활동을 종합 분석하여 성과와 개선점을 도출",
    "weekly-tech-digest": "주간 기술 요약 뉴스레터 — AI/iOS/자동화 트렌드를 종합하여 Tistory에 자동 발행",
    "agent-prompts": "전문 에이전트용 최적화 프롬프트 템플릿 — 코딩, 리서치, 자동화 작업에 특화",
    "claude-code": "Anthropic Claude Code CLI로 코딩 작업 위임 — 기능 구현, 리팩토링, PR 리뷰, 반복 코딩",
    "codex": "OpenAI Codex CLI로 코딩 작업 위임 — 기능 구현, 리팩토링, PR 리뷰, 일괄 이슈 수정",
    "hermes-agent": "Hermes Agent 완전 가이드 — CLI 사용, 설정, 에이전트 생성, 게이트웨이, 스킬, 음성, 도구, 프로필 관리",
    "opencode": "OpenCode CLI로 코딩 작업 위임 — 기능 구현, 리팩토링, PR 리뷰, 장기 자율 세션",
    "ascii-art": "pyfiglet(571폰트), cowsay, boxes, toilet 등으로 ASCII 아트 생성. API 키 불필요.",
    "ascii-video": "ASCII 아트 비디오 프로덕션 파이프라인 — 비디오/오디오/이미지를 컬러 ASCII 캐릭터 비디오(MP4, GIF)로 변환",
    "ideation": "창의적 제약을 통해 프로젝트 아이디어 생성 — 코드, 아트, 하드웨어, 글쓰기 등 다양한 분야",
    "excalidraw": "Excalidraw JSON 포맷으로 수작업 스타일 다이어그램 생성 — 아키텍처, 순서도, 컨셉 맵 등",
    "manim-video": "Manim Community Edition으로 수학/기술 애니메이션 제작 — 3Blue1Brown 스타일 설명 영상",
    "p5js": "p5.js로 인터랙티브/제너러티브 비주얼 아트 생성 — 브라우저 스케치, 데이터 시각화, 3D 씬",
    "popular-web-designs": "실제 웹사이트에서 추출한 54종 프로덕션 품질 디자인 시스템",
    "songwriting-and-ai-music": "작사 기법 및 AI 음악 생성 프롬프트 (Suno 중심)",
    "jupyter-live-kernel": "라이브 Jupyter 커널로 상태 유지형 반복 Python 분석",
    "skill-security-audit": "스킬 파일 보안 감사 — 공개 전 민감 정보(DB ID, 절대경로, 시크릿 경로, 계정명 등) 검출 및 환경변수 대체",
    "webhook-subscriptions": "이벤트 기반 에이전트 활성화를 위한 웹훅 구독 생성 및 관리",
    "dogfood": "웹 애플리케이션 체계적 탐색 QA 테스트 — 버그 발견, 증거 캡처, 구조화된 리포트 생성",
    "himalaya": "IMAP/SMTP로 이메일 관리 CLI — 목록, 읽기, 작성, 회신, 검색, 정리. 다중 계정 지원.",
    "minecraft-modpack-server": "CurseForge/Modrinth 서버 팩에서 모드 Minecraft 서버 구축 — NeoForge/Forge, JVM 튜닝, 백업",
    "pokemon-player": "헤드리스 에뮬레이션으로 Pokemon 자동 플레이 — RAM에서 게임 상태 읽기, 전략적 결정, 버튼 입력",
    "codebase-inspection": "pygount으로 코드베이스 검사 — LOC 카운트, 언어별 분석, 코드/주석 비율",
    "github-auth": "git 또는 gh CLI로 GitHub 인증 설정 — HTTPS 토큰, SSH 키, 크레덴셜 헬퍼",
    "github-code-review": "git diff 분석으로 코드 변경 리뷰 — PR 인라인 코멘트, 사전 푸시 리뷰",
    "github-issues": "GitHub 이슈 생성, 관리, 트리아지, 닫기 — 라벨, 담당자, PR 연결",
    "github-pr-workflow": "풀 리퀘스트 전체 라이프사이클 — 브랜치 생성, 커밋, PR 오픈, CI 모니터링, 병합",
    "github-repo-management": "GitHub 저장소 관리 — 클론, 생성, 포크, 리모트, 시크릿, 릴리즈, 워크플로우",
    "github-trending-monitor": "GitHub 트렌딩 리포지토리와 관심 프로젝트의 새 릴리즈를 자동 모니터링 — AI/ML/iOS 트렌딩 수집, Notion DB 저장",
    "find-nearby": "OpenStreetMap으로 근처 장소 검색 — 식당, 카페, 약국 등. API 키 불필요.",
    "mcporter": "mcporter CLI로 MCP 서버/도구 목록, 설정, 인증, 호출 — HTTP/stdio 지원",
    "native-mcp": "내장 MCP 클라이언트 — 외부 MCP 서버 연결, 도구 발견, 네이티브 도구로 자동 등록",
    "gif-search": "Tenor에서 GIF 검색/다운로드 — curl과 jq만으로 동작. 채팅용 반응 GIF에 유용.",
    "heartmula": "HeartMuLa 오픈소스 음악 생성 모델 — 가사+태그로 전체 곡 생성, 다국어 지원",
    "songsee": "오디오 파일에서 스펙트로그램 및 오디오 특징 시각화 생성 — mel, chroma, MFCC 등",
    "youtube-content": "YouTube 비디오 트랜스크립트 추출 및 콘텐츠 변환",
    "modal-serverless-gpu": "서버리스 GPU 클라우드 — ML 워크로드 온디맨드 GPU, 모델 API 배포, 자동 스케일링",
    "evaluating-llms-harness": "60개 이상 학술 벤치마크로 LLM 평가 — MMLU, HumanEval, GSM8K, TruthfulQA 등",
    "weights-and-biases": "W&B로 ML 실험 추적 — 자동 로깅, 실시간 시각화, 하이퍼파라미터 스윕, 모델 레지스트리",
    "huggingface-hub": "Hugging Face Hub CLI (hf) — 모델/데이터셋 검색, 다운로드, 업로드, Space 관리",
    "gguf-quantization": "GGUF 포맷 및 llama.cpp 양자화 — CPU/GPU 효율적 추론, 2~8비트 유연한 양자화",
    "guidance": "정규식/문법으로 LLM 출력 제어 — JSON/XML/코드 구조 보장, 구조화된 생성",
    "llama-cpp": "CPU, Apple Silicon, 소비자 GPU에서 LLM 추론 — NVIDIA 없이도 동작, GGUF 양자화 지원",
    "obliteratus": "오픈웨이트 LLM의 거부 행위 제거 — 기계론적 해석가능성 기법으로 가드레일 제거",
    "outlines": "생성 중 유효한 JSON/XML/코드 구조 보장 — Pydantic 모델, 타입 안전 출력",
    "serving-llms-vllm": "vLLM PagedAttention으로 고처리량 LLM 서빙 — OpenAI 호환 엔드포인트, 양자화 지원",
    "audiocraft-audio-generation": "PyTorch 오디오 생성 — 텍스트→음악(MusicGen), 텍스트→사운드(AudioGen)",
    "clip": "OpenAI 비전-언어 연결 모델 — 제로샷 이미지 분류, 이미지-텍스트 매칭, 크로스모달 검색",
    "segment-anything-model": "이미지 세그멘테이션 파운데이션 모델 — 제로샷 전이, 포인트/박스/마스크 프롬프트",
    "stable-diffusion-image-generation": "HuggingFace Diffusers로 Stable Diffusion 텍스트→이미지 생성",
    "whisper": "OpenAI 범용 음성 인식 — 99개 언어, 전사, 영어 번역, 6가지 모델 크기",
    "dspy": "Stanford NLP의 DSPy — 선언형 프로그래밍으로 AI 시스템 구축, 프롬프트 자동 최적화",
    "axolotl": "Axolotl로 LLM 파인튜닝 — YAML 설정, 100+ 모델, LoRA/QLoRA, DPO/KTO/ORPO/GRPO",
    "grpo-rl-training": "TRL로 GRPO/강화학습 파인튜닝 — 추론 및 작업 특화 모델 훈련",
    "peft-fine-tuning": "HuggingFace PEFT로 파라미터 효율적 파인튜닝 — LoRA, QLoRA, 25개 이상 방법",
    "pytorch-fsdp": "PyTorch FSDP 완전 분할 데이터 병렬 훈련 — 파라미터 샤딩, 혼합 정밀도, CPU 오프로딩",
    "fine-tuning-with-trl": "TRL로 강화학습 LLM 파인튜닝 — SFT, DPO, PPO/GRPO, 보상 모델 훈련",
    "unsloth": "Unsloth 고속 파인튜닝 — 2~5배 빠른 훈련, 50~80% 메모리 절감",
    "obsidian": "Obsidian 볼트에서 노트 읽기, 검색, 생성",
    "llm-rpg": "LLM 기반 텍스트 RPG/전략 시뮬레이션 — 인터랙티브 어드벤처, 캐릭터 성장, 전투, 스토리",
    "skillsmp-search": "SkillsMP 마켓플레이스에서 AI 스킬 키워드/시맨틱 검색",
    "strategy-sim": "군사/전략 시뮬레이션 엔진 — 시나리오 분석, 전술 개발, 자원 할당 최적화",
    "google-workspace": "Gmail, 캘린더, 드라이브, 연락처, 시트, 문서 통합 — gws CLI + OAuth2",
    "linear": "Linear 이슈/프로젝트/팀 관리 — GraphQL API, API 키 인증, curl만으로 동작",
    "nano-pdf": "자연어 명령으로 PDF 편집 — 텍스트 수정, 오타 교정, 제목 업데이트",
    "notion": "Notion API로 페이지/데이터베이스/블록 관리 — curl로 검색, 생성, 업데이트, 쿼리",
    "ocr-and-documents": "PDF 및 스캔 문서에서 텍스트 추출 — web_extract, pymupdf, marker-pdf",
    "powerpoint": ".pptx 파일 완전 지원 — 생성, 읽기, 편집, 병합, 템플릿, 스피커 노트",
    "godmode": "G0DM0D3 기법으로 API 서빙 LLM 제일브레이크 — Parseltongue 난독화, 시스템 프롬프트 템플릿",
    "arxiv": "arXiv 무료 REST API로 학술 논문 검색/조회 — 키워드, 저자, 카테고리, ID 검색",
    "blogwatcher": "blogwatcher-cli로 블로그/RSS/Atom 피드 모니터링 — 새 글 스캔, 읽음 상태 추적",
    "llm-wiki": "Karpathy의 LLM Wiki — 영구적 인터링크 마크다운 지식 베이스 구축/유지",
    "polymarket": "Polymarket 예측 시장 데이터 조회 — 시장 검색, 가격, 오더북, 가격 이력",
    "research-paper-writing": "ML/AI 연구 논문 엔드투엔드 작성 — 실험 설계부터 분석, 초안, 수정, 제출까지",
    "openhue": "OpenHue CLI로 Philips Hue 조명/방/씬 제어 — 켜기/끄기, 밝기, 색상, 색온도",
    "xitter": "x-cli로 X/Twitter 상호작용 — 포스팅, 타임라인, 검색, 좋아요, 리트윗, 북마크",
    "plan": "Hermes 플랜 모드 — 컨텍스트 검사, 마크다운 계획 작성, 실행하지 않음",
    "requesting-code-review": "사전 커밋 검증 파이프라인 — 정적 보안 스캔, 린팅, 테스트 실행",
    "subagent-driven-development": "독립 태스크별 delegate_task 분배 — 2단계 리뷰(사양 준수 + 코드 품질)",
    "systematic-debugging": "4단계 근원 원인 조사 — 버그/테스트 실패/예상치 못한 동작 분석",
    "test-driven-development": "TDD 강제 — RED-GREEN-REFACTOR 사이클, 테스트 우선 접근",
    "writing-plans": "다단계 작업용 구현 계획 생성 — 바이트 단위 태스크, 정확한 파일 경로, 완전한 코드 예제",
    "telegram-commands": "ICBM2 핵심 자동화 기능에 빠르게 접근하는 텔레그램 명령어 라우터",
    "agent-benchmark-tracker": "AI 에이전트/모델 벤치마크 결과를 추적하여 Notion에 기록 — SWE-bench, HumanEval, GAIA, WebArena, LiveCodeBench 등",
    "auto-researcher": "심층 자동 조사 — 주제를 받아 여러 소스에서 수집 후 종합 리포트 작성",
    "chrome-automation": "Playwright 기반 웹 브라우저 자동화 — 로그인, 스크래핑, 폼 제출, 스크린샷, PDF 생성 등",
    "docker-manager": "Docker 컨테이너/이미지/네트워크/볼륨 관리 — 생성, 배포, 모니터링, 로그 수집, 자동 정리",
    "portfolio-rebalancer": "포트폴리오 리밸런싱 제안 — 보유 종목 비중 분석, 목표 비중 대비 차이 계산, 매수/매도 추천",
    "smart-summary": "다중 소스 지능 요약 — URL, PDF, 유튜브, 긴 텍스트를 핵심만 추려서 요약",
    "tech-doc-translator": "영문 기술 문서를 한국어로 요약 번역 — HN, Arxiv, Reddit 기술 글을 수집하여 Notion에 기록",
}


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """
    Parse YAML-like frontmatter from SKILL.md content.
    Returns (metadata_dict, body_markdown).
    """
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    raw_yaml = parts[1].strip()
    body = parts[2].strip()

    metadata = {}
    current_section = metadata
    current_key_path = []

    for line in raw_yaml.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Count indentation to determine nesting level
        indent = len(line) - len(line.lstrip())
        indent_level = indent // 2  # assuming 2-space indent

        # Simple key: value parsing
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            # Parse the value
            parsed_value = parse_yaml_value(value)

            # Determine nesting
            if indent_level == 0:
                # Top-level key
                if value == "" or value.startswith("#"):
                    # This is a nested section start
                    metadata[key] = {}
                    current_section = metadata[key]
                    current_key_path = [key]
                else:
                    metadata[key] = parsed_value
            elif indent_level == 1 and current_key_path:
                current_section[key] = parsed_value
            elif indent_level == 2 and len(current_key_path) >= 1:
                # This is a sub-key under a nested section
                current_section[key] = parsed_value

    return metadata, body


def parse_yaml_value(value: str):
    """Parse a YAML value string into appropriate Python type."""
    value = value.strip()

    # Empty value
    if not value:
        return ""

    # List: [item1, item2, ...]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items = []
        for item in inner.split(","):
            item = item.strip()
            if item.startswith('"') and item.endswith('"'):
                items.append(item[1:-1])
            elif item.startswith("'") and item.endswith("'"):
                items.append(item[1:-1])
            else:
                items.append(item)
        return items

    # String with quotes
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    # Boolean
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    return value


def extract_nested(metadata: dict, dotted_key: str, default=None):
    """Extract a value from nested dict using dot notation."""
    keys = dotted_key.split(".")
    current = metadata
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def estimate_reading_time(text: str) -> float:
    """Estimate reading time in minutes based on word count."""
    words = len(text.split())
    minutes = words / READING_SPEED_WPM
    return max(1, round(minutes, 1)) if minutes > 0 else 1


def process_skill_file(filepath: Path) -> Optional[dict]:
    """Process a single SKILL.md file and return structured data."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return None

    if not content.strip():
        print(f"  Warning: Empty file: {filepath}")
        return None

    metadata, body = parse_frontmatter(content)

    # Determine category and skill name from path
    # Path: .../skills/category/skill-name/SKILL.md (2 levels)
    #   or: .../skills/category/subcategory/skill-name/SKILL.md (3 levels)
    rel_path = filepath.relative_to(SKILLS_DIR)
    parts = rel_path.parts
    category = parts[0] if len(parts) >= 2 else "uncategorized"
    skill_dir_name = parts[-2] if len(parts) >= 2 else filepath.parent.name

    name = metadata.get("name", skill_dir_name)
    description = metadata.get("description", "")
    version = str(metadata.get("version", ""))
    author = str(metadata.get("author", ""))
    license_val = str(metadata.get("license", ""))

    tags = extract_nested(metadata, "metadata.hermes.tags", [])
    related_skills = extract_nested(metadata, "metadata.hermes.related_skills", [])
    prerequisites = metadata.get("prerequisites", {})

    line_count = len(content.splitlines())
    reading_time = estimate_reading_time(body)

    # Determine Korean and English descriptions
    skill_slug = slugify(name)
    ko_desc = KO_TRANSLATIONS.get(skill_slug, "")

    # description_en: keep original English description (or whatever was in SKILL.md)
    description_en = description if description else ""

    # If description is empty but we have a Korean translation, use it as primary
    if not description and ko_desc:
        description = ko_desc

    # File modification time for sorting
    try:
        mtime = int(filepath.stat().st_mtime)
    except Exception:
        mtime = 0

    return {
        "name": name,
        "slug": skill_slug,
        "category": category,
        "category_slug": slugify(category),
        "dir_name": skill_dir_name,
        "description": description,
        "description_ko": ko_desc,
        "description_en": description_en,
        "version": version,
        "author": author,
        "license": license_val,
        "tags": tags,
        "related_skills": related_skills,
        "prerequisites": prerequisites if isinstance(prerequisites, dict) else {},
        "content": body,
        "reading_time_minutes": reading_time,
        "line_count": line_count,
        "created_at": mtime,
    }


def main():
    print(f"Scanning skills in: {SKILLS_DIR}")
    print(f"Output to: {OUTPUT_PATH}")
    print()

    if not SKILLS_DIR.exists():
        print(f"Error: Skills directory not found: {SKILLS_DIR}")
        return

    # Find all SKILL.md files
    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    print(f"Found {len(skill_files)} SKILL.md files")
    print()

    skills = []
    errors = 0

    for filepath in skill_files:
        rel = filepath.relative_to(SKILLS_DIR)
        skill = process_skill_file(filepath)
        if skill:
            skills.append(skill)
        else:
            errors += 1

    # Build category summary
    category_counter = Counter(s["category"] for s in skills)
    categories = []
    for cat_name, count in category_counter.most_common():
        categories.append(
            {
                "name": cat_name,
                "slug": slugify(cat_name),
                "count": count,
            }
        )

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_skills": len(skills),
        "total_categories": len(categories),
        "categories": categories,
        "skills": skills,
    }

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Successfully parsed {len(skills)} skills")
    if errors:
        print(f"Errors/skipped: {errors}")
    print(f"Categories: {len(categories)}")
    for cat in categories:
        print(f"  {cat['name']}: {cat['count']} skills")
    print(f"\nOutput written to: {OUTPUT_PATH}")
    print(f"File size: {OUTPUT_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
