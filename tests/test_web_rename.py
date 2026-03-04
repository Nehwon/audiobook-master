import unittest

from web.app import _smart_rename


class TestWebRename(unittest.TestCase):
    def test_book_only_format(self):
        folder = "Cécile Cabanac - La petite ritournelle de l_horreur"
        renamed = _smart_rename(folder)
        self.assertEqual(
            renamed,
            "Cécile Cabanac - La petite ritournelle de l’horreur",
        )
        self.assertNotIn("'", renamed)

    def test_series_format(self):
        folder = "Glen+Cook+-+Les+Annales+de+la+Compagnie+noire+3+-+La+Rose+Blanche"
        self.assertEqual(
            _smart_rename(folder),
            "Glen Cook - Les Annales de la Compagnie noire - Vol 3 - La Rose Blanche",
        )

    def test_existing_ascii_apostrophe_is_normalized(self):
        folder = "L'auteur - L'histoire"
        renamed = _smart_rename(folder)
        self.assertEqual(renamed, "L’auteur - L’histoire")
        self.assertNotIn("'", renamed)


if __name__ == "__main__":
    unittest.main()
