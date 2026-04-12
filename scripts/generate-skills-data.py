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

    return {
        "name": name,
        "slug": slugify(name),
        "category": category,
        "category_slug": slugify(category),
        "dir_name": skill_dir_name,
        "description": description,
        "version": version,
        "author": author,
        "license": license_val,
        "tags": tags,
        "related_skills": related_skills,
        "prerequisites": prerequisites if isinstance(prerequisites, dict) else {},
        "content": body,
        "reading_time_minutes": reading_time,
        "line_count": line_count,
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
