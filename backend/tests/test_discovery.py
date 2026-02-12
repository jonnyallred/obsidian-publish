from discovery import find_orphaned_pages, get_page_metadata


class TestFindOrphanedPages:
    def test_finds_orphan(self, content_dir):
        orphans = find_orphaned_pages(str(content_dir))
        assert "orphan.md" in orphans

    def test_linked_page_not_orphan(self, content_dir):
        orphans = find_orphaned_pages(str(content_dir))
        assert "page-b.md" not in orphans

    def test_index_excluded(self, content_dir):
        orphans = find_orphaned_pages(str(content_dir))
        assert "index.md" not in orphans

    def test_unpublished_excluded(self, content_dir):
        orphans = find_orphaned_pages(str(content_dir))
        assert "draft.md" not in orphans

    def test_all_linked_returns_fewer_orphans(self, content_dir):
        # Link to orphan from page-a
        page_a = content_dir / "page-a.md"
        page_a.write_text(
            "---\ntitle: Page A\npublish: true\n---\n"
            "Links to [[Page B]] and [[Orphan Page]].\n"
        )
        orphans = find_orphaned_pages(str(content_dir))
        assert "orphan.md" not in orphans

    def test_empty_dir(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()
        assert find_orphaned_pages(str(d)) == []

    def test_nonexistent_dir(self, tmp_path):
        assert find_orphaned_pages(str(tmp_path / "nope")) == []


class TestWikilinkMatching:
    def test_match_by_title(self, content_dir):
        # page-a links to [[Page B]] by title — page-b should not be orphan
        orphans = find_orphaned_pages(str(content_dir))
        assert "page-b.md" not in orphans

    def test_match_by_filename(self, content_dir):
        # Change link to use filename instead of title
        page_a = content_dir / "page-a.md"
        page_a.write_text(
            "---\ntitle: Page A\npublish: true\n---\n"
            "Link to [[page-b]].\n"
        )
        orphans = find_orphaned_pages(str(content_dir))
        assert "page-b.md" not in orphans

    def test_anchor_stripped(self, content_dir):
        # Link with anchor should still resolve
        page_a = content_dir / "page-a.md"
        page_a.write_text(
            "---\ntitle: Page A\npublish: true\n---\n"
            "Link to [[Page B#section]].\n"
        )
        orphans = find_orphaned_pages(str(content_dir))
        assert "page-b.md" not in orphans


class TestGetPageMetadata:
    def test_extracts_title_tags_date(self, content_dir):
        meta = get_page_metadata(str(content_dir))
        assert "page-a.md" in meta
        assert meta["page-a.md"]["title"] == "Page A"
        assert "foo" in meta["page-a.md"]["tags"]
        assert meta["page-a.md"]["date"] == "2024-01-01"

    def test_excludes_unpublished(self, content_dir):
        meta = get_page_metadata(str(content_dir))
        assert "draft.md" not in meta

    def test_handles_missing_fields(self, content_dir):
        # page-b has no tags or date
        meta = get_page_metadata(str(content_dir))
        assert "page-b.md" in meta
        assert meta["page-b.md"]["tags"] == []
        assert meta["page-b.md"]["date"] is None

    def test_nonexistent_dir(self, tmp_path):
        # get_page_metadata with nonexistent dir — should return empty
        # The function iterates .rglob on the path; if it doesn't exist it will
        # raise or return empty depending on implementation
        meta = get_page_metadata(str(tmp_path / "nope"))
        assert meta == {}
