#!/usr/bin/env python3
"""Generate individual skill zip files for download from the marketplace."""

import os
import json
import zipfile
import argparse

SKILLS_DIR = os.path.expanduser("~/.hermes/skills")
OUTPUT_DIR = None  # set via args


def get_skill_files(skill_dir):
    """Get all files in a skill directory recursively."""
    files = []
    for root, dirs, filenames in os.walk(skill_dir):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for fname in filenames:
            if fname.startswith('.') or fname.endswith('.pyc'):
                continue
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, skill_dir)
            files.append((full_path, rel_path))
    return files


def create_skill_zip(skill_name, category, output_dir):
    """Create a zip file for a single skill."""
    skill_dir = os.path.join(SKILLS_DIR, category, skill_name)
    if not os.path.isdir(skill_dir):
        return None

    files = get_skill_files(skill_dir)
    if not files:
        return None

    zip_filename = f"{skill_name}.zip"
    zip_path = os.path.join(output_dir, zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Put files under skill-name/ directory in the zip
        for full_path, rel_path in files:
            arcname = os.path.join(skill_name, rel_path)
            zf.write(full_path, arcname)

        # Add a README if SKILL.md exists
        skillmd_path = os.path.join(skill_dir, 'SKILL.md')
        if os.path.exists(skillmd_path) and 'SKILL.md' not in [r for _, r in files]:
            zf.write(skillmd_path, os.path.join(skill_name, 'SKILL.md'))

    size = os.path.getsize(zip_path)
    return {
        "filename": zip_filename,
        "size_bytes": size,
        "size_human": f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB",
        "file_count": len(files)
    }


def main():
    parser = argparse.ArgumentParser(description="Generate skill zip files for download")
    parser.add_argument("--output", "-o", required=True, help="Output directory for zip files")
    parser.add_argument("--data", "-d", required=True, help="Path to skills.json")
    args = parser.parse_args()

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    # Load skills data
    with open(args.data) as f:
        data = json.load(f)

    # Generate zips
    download_info = {}
    for skill in data["skills"]:
        info = create_skill_zip(skill["name"], skill["category"], output_dir)
        if info:
            download_info[skill["slug"]] = info

    # Write download manifest
    manifest_path = os.path.join(output_dir, "downloads.json")
    with open(manifest_path, 'w') as f:
        json.dump(download_info, f, indent=2)

    print(f"Generated {len(download_info)} zip files")
    print(f"Manifest: {manifest_path}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
