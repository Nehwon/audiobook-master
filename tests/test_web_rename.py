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

    def test_author_at_end(self):
        folder = "Machiavel, L’art de l’Etat - Julien Le Mauff"
        self.assertEqual(
            _smart_rename(folder),
            "Julien Le Mauff - Machiavel, L’art de l’Etat",
        )

    def test_encoding_and_volume_cleanup(self):
        folder = "Michael Anderle - Le gambit kurthÃ©rien - Vol 1 - Morte et mortelle"
        self.assertEqual(
            _smart_rename(folder),
            "Michael Anderle - Le gambit kurthérien - Vol 1 - Morte et mortelle",
        )

    def test_remove_non_essential_tags(self):
        folder = "Mo Hayder - Crâne dOs MP3 128Kbps"
        self.assertEqual(_smart_rename(folder), "Mo Hayder - Crâne d'Os")

    def test_numeric_series_block(self):
        folder = "Tempest Auburn et Michael Anderle - 2 - Le bosquet sacré"
        self.assertEqual(
            _smart_rename(folder),
            "Tempest Auburn et Michael Anderle - Vol 2 - Le bosquet sacré",
        )


if __name__ == "__main__":
    unittest.main()
