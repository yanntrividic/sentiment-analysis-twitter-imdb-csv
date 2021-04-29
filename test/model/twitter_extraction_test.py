'''
Created on Mar 17, 2021

@author: messie
'''

import unittest
from datetime import datetime
from twitter_extraction import mise_en_forme_recherche, mise_en_forme_date,\
    supp_mention_liste, supp_lien_liste, supp_espace_liste

class TestTwitterExtraction(unittest.TestCase):
    
    def test_mise_en_forme_recherche(self):
        requete1 = {'hashtag': ['covid'], 'search': ['2021']}
        requete2 = {'hashtag': ['covid', 'france'], 'search': ['2021']}
        requete3 = {'hashtag': ['covid'], 'search': ['2021', 'deces']}
        requete4 = {'hashtag': ['covid', 'france'], 'search': ['2021', 'deces']}
        
        self.assertEqual(mise_en_forme_recherche(requete1), "covid 2021 -filter:retweets")
        self.assertEqual(mise_en_forme_recherche(requete2), "covid france 2021 -filter:retweets")
        self.assertEqual(mise_en_forme_recherche(requete3), "covid 2021 deces -filter:retweets")
        self.assertEqual(mise_en_forme_recherche(requete4), "covid france 2021 deces -filter:retweets")
     
    def test_mise_en_forme_date(self):
        date1 = [datetime(2021, 4, 17, 5, 46, 56)]
        date2 = [datetime(2021, 4, 17, 4, 51, 9), datetime(2021, 4, 17, 4, 46, 34)]
        date3 = [datetime(2021, 4, 17, 4, 51, 9), datetime(2021, 4, 17, 4, 46, 34), datetime(2021, 4, 17, 4, 16, 45)]
        
        resultat_date1 = ['2021-04-17']
        resultat_date2 = ['2021-04-17', '2021-04-17']
        resultat_date3 = ['2021-04-17', '2021-04-17', '2021-04-17']
        
        self.assertEqual(mise_en_forme_date(date1),resultat_date1)
        self.assertEqual(mise_en_forme_date(date1),resultat_date2)
        self.assertEqual(mise_en_forme_date(date1),resultat_date3)
        
    def test_supp_mention_liste(self):
        liste = ["Lorem @ipsum dolor sit amet", 
                  "consectetur @@adipiscing elit", 
                  "sed do \@eiusmod tempor incididunt ut", 
                  "labore et @dolore magna@ aliqua."]
        
        resultat = ['Lorem  dolor sit amet',
                          'consectetur @ elit',
                          'sed do \\ tempor incididunt ut',
                          'labore et  magna@ aliqua.']
        
        self.assertEqual(supp_mention_liste(liste), resultat)
        
    def test_supp_lien_liste(self):
        liste = ['https://www.imdb.com/ movies !!!',
                 'https://twitter.com/home is Twitter\'s website']
        
        resultat = [' movies !!!', " is Twitter's website"]
        
        self.assetEqual(supp_lien_liste(liste), resultat)
        
    def test_supp_espace_liste(self):
        liste = ["Lorem ipsum dolor      sit amet", 
                  "consectetur     adipiscing     elit", 
                  "    sed  do  eiusmod   tempor  incididunt   ut     "]
        
        resultat = ['Lorem ipsum dolor sit amet', 
                    'consectetur adipiscing elit', 
                    ' sed do eiusmod tempor incididunt ut ']
        
        self.assertEqual(supp_espace_liste(liste), resultat)
     
if __name__ == '__main__':
    unittest.main()