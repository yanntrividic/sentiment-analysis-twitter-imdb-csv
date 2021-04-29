#!/usr/bin/env python
# coding: utf-8
'''
@author: messie
'''

import copy
from datetime import datetime
import re
import tweepy
from config import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
import pandas as pd

# Informations de connexion à l'API Twitter
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


# FONCTION principale pour les requêtes
def requetes_twitter(requete):
    """ Fonction de traitement des requêtes concernant Twitter. """
    
    requete['colname'] = ["tweet"]  # On met le nom de la colonne de texte de la dataframe
    recherche = mise_en_forme_recherche(requete)

    " Si la requête ne concerne PAS les tweets d'un utilisateur en particulier "
    if not requete['user']:
        try:
            resultat_recherche = recherche_twitter(recherche,
                                                   langue=requete['lang'][0],
                                                   nombre_tweets=requete['maxentries'][0])
    
        except tweepy.error.RateLimitError:
            raise ValueError("Your request could not be completed as you have reached your API credits limit. " +
                             "Please come back later.")
    else: # on fait une recherche par utilisateur
        try:
            resultat_recherche = recherche_twitter_user(requete['user'][0],
                                                   langue=requete['lang'][0],
                                                   nombre_tweets=requete['maxentries'][0])
    
        except tweepy.error.RateLimitError:
            raise ValueError("Your request could not be completed as you have reached your API credits limit. " +
                             "Please come back later.")

    # On récupère les données via la recherche faite précédemment
    d, aut, t = extraction_twitter(resultat_recherche)
    
    # Nettoyage des données
    dat = mise_en_forme_date(d)
    tex = nettoyage_texte(t, symbole=False, mention=False, lien=True)
    
    # Création de la dataframe de données
    data = mise_sous_forme_data_frame(dat, aut, tex, requete['lang'][0], requete['maxentries'][0])
    " Si la recherche est ciblée utilisateur, suppression des tweets non demandés :"
    if requete['user']:
        data = tweet_contain_hashtag(data, requete['hashtag'])
        data = tweet_contain_search(data, requete['search'])
    if not data.empty:
        return data
    else:
        raise ValueError("Your Twitter search didn't result in the extraction of any tweets.")


def mise_en_forme_recherche(recherche):
    """ Fonction qui forme la recherche destinée à l'API. """
    
    rech = ''
    for h in recherche['hashtag']:
        rech = rech + h + ' '
    for s in recherche['search']:
        rech = rech + s + ' '
    return rech + '-filter:retweets' # le filtre sert à ne pas extraire les retweets


def recherche_twitter(recherche, langue="en", nombre_tweets=500):
    """ Fonction qui lance la recherche sur l'API. """
    
    tweets = tweepy.Cursor(api.search,  # notre session d'api
                           q=recherche,  # la recherche twitter
                           lang=langue,
                           tweet_mode='extended',  # pour avoir tout le texte du tweet
                           # since=date_debut, until=date_fin
                           ).items(nombre_tweets)
    return tweets  # on a le résultat de la recherche


def recherche_twitter_user(username, langue="en", nombre_tweets=500):
    """ Fonction qui lance la recherche ciblée utilisateur sur l'API. """
    
    tweets = tweepy.Cursor(api.user_timeline,
                           id=username,
                           lang=langue,
                           tweet_mode='extended',
                           # since=date_debut, until=date_fin
                           ).items(nombre_tweets)
    return tweets


def extraction_twitter(resultat_recherche):
    """ Fonction qui extrait les données de la recherche faite via l'API. """
    
    date = []
    aut = []
    text = []
    for tweet in resultat_recherche:
        date.append(tweet.created_at)  # la date du tweet
        aut.append(tweet.user.screen_name)  # le nom de l'auteur
        text.append(tweet.full_text)  # le texte du tweet
    return date, aut, text


def mise_en_forme_date(liste):
    """ Fonction qui met la date d'un format "datetime" à un format du type AAAA-MM-JJ."""
    
    dat = copy.deepcopy(liste)
    new_date = []
    for d in dat:
        new_date.append(datetime.strftime(d, '%Y-%m-%d'))
    return new_date


def supp_symbole_string(string):
    """ Fonction de suppression des émojis dans un texte. 
    
    SOURCE: https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python. """
    
    return string.encode('ascii', 'ignore').decode('ascii')

def supp_symbole_liste(liste):
    """ Fonction de suppression des émojis dans une liste. """
    
    return [supp_symbole_string(li) for li in liste]


def supp_mention_string(string):
    """ Fonction de suppression des mentions de personnes dans un texte. """
    
    return re.sub("(#[A-Za-z0-9]+)|(@[A-Za-z0-9]+)|(_[A-Za-z0-9]+)", "", string)

def supp_mention_liste(liste):
    """ Fonction de suppression des mentions de personnes dans une liste. """
    
    return [supp_mention_string(li) for li in liste]


def supp_lien_string(string):
    """ Fonction de suppression des liens dans un texte. """
    
    return re.sub(r'http\S+', '', string)

def supp_lien_liste(liste):
    """ Fonction de suppression des liens dans une liste. """
    
    return [supp_lien_string(li) for li in liste]


def supp_espace_string(string):
    """ Fonction de suppression des espaces superflus dans un texte. """
    
    return re.sub('( +)|(\n+)', ' ', string)

def supp_espace_liste(liste):
    """ Fonction de suppression des espaces superflus dans une liste. """
    
    return [supp_espace_string(li) for li in liste]


def nettoyage_texte(liste, symbole=False, mention=False, lien=True):
    """ Fonction qui nettoie un texte.
    
    Le texte peut être nettoyé des symboles, mentions et liens. Ces nettoyages sont modulables.
    symbole = True : les symboles sont gardés.
    """
    
    if symbole:
        liste = supp_symbole_liste(liste)
    if mention:
        liste = supp_mention_liste(liste)
    if lien:
        liste = supp_lien_liste(liste)
    liste = supp_espace_liste(liste) # les espaces en trop sont forcément retirés
    return liste


def tweet_contain_hashtag(data, hashtags):
    """ Fonction qui sélectionne les lignes d'une dataframe.
    
    Les lignes sélectionnées sont celles des tweets contenant les hashtags demandés.
    """
    
    contain_values = data
    for hashtag in hashtags :
        contain_values = contain_values[contain_values['tweet'].str.contains(hashtag, case=False)]
    return contain_values


def tweet_contain_search(data, searchs):
    """ Fonction qui sélectionne les lignes d'une dataframe.
    
    Les lignes sélectionnées sont celles des tweets contenant les mots-clés demandés.
    """
    
    contain_values = data
    for search in searchs :
        contain_values = contain_values[contain_values['tweet'].str.contains(search, case=False)]
    return contain_values


def mise_sous_forme_data_frame(d, a, t, lang="", nb_tweets=0):
    """ Fonction qui met les données récoltées sous forme de dataframe. """
    
    if lang == "":
        lang = "en"
        
    df = pd.DataFrame(list(zip(d, a, t)), columns = ['date', 'author', 'tweet'])
    df['src_lang'] = "en"
    
    if not nb_tweets == "":
        df = df.head(int(nb_tweets))
        
    return suppression_tweet_vide(df)


def suppression_tweet_vide(data):
    """ Fonction de suppression de lignes dans une dataframe.
    
    Les lignes supprimées sont celles qui concernent les tweets vides. 
    Par exemple : un tweet qui ne contient qu'un lien, qui est ensuite supprimé devient vide.
    """
    
    data['tweet'].replace('', float("NaN"), inplace=True)
    data.dropna(subset=['tweet'], inplace=True)
    return data