from core.metadata import BookInfo, BookScraper


def test_book_scraper_uses_plugins_in_order(monkeypatch):
    scraper = BookScraper(enabled_plugins=["google_books", "audible", "babelio"])

    monkeypatch.setattr(scraper.google_books, "search_google_books", lambda a, t: None)
    monkeypatch.setattr(scraper.audible, "search_audible", lambda a, t: BookInfo(title=t, author=a))
    monkeypatch.setattr(scraper.babelio, "search_babelio", lambda a, t: None)

    result = scraper.search_book("Auteur", "Titre")

    assert result is not None
    assert result.title == "Titre"
    assert scraper.list_plugins() == ["google_books", "audible", "babelio"]


def test_book_scraper_filters_unknown_plugins(monkeypatch):
    scraper = BookScraper(enabled_plugins=["unknown", "babelio"])

    monkeypatch.setattr(scraper.babelio, "search_babelio", lambda a, t: BookInfo(title=t, author=a))

    result = scraper.search_book("Auteur", "Titre")

    assert scraper.list_plugins() == ["babelio"]
    assert result is not None
