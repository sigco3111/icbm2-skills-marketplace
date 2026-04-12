# 🛒 ICBM2 Skills Marketplace

ICBM2 에이전트가 축적한 스킬(Skill)들을 웹에서 탐색하고 검색할 수 있는 마켓플레이스입니다. SKILL.md 파일을 자동 파싱하여 카테고리별로 분류하고, 상세 정보를 제공합니다.

> 🤖 ICBM2가 자동 생성/관리하는 프로젝트입니다.

## 📁 프로젝트 구조

```text
/
├── public/
├── src/
│   ├── components/   # UI 컴포넌트
│   ├── data/         # 스킬 데이터 (자동 생성)
│   ├── layouts/      # 페이지 레이아웃
│   └── pages/        # 라우트 페이지
│       └── index.astro
├── scripts/          # 스킬 데이터 수집 스크립트
├── package.json
└── astro.config.mjs
```

## 🧞 명령어

모든 명령어는 프로젝트 루트에서 실행합니다:

| 명령어 | 설명 |
| :--- | :--- |
| `npm install` | 의존성 설치 |
| `npm run dev` | 로컬 개발 서버 실행 (`localhost:4321`) |
| `npm run build` | 프로덕션 빌드 (`./dist/` 출력) |
| `npm run preview` | 배포 전 로컬 미리보기 |
| `npm run collect` | 스킬 데이터 수집 (GitHub API) |

## 🚀 기술 스택

- **Astro** — 정적 사이트 생성 프레임워크
- **TypeScript** — 타입 안전한 개발
- **GitHub API** — 스킬 데이터 수집
- **GitHub Pages** — 자동 배포

## 📦 배포

GitHub Actions를 통해 `main` 브랜치에 push되면 자동으로 GitHub Pages에 배포됩니다.

## 👀 더 알아보기

- [Astro 문서](https://docs.astro.build)
- [Astro Discord](https://astro.build/chat)
