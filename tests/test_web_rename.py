import unittest

from web.app import _smart_rename


class TestWebRename(unittest.TestCase):
    def test_book_only_format(self):
        folder = "Cécile Cabanac - La petite ritournelle de l_horreur"
        self.assertEqual(
            _smart_rename(folder),
            "Cécile Cabanac - La petite ritournelle de l'horreur",
        )

    def test_series_format(self):
        folder = "Glen+Cook+-+Les+Annales+de+la+Compagnie+noire+3+-+La+Rose+Blanche"
        self.assertEqual(
            _smart_rename(folder),
            "Glen Cook - Les Annales de la Compagnie noire - Vol 3 - La Rose Blanche",
        )


if __name__ == "__main__":
    unittest.main()
