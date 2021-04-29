'''
Created on Apr 07, 2021

@author: Johan
'''

from os.path import sep

from main_window import IMG_PATH
from table_model import POS_ROW_COLOR, NEG_ROW_COLOR, NEU_ROW_COLOR
import matplotlib.pyplot as plt
# from wordcloud import WordCloud

WORDCLOUD_PNG_PATH = IMG_PATH + sep + "wordcloud.png"

DARKER_POS_ROW_COLOR = "#419542"
DARKER_NEG_ROW_COLOR = "#d37d2d"
DARKER_NEU_ROW_COLOR = "#868788"


def graph_convert(data):
    '''
    Convert dataframes into graphs
    '''

    source = data.interpreted_request['src'][0]
    if source == 'imdb':
        source = 'IMDb'
    elif source == 'twitter':
        source = 'Twitter'
    elif source == 'local':
        source = "your CSV file"

    condensed_interpreted_request = data.get_comprehensive_request_summary()

    plots_title = "Data analysis for the \"" + condensed_interpreted_request + "\" search on " + source

    # print(data.get_polarity_data())  #  extracts the polarity data
    colors = [POS_ROW_COLOR, NEG_ROW_COLOR, NEU_ROW_COLOR]
    # setting up values for pie chart
    pos = 0
    neg = 0
    neu = 0
    for i in range(0, len(data.get_polarity_data())):  # get values for each polarity to fill the pie graph
        if(data.get_polarity_data()[i] == 'pos'):
            pos = pos + 1
        if(data.get_polarity_data()[i] == 'neg'):
            neg = neg + 1
        if(data.get_polarity_data()[i] == 'neu'):
            neu = neu + 1
    # values for pie chart
    labels = ['Positive', 'Negative', 'Neutral']
    effectif = [pos, neg, neu]

    # values to draw bar plot for most common words
    #  @Johan: FIXME : if the number of extracted words is less that 10 the program crashes on line 48
    #  IndexError: list index out of range
    vals = data.statistics['word_frequencies'].most_common(10)
    names_stats = []
    values_stats = []
    for i in range(0, 10):  # get inputs for bar plot
        names_stats.append(vals[9 - i][0])
        values_stats.append(vals[9 - i][1])

    # setting up all values for ax2 graph wich will draw either polarity per day/month/year depends on wich is closer to 10 values,
    # because we considere that 10 values is the most representative number of values for this graph

    posi = []
    negati = []
    neutri = []
    stats_per_day = []
    stats_per_month = []
    stats_per_year = []
    N = 10
    N_day = abs(N - len(list(data.statistics['pol_data_per_day'].keys())))
    N_month = abs(N - len(list(data.statistics['pol_data_per_month'].keys())))
    N_year = abs(N - len(list(data.statistics['pol_data_per_year'].keys())))
    # setting up booleans to know wich draw is gonna be the good one
    b_day = False
    b_month = False
    b_year = False

    names_per_day = list(data.statistics['pol_data_per_day'].keys())
    names_per_month = list(data.statistics['pol_data_per_month'].keys())
    names_per_year = list(data.statistics['pol_data_per_year'].keys())

    # selecting the case for day/month/year and fill the values into lists
    if min(N_day, N_month, N_year) == N_day:
        names_per_day.reverse()
        stats_per_day = list(data.statistics['pol_data_per_day'].values())
        for i in range(0, len(stats_per_day)):
            posi.append((stats_per_day[len(stats_per_day) - i - 1][0][1] + 0.2))
            neutri.append((stats_per_day[len(stats_per_day) - i - 1][1][1] + 0.1))
            negati.append(stats_per_day[len(stats_per_day) - i - 1][2][1])
            b_day = True

    elif min(N_day, N_month, N_year) == N_month:
        names_per_month.reverse()
        stats_per_month = list(data.statistics['pol_data_per_month'].values())
        for i in range(0, len(stats_per_month)):
            posi.append((stats_per_month[len(stats_per_month) - i - 1][0][1] + 0.2))
            neutri.append((stats_per_month[len(stats_per_month) - i - 1][1][1] + 0.1))
            negati.append(stats_per_month[len(stats_per_month) - i - 1][2][1])
            b_month = True

    elif min(N_day, N_month, N_year) == N_year:
        names_per_year.reverse()
        stats_per_year = list(data.statistics['pol_data_per_year'].values())
        for i in range(0, len(stats_per_year)):
            posi.append((stats_per_year[len(stats_per_year) - i - 1][0][1] + 0.2))
            neutri.append((stats_per_year[len(stats_per_year) - i - 1][1][1] + 0.1))
            negati.append(stats_per_year[len(stats_per_year) - i - 1][2][1])
            b_year = True

    # ax4 print the number of data we have for each days, months, years
    jour = 0
    mois = 0
    annees = 0
    nb_ = ['Days', 'Months', 'Years']
    for i in range(0, len(names_per_day)):
        jour = jour + 1
    for i in range(0, len(names_per_month)):
        mois = mois + 1
    for i in range(0, len(names_per_year)):
        annees = annees + 1

    nb_stats_ = [jour, mois, annees]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    fig.suptitle(plots_title)
    # bar plot with most common words
    ax1.set(title='Most common words')
    ax1.bar(names_stats, values_stats, edgecolor='black', color=POS_ROW_COLOR)
    ax1.set_xticklabels(labels=names_stats, rotation=45)

    # plot with polarity through time
    ax2.plot(posi, "r--", color=DARKER_POS_ROW_COLOR, label="Positive")
    ax2.plot(negati, "-.", color=DARKER_NEG_ROW_COLOR, label="Negative")
    ax2.plot(neutri, color=DARKER_NEU_ROW_COLOR, label="Neutral")

    # settings for ax2 plot depends on each case (day/month/year)
    # TODO: afficher toutes les dates et non pas seulement 5 ou 6
    # TODO: corriger le warning
    if b_day:
        ax2.set_xticklabels(labels=names_per_day, rotation=45)
        ax2.set(title='Daily opinion from ' + names_per_day[0] + ' to ' + names_per_day[len(stats_per_day) - 1])

    elif b_month:
        ax2.set_xticklabels(labels=names_per_month, rotation=45)
        ax2.set(title='Monthly opinion from ' + names_per_month[0] + ' to ' + names_per_month[len(stats_per_month) - 1])

    elif b_year:
        ax2.set_xticklabels(labels=names_per_year, rotation=45)
        ax2.set(title='Yearly opinion time from ' + names_per_year[0] + ' to ' + names_per_year[len(stats_per_year) - 1])
    ax2.legend()

    # pie graph to chose polarity percentage
    ax3.set(title='Opinion percentage')
    ax3.pie(effectif, labels=labels, autopct='%1.1f%%', colors=colors)

    # bar plot for Data range
    ax4.set(title='Number of unique days, months and years represented')
    ax4.bar(nb_, nb_stats_, edgecolor='black', color=NEG_ROW_COLOR)
    ax4.set_xticklabels(labels=nb_)

    fig.tight_layout()
    return fig
