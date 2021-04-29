'''
Created on 17 avr. 2021

@author: messie
'''

import unittest
from imdb_extraction import mise_en_forme_URL

class TestTwitterExtraction(unittest.TestCase):
    
    def test_mise_en_forme_URL(self):
        identifiant1 = '6737010'
        identifiant2 = '1869152'
        identifiant3 = '1640571'
        
        resultat1 = 'https://www.imdb.com/title/tt6737010/reviews?sort=submissionDate&dir=desc&ratingFilter=0'
        resultat2 = 'https://www.imdb.com/title/tt1869152/reviews?sort=submissionDate&dir=desc&ratingFilter=0'
        resultat3 = 'https://www.imdb.com/title/tt1869152/reviews?sort=submissionDate&dir=desc&ratingFilter=0'
        
        self.assertEqual(mise_en_forme_URL(identifiant1), resultat1)
        self.assertEqual(mise_en_forme_URL(identifiant2), resultat2)
        self.assertEqual(mise_en_forme_URL(identifiant3), resultat3)

if __name__ == '__main__':
    unittest.main()