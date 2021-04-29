'''
Created on Apr 15, 2021

@author: yann

Utility module to verify if the network, if the various api services are available for our use, and that tries to load
either firefox's webdriver or chrome's
'''
from multiprocessing import Process, Value
import os
import requests
import time
import traceback
from urllib3.exceptions import NewConnectionError, MaxRetryError, TimeoutError, ConnectionError

from googletrans.client import Translator
from selenium import webdriver
from selenium.webdriver import chrome
from translator import is_lang_valid
import tweepy
from twitter_extraction import api
from webdriver_manager.chrome import ChromeDriverManager  # python3.7 -m pip install webdriver-manager
from webdriver_manager.firefox import GeckoDriverManager

TIMEOUT_DURATION = 5  #  for api requests


def is_connected_internet():
    '''Checks basic internet connection, returns a boolean
    '''
    url = "http://www.google.com"  #  the url doesn't matter as long as its a valid one

    try:
        requests.get(url, timeout=TIMEOUT_DURATION)
        # print("Connected to the Internet")
        return True

    except (requests.ConnectionError, requests.Timeout):
        print("No internet connection.")
        return False


def load_driver():  # le driver est créé
    ''' Function that tries to load a webdriver in the RequestsHandler. If neither Chrome nor Firefox is installed on
    the machine, it won't work and will return an error.
    '''
    driver = None

    try:  #  first we try with Chrome
        options = chrome.options.Options()
        options.add_argument("--headless")
        print("Trying to load Chrome's webdriver...")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        print("Chrome's webdriver loaded with success!")

    except ValueError as e:  # when chrome is not found
        print("Chrome's webdriver couldn't be loaded.")
        print(e)

        try:  #  second with firefox
            options = webdriver.FirefoxOptions()
            options.headless = True
            print("Trying to load Firefox's webdriver...")
            driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),
                                       options=options,
                                       service_log_path=os.devnull)  # prevents the driver from generating logs
            print("Firefox's webdriver loaded with success!")

        except ValueError as e:  # when firefox is not found
            print("Firefox's webdriver couldn't be loaded.")
            print(e)

            raise ValueError("No webdriver could be loaded. Please install a recent version of Chrome or Firefox" +
                             " on your machine.")
            driver = None

        except Exception(e):  # any other exception is caught and printed, but no webdriver will be loaded

            driver = None

    finally:
        print('Finally reached in load_driver')
        return driver


def is_api_up(process, process_name: str, rh=None, iterations=1):
    '''Function that creates a process of the function passed as argument to test if the tested service is
    available or not.
    '''
    result = Value('i', True)  # we create a Value object to be able to retrieve the boolean value changed in the process
    if rh:  #  if the rh is needed
        args = [result, rh]
    else:
        args = [result]

    for i in range(iterations):  #  if we want to test it several times, we can by changing the iterations value

        p = Process(target=process, name=process_name, args=args)
        p.start()

        # Wait for sec_timeout seconds or until process finishes
        p.join(timeout=TIMEOUT_DURATION)

        if p.is_alive():
            p.kill()
            print(p.name + " timed out and was killed.")
            p.join()
            result.value = False
            return

        elif iterations > 1 and not result.value:  # in the case we want to test it again
            print(i, result.value)
            time.sleep(1)

        elif result.value:  # if true, then we exit the loop
            break

    return result.value


def is_detectlanguage_api_up(result: Value, txt='dummy request'):
    '''Method to check if the detect-language API is available or not.
    Returns a boolean that answers the question
    '''
    try:  # if no error is raised, then the API is available
        is_lang_valid(txt, ['fr'])
        result.value = True
        return True
    except(AttributeError, MaxRetryError, NewConnectionError, TimeoutError, ConnectionError, requests.exceptions.ConnectionError):
        # the API raises an attribute error if too many requests were sent today or if the server is not available
        result.value = False
        return False


def is_imdb_api_up(rh):
    '''Checks if a value has been assigned to the RH's webdriver
    '''
    print(rh)
#     if rh.imdb_webdriver:
#         result.value = True
#     else:
#         result.value = False
#     return

    if rh.imdb_webdriver:  # if the webdriver is loaded then it will have a value other than None
        return True
    else:  # we might need to wait for a bit to load
        time.sleep(TIMEOUT_DURATION)
        if rh.imdb_webdriver:
            return True
        else:
            return False  # if at this point this is not loaded, there's no hope.


def is_tweepy_up(result: Value):
    '''Tests if the Twitter API is up by checking the output of Tweepy's requests
    '''
    try:
        result.value = True

        data = api.rate_limit_status()
        if (not data['resources']['search']['/search/tweets']['remaining'] or
                not data['resources']['statuses']['/statuses/user_timeline']['remaining']):
            result.value = False
        # data['resources']['search']['/search/tweets']['remaining'] # remaining requests for tweets
        # data['resources']['statuses']['/statuses/user_timeline']['remaining'] # remaining requests for users
        # with the 'limit' key, we get the original limit

#         print(data['resources']['statuses']['/statuses/home_timeline'])
#         print("/users/lookup " + str(data['resources']['users']['/users/lookup']['remaining']))
#         print("/search/tweets " + str(data['resources']['search']['/search/tweets']['remaining']))
#         print("/statuses/user_timeline " + str(data['resources']['statuses']['/statuses/user_timeline']['remaining']))
#         print("/statuses/lookup " + str(data['resources']['statuses']['/statuses/lookup']['remaining']))
#         print("/application/rate_limit_status " + str(data['resources']['application']['/application/rate_limit_status']['remaining']))

    except tweepy.error.RateLimitError:
        print("Rate limits for the Twitter API called too many times. Please wait your API credits to be reset.")
        result.value = False  # by default, but it needs to be updated to a warning
        return

    except tweepy.error.TweepError:
        print("Your Twitter API key is not valid.")
        result.value = False
        return

    except Exception:
        traceback.print_exc()
        result.value = False
        return


def is_tweepy_api_key_valid():
    try:
        api.rate_limit_status()
    except tweepy.error.TweepError as e:
        if e.api_code == 32:
            return False
        return True
    return True


def is_googletrans_api_up(result: Value, txt='dummy request'):
    '''Method to check if the googletrans API is available or not.
    Returns a boolean that answers the question
    '''
    try:
        translator = Translator()
        output = translator.translate(txt, dest='fr')._response.status_code
        result.value = not (output == 429)  # if the output is equal to 429, it means we don't have anymore credits for today
    except Exception:  # if any exception is raised... Even though this scenario is not very probable
        result.value = False
