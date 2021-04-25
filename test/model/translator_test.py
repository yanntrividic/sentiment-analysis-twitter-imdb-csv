'''
Created on Apr 7, 2021

@author: yann
'''

from multiprocessing import Value
from network_utils import is_detectlanguage_api_up
import pytest
from translator import SUPPORTED_TARGET_LANGUAGES, is_valid_target_lang, is_lang_valid

valid_langs = ['fr', 'french', 'en', 'english', 'swahili', 'dutch', 'afrikaans', 'maori', 'frisian', 'es', 'it']
invalid_langs = ['test', 'haha', 'tesz', 'zy', 'kw', 'column', 'target', 'src', 'imdb', 'twitter']


def test_supported_languages_dict_not_empty():  # tests if the dict is not empty
    assert SUPPORTED_TARGET_LANGUAGES


@pytest.mark.parametrize("lang", valid_langs)
def test_validity_target(lang):
    assert is_valid_target_lang(lang)


@pytest.mark.parametrize("lang", invalid_langs)
def test_invalidity_target(lang):
    assert not is_valid_target_lang(lang)


valid_detected_lang = [
    ('here comes the warior', ['en']),
    ('here comes the queen', ['en']),
    ('long live the queen', ['en']),
    ('oui il fait beau.', ['fr']),
    ("j'en ai marre de coder des tests unitaires c'est trop chiant", ['fr'])]


@pytest.mark.parametrize("sent, expected_detect_lang", valid_detected_lang)
def test_valid_detected_lang_1(sent, expected_detect_lang):
    if is_detectlanguage_api_up(Value('i', False)):
        with pytest.raises(AttributeError):  # FIXME: find a way to make it fit both cases
            is_lang_valid(sent, expected_detect_lang)
        assert is_lang_valid(sent, expected_detect_lang)
    else:
        print("We can't test the detectlanguage API at the moment.")
        assert True


@pytest.mark.parametrize("sent, expected_detect_lang", valid_detected_lang)  # robustesse à la casse
def test_valid_detected_lang_2(sent, expected_detect_lang):
    if is_detectlanguage_api_up(Value('i', False)):
        assert is_lang_valid(sent.upper(), expected_detect_lang)
    else:
        print("We can't test the detectlanguage API at the moment.")
        assert True
