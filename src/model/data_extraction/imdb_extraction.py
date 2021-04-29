#!/usr/bin/env python
# coding: utf-8
'''
@author: messie
'''

from datetime import datetime
import locale
import time

from imdb import IMDb
import selenium

import pandas as pd


def requetes_imdb(requete, driver):
    """ Fonction de traitement des requêtes imdb. """

    requete['colname'] = ["review"]

    # Recherche du film
    if not requete['id']:
        films = film_name_infos(requete['film'][0])
        if not requete['year']:
            film_id = get_film_id(films)
        else:
            film_id = get_film_id(films, requete['year'][0])
        URL = mise_en_forme_URL(film_id)
    else:
        URL = mise_en_forme_URL(requete['id'][0])

    driver.get(URL)
    print("URL : " + URL)

    try:
        if driver.find_element_by_id("load-more-trigger").is_displayed():
            load_more(driver, max_results=requete['maxentries'][0])
    except selenium.common.exceptions.NoSuchElementException:
        raise ValueError("The specified ID doesn't exist in IMDb.")

    # Récupération des données
    dat = driver_extraction_date(driver)
    aut = driver_extraction_auteur(driver)
    com = driver_extraction_commentaire(driver)

    return mise_sous_forme_data_frame(dat, aut, com)


def film_name_infos(name):
    """ Fonction qui récupère les infos d'un film.
    
    Les films récupérés par la fonction search_movie() sont ceux ayant un nom proche de "name".
    """

    ia = IMDb()  # on crée une instance d'imdb
    movies = ia.search_movie(name)

    # on récupère les infos des films trouvés
    identifiant = []
    titre = []
    annee = []

    for movie in movies:
        if name.lower() in movie['title'].lower():  # la boucle est insensible à la casse, mais sensible à l'orthographe
            identifiant.append(movie.movieID)
            titre.append(movie['title'])
            if movie.has_key('year'):
                year = movie['year']
                if year is None:
                    annee.append('')
                else:
                    annee.append(movie['year'])
            else:
                annee.append('')
        # les infos sont mises dans une dataframe
        df = pd.DataFrame(list(zip(identifiant, titre, annee)),
                          columns=['id', 'titre', 'annee'])
        df.annee = df.annee.astype(str)
    return df.sort_values(by=['annee'], ascending=False)  # dataframe triée par ordre de sortie de film, le plus récent en haut


def get_film_id(data, annee=''):
    """ Fonction qui récupère l'identifiant d'un film.
    
    Elle utilise "data", qui est la dataframe créée par la fonction film_name_infos().
    Si la requête indique une année de sortie du film, on choisit ce film. 
    Sinon, par défaut, c'est le film sorti le plus récemment qui sera choisi (premier élément de la dataframe).
    """

    if annee == '':
        return data['id'][0]
    else:
        df = data[data['annee'] == annee]
        return df['id'].values[0]


def mise_en_forme_URL(identifiant):
    """ Fonction qui met en forme une URL.
    
    L'URL formée est celle qui va être donnée au driver de Selenium.
    Pour cela, il faut l'identifiant du film.
    Elle correspond à la page des commentaires d'un film, classés par date.
    """

    if "tt" in identifiant:
        morceau_url_1 = "https://www.imdb.com/title/"
    else:
        morceau_url_1 = "https://www.imdb.com/title/tt"
    morceau_url_2 = "/reviews?sort=submissionDate&dir=desc&ratingFilter=0"
    return morceau_url_1 + identifiant + morceau_url_2


def driver_quit(driver):
    """ Fonction qui permet de quitter le driver. """

    driver.quit()


def load_more(driver, max_results):
    """ Fonction de défilement de la page du driver.
    
    On peut défiler à travers les commentaires d'IMDb via un bouton à cliquer.
    À chaque clic, au moins 1 et au plus 25 commentaires sont affichés en plus sur la page.
    Certains commentaires ne consistant qu'en une notation, 
    et un clic pouvant n'afficher qu'un commentaire en plus,
    le nombre de commentaires recherchés est margé à 30 de plus.
    """

    is_element_present = driver.find_element_by_id("load-more-trigger").is_displayed()  # localisation du bouton clicable
    while is_element_present and (max_results + 30) > 0:
        try:
            button = driver.find_element_by_id("load-more-trigger")  # on trouve le bouton "show more"
            button.click()
            time.sleep(2)
            max_results -= 25
            is_element_present = driver.find_element_by_id("load-more-trigger").is_displayed()
        except Exception:
            raise ValueError("Une erreur est survenue sur la page du driver (scrolling).")
            break


def driver_extraction_date(driver):
    """ Récupération des dates des commentaires sur la page du driver. """

    date_classe = 'review-date'  # nom de la classe des dates dans le code HTML de la page
    date = driver.find_elements_by_class_name(date_classe)
    date_text = []
    for dat in date:
        date_text.append(dat.text)
    date_text = mise_en_forme_date(date_text)
    return date_text


def driver_extraction_auteur(driver):
    """ Récupération des noms d'auteurs sur la page du driver. """

    auteur_classe = 'display-name-link'  # nom de la classe des noms d'auteurs dans le code HTML de la page
    auteur = driver.find_elements_by_class_name(auteur_classe)
    auteur_text = []
    for aut in auteur:
        auteur_text.append(aut.text)
    return auteur_text


def driver_extraction_commentaire(driver):
    """ Récupération des commentaires sur la page du driver. """

    commentaire_classe = 'text.show-more__control'  # nom de la classe des commentaires dans le code HTML de la page
    commentaire = driver.find_elements_by_class_name(commentaire_classe)
    commentaire_text = []
    for com in commentaire:
        commentaire_text.append(com.text)
    return commentaire_text


def mise_en_forme_date(liste):
    """ Fonction qui met la date d'un format "datetime" à un format du type AAAA-MM-JJ."""

    try:
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')  # matching des valeurs temporelles avec celles d'IMDb
    except locale.Error:
        pass

    new_date = []

    try:
        for d in liste:
            d_datetime = datetime.strptime(d, '%d %B %Y').date()
            new_date.append(str(d_datetime))
    except ValueError:
        # in the case an error occurs because the user doesn't have the right default locale
        # or hasn't the 'en_US.utf8' locale installed
        raise AttributeError("The locale installed on your machine does not match the requirements of the " +
                             "program, please install the 'en_US.utf8' locale.")
    return new_date


def mise_sous_forme_data_frame(d, a, t):
    """ Fonction qui met sous forme de dataframe.
    
    Les dates, noms d'auteur et commentaires récoltés sont placés dans une dataframe. """

    data = pd.DataFrame(list(zip(d, a, t)), columns=['date', 'author', 'review'])
    suppression_com_vide(data)
    return data


def suppression_com_vide(data):
    """ Fonction de suppression de lignes dans une dataframe.
    
    Les lignes supprimées sont celles qui concernent les commentaires vides. """

    data['review'].replace('', float("NaN"), inplace=True)
    data.dropna(subset=['review'], inplace=True)
    return data
