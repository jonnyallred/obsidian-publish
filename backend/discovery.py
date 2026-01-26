import re
from pathlib import Path
from typing import Dict, List, Set


def find_orphaned_pages(content_dir: str = None) -> List[str]:
    """
    Find published pages with no incoming backlinks

    Analyzes all markdown files in the content directory, finds [[wikilinks]],
    and identifies pages that have no other pages linking to them.

    Args:
        content_dir: Path to content directory (defaults to ../content)

    Returns:
        List of orphaned page paths relative to content_dir
    """
    if content_dir is None:
        # Find content dir relative to backend directory
        backend_dir = Path(__file__).parent
        content_dir = backend_dir.parent / 'content'
    else:
        content_dir = Path(content_dir)

    if not content_dir.exists():
        return []

    # Find all published markdown files
    published_pages = []
    page_titles = {}  # Map title to file path

    for md_file in content_dir.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Check if published
                if 'publish: true' not in content:
                    continue

                published_pages.append(md_file)

                # Extract title from frontmatter or filename
                title_match = re.search(r'title:\s*([^\n]+)', content)
                if title_match:
                    title = title_match.group(1).strip()
                    page_titles[title] = md_file
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue

    # Build backlink graph
    backlinks: Dict[Path, Set[Path]] = {page: set() for page in published_pages}

    for page in published_pages:
        try:
            with open(page, 'r', encoding='utf-8') as f:
                content = f.read()

                # Find all [[wikilinks]]
                wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)

                for link in wikilinks:
                    # Extract just the page name (remove anchors)
                    page_name = link.split('#')[0].strip()

                    # Try to find the target page
                    # First try exact title match
                    target = None
                    if page_name in page_titles:
                        target = page_titles[page_name]
                    else:
                        # Try to find by filename (case-insensitive)
                        for published_page in published_pages:
                            page_stem = published_page.stem
                            if page_name.lower() == page_stem.lower():
                                target = published_page
                                break

                    if target and target != page:
                        backlinks[target].add(page)
        except Exception as e:
            print(f"Error processing backlinks for {page}: {e}")
            continue

    # Find orphans (pages with no backlinks)
    orphans = []
    for page in published_pages:
        # Home page is never considered orphaned
        if page.name == 'index.md':
            continue

        # Check if page has no backlinks
        if not backlinks[page]:
            # Get relative path
            rel_path = page.relative_to(content_dir)
            orphans.append(str(rel_path))

    return sorted(orphans)


def get_page_metadata(content_dir: str = None) -> Dict[str, dict]:
    """
    Get metadata for all published pages

    Args:
        content_dir: Path to content directory

    Returns:
        Dict mapping page path to metadata (title, tags, date)
    """
    if content_dir is None:
        backend_dir = Path(__file__).parent
        content_dir = backend_dir.parent / 'content'
    else:
        content_dir = Path(content_dir)

    metadata = {}

    for md_file in content_dir.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Check if published
                if 'publish: true' not in content:
                    continue

                # Extract metadata
                title_match = re.search(r'title:\s*([^\n]+)', content)
                title = title_match.group(1).strip() if title_match else md_file.stem

                tags_match = re.search(r'tags:\s*\[(.*?)\]', content, re.DOTALL)
                tags = []
                if tags_match:
                    tags_str = tags_match.group(1)
                    tags = [t.strip().strip('"\'') for t in tags_str.split(',')]

                date_match = re.search(r'date:\s*([^\n]+)', content)
                date = date_match.group(1).strip() if date_match else None

                rel_path = str(md_file.relative_to(content_dir))
                metadata[rel_path] = {
                    'title': title,
                    'tags': tags,
                    'date': date,
                }
        except Exception as e:
            print(f"Error extracting metadata from {md_file}: {e}")
            continue

    return metadata


if __name__ == '__main__':
    # Test the discovery functions
    orphans = find_orphaned_pages()
    print(f"Found {len(orphans)} orphaned pages:")
    for orphan in orphans:
        print(f"  - {orphan}")

    print("\nPage metadata:")
    metadata = get_page_metadata()
    for page, data in metadata.items():
        print(f"  {page}: {data}")
