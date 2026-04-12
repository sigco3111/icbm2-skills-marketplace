#!/bin/bash
# sync-skills-to-marketplace.sh
# 스킬 변경을 감지하고 GitHub Pages 사이트를 업데이트합니다

REPO_DIR="/Users/hjshin/Desktop/project/work/icbm2-skills-marketplace"
SKILLS_DIR="$HOME/.hermes/skills"
HASH_FILE="$HOME/.hermes/data/skills-sync-hash.txt"

# 1. 스킬 디렉토리 해시 계산
CURRENT_HASH=$(find "$SKILLS_DIR" -name "SKILL.md" -exec md5 {} + 2>/dev/null | md5)

# 2. 이전 해시와 비교
if [ -f "$HASH_FILE" ]; then
    PREV_HASH=$(cat "$HASH_FILE")
    if [ "$CURRENT_HASH" = "$PREV_HASH" ]; then
        echo "NO_CHANGE: Skills unchanged since last sync"
        exit 0
    fi
fi

# 3. 변경 감지 → 데이터 재생성 & 배포
echo "CHANGE_DETECTED: Regenerating skills data..."
cd "$REPO_DIR"

python3 scripts/generate-skills-data.py
node scripts/copy-data.mjs
python3 scripts/generate-skill-zips.py -o public/downloads -d src/data/skills.json

git add src/data/skills.json public/skills-data.json public/downloads/
CHANGES=$(git diff --cached --stat)

if [ -z "$CHANGES" ]; then
    echo "NO_CHANGE: Data unchanged after regeneration"
    echo "$CURRENT_HASH" > "$HASH_FILE"
    exit 0
fi

git commit -m "🔄 Auto-sync: Update skills data ($(date +%Y-%m-%d\ %H:%M))"
git push origin main

echo "$CURRENT_HASH" > "$HASH_FILE"
echo "SYNC_COMPLETE: Pushed to GitHub Pages"
