# 🛒 ICBM2 Skills Marketplace

ICBM2 에이전트가 축적한 스킬(Skill)들을 웹에서 탐색하고 검색할 수 있는 마켓플레이스입니다. `~/.hermes/skills/` 디렉토리의 SKILL.md 파일을 자동 파싱하여 카테고리별로 분류하고, 상세 정보를 제공합니다.

> 🤖 ICBM2가 자동 생성/관리하는 프로젝트입니다.

🔗 **Live:** [https://sigco3111.github.io/icbm2-skills-marketplace/](https://sigco3111.github.io/icbm2-skills-marketplace/)

## ✨ 기능

- 113개+ AI 에이전트 스킬 카탈로그
- 24개 카테고리 분류
- 한국어/영어 설명 토글 지원 (카드별)
- 실시간 검색 (Ctrl+K)
- 다중 정렬 (기본 / 이름 A→Z / 이름 Z→A / 최신순 / 오래된순)
- 스킬 상세 페이지 (전문 내용, 관련 스킬, 다운로드)
- 카테고리별 필터링
- 스킬 ZIP 다운로드
- 반응형 다크 테마 디자인
- GitHub Pages 자동 배포

## 📂 카테고리

| 카테고리 | 스킬 수 | 카테고리 | 스킬 수 |
|----------|--------|----------|--------|
| automation | 28 | autonomous-ai-agents | 5 |
| mlops | 22 | research | 5 |
| creative | 8 | apple | 4 |
| github | 6 | media | 4 |
| productivity | 6 | openclaw-imports | 3 |
| software-development | 6 | 기타 15개 카테고리 | 17 |

## 📁 프로젝트 구조

```text
/
├── public/
│   ├── downloads/          # 스킬 ZIP 파일 (자동 생성)
│   │   ├── downloads.json  # 다운로드 매니페스트
│   │   └── *.zip           # 스킬 아카이브
│   ├── skills-data.json    # 검색용 공개 데이터
│   └── favicon.svg
├── src/
│   ├── components/         # UI 컴포넌트
│   │   ├── CategoryFilter.astro
│   │   ├── Header.astro
│   │   ├── SearchBar.astro
│   │   └── SkillCard.astro
│   ├── data/               # 스킬 데이터 (자동 생성)
│   │   ├── skills.json     # 전체 스킬 데이터
│   │   └── downloads.json  # 다운로드 매니페스트 (복사본)
│   ├── layouts/
│   │   └── Layout.astro    # 공통 레이아웃
│   ├── pages/
│   │   ├── index.astro             # 메인 페이지
│   │   ├── 404.astro               # 404 페이지
│   │   ├── skills/[slug].astro     # 스킬 상세 페이지
│   │   └── category/[slug].astro   # 카테고리 페이지
│   └── styles/
│       └── global.css      # Tailwind CSS
├── scripts/
│   ├── generate-skills-data.py   # SKILL.md 파싱 → skills.json
│   ├── generate-skill-zips.py    # 스킬 → ZIP 아카이브
│   ├── copy-data.mjs             # 데이터 파일 복사
│   └── sync-skills.sh            # 전체 동기화 스크립트
├── astro.config.mjs
├── tailwind.config.mjs
└── package.json
```

## 🧞 명령어

| 명령어 | 설명 |
| :--- | :--- |
| `npm install` | 의존성 설치 |
| `npm run dev` | 로컬 개발 서버 (`localhost:4321`) |
| `npm run build` | 프로덕션 빌드 (`./dist/`) |
| `npm run preview` | 배포 전 로컬 미리보기 |

### 스킬 데이터 갱신

```bash
# 1. SKILL.md 파싱 → skills.json 생성
python3 scripts/generate-skills-data.py

# 2. 스킬 ZIP 아카이브 생성
python3 scripts/generate-skill-zips.py

# 3. 다운로드 매니페스트 동기화 (public → src)
node scripts/copy-data.mjs

# 4. 공개 검색 데이터 업데이트 (빌드 시 자동 처리)
npm run build

# 전체 한 번에 실행
bash scripts/sync-skills.sh
```

## 🚀 기술 스택

- **Astro 5** — 정적 사이트 생성 프레임워크
- **Tailwind CSS v4** — 유틸리티 퍼스트 CSS
- **TypeScript** — 타입 안전한 개발
- **GitHub Pages** — 자동 배포 (GitHub Actions)
- **Playwright** — 브라우저 자동 테스트

## 📦 배포

`main` 브랜치에 push하면 GitHub Actions가 자동으로 빌드 후 GitHub Pages에 배포합니다.

## 📝 데이터 스키마

`skills.json`의 각 스킬 항목:

```json
{
  "name": "스킬 이름",
  "slug": "skill-slug",
  "category": "카테고리명",
  "category_slug": "category-slug",
  "description": "기본 설명 (한국어 우선)",
  "description_ko": "한국어 설명",
  "description_en": "영어 설명",
  "version": "1.0.0",
  "author": "ICBM2",
  "tags": ["tag1", "tag2"],
  "reading_time_minutes": 5,
  "line_count": 120,
  "created_at": 1775990343
}
```

## 👀 더 알아보기

- [Astro 문서](https://docs.astro.build)
- [Tailwind CSS v4 문서](https://tailwindcss.com/docs)
