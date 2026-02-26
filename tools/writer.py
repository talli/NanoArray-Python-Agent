import os
import re
from datetime import datetime
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
FINDINGS_DIR = BASE_DIR / "findings"
SOURCES_DIR = BASE_DIR / "sources"
SUMMARIES_DIR = BASE_DIR / "summaries"

# Ensure directories exist
for d in [FINDINGS_DIR, SOURCES_DIR, SUMMARIES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def _sanitize_filename(slug: str) -> str:
    """Creates a URL-friendly and path-safe slug."""
    slug = slug.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")

def write_markdown_artifact(folder: str, topic_slug: str, content: str, status: str = "draft") -> str:
    """
    Writes content to a markdown file with consistent YAML frontmatter according to CLAUDE.md standards.
    folder: 'findings', 'sources', or 'summaries'
    topic_slug: Short descriptive name (e.g., 'dna-origami-placement')
    content: The markdown payload
    status: 'draft', 'reviewed', or 'final'
    """
    if folder not in ["findings", "sources", "summaries"]:
        raise ValueError("Folder must be one of: findings, sources, summaries")
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    clean_slug = _sanitize_filename(topic_slug)
    
    # Format according to CLAUDE.md File Naming Convention
    if folder == "sources":
        filename = f"{date_str}_bibliography-{clean_slug}.md"
    elif folder == "summaries":
        filename = f"{date_str}_summary-{clean_slug}.md"
    else:
        filename = f"{date_str}_{clean_slug}.md"
        
    target_path = BASE_DIR / folder / filename
    
    # Check if we are updating an existing file to preserve creation date
    date_created = date_str
    if target_path.exists():
        with open(target_path, "r") as f:
            first_lines = f.readlines()[:10]
            for line in first_lines:
                if line.startswith("date_created:"):
                    date_created = line.split(":", 1)[1].strip()
                    break

    frontmatter = f"""---
topic: {topic_slug.replace('-', ' ').title()}
date_created: {date_created}
last_updated: {date_str}
status: {status}
---

"""
    
    full_content = frontmatter + content.strip() + "\n"
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    return str(target_path)
