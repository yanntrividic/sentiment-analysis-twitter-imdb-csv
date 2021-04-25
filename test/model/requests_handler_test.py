'''
Created on Mar 11, 2021

@author: yann
'''

import os

from network_utils import load_driver
import pytest
from requests_handler import RequestsHandler, RequestSyntaxError

cwd = os.getcwd()
os.chdir(cwd)
os.chdir(os.path.realpath('src'))

rh = RequestsHandler()
rh.imdb_webdriver = load_driver()
print(os.getcwd())


def test_import_1():
    try:
        rh.import_local_data("path")
    except FileNotFoundError:
        pytest.fail("Unexpected MyError ..")


def test_import_2():
    rh.import_local_data("path")
    assert rh.local_data.data is None


requests = []
dicts = []

valid_syntax_requests = ["@hello is a valid basic syntax, \"here !\"",
                         "basic request",
                         "#test src:twitter",
                         "lang:blaha #boom", "bam boom", "BAM BOOM"]


@pytest.mark.parametrize("req", valid_syntax_requests)
def test_regex_1(req):
    assert rh._RequestsHandler__check_basic_requirements(req)


invalid_syntax_requests = ['', "*f*e*fzfzef", "hello!", "^test", "#", "Valid request except there's a ; test",
                           "\"A good movie title? *+\"", "       ", ",,,,,,valid,,,,,,", "src::::test", ":", "srce:test",
                           "src:", "\"\"", "   ,  ", "foundentries:50 src:twitter #text", "colname:50 src:twitter #text"]


@pytest.mark.parametrize("req", invalid_syntax_requests)
def test_regex_2(req):
    with pytest.raises(RequestSyntaxError):
        rh._RequestsHandler__interpret_request(req)


valid_semantics_requests = ["@user #tweet but src:twitter", "src:imdb test \"movie\"", "boom src:local", "\"0\" src:imdb",
                            "src:twitter      #test", "src:twitter #test lang:fr", "bam b src:local",
                            "#hello src:twitter, src:local hey lang:fr target:en target:maori", "src:imdb \"test\"", "src:imdb \"test\"",
                            "src:imdb \"test\" maxentries:100", "src:imdb \"test\" lang:en"]


@pytest.mark.parametrize("req", valid_semantics_requests)
def test_semantics_1(req):
    assert rh._RequestsHandler__interpret_request(req)


invalid_semantics_requests = ["@user #tweet but src:imdb", "src:imdb test \"movie\" @user", "boom src:imdb src:twitter",
                              "src:twitter type:reviews test", "src:imdb type:tweets test", "src:twitter"
                              "src:twitter type:tweets test", "src:imdb type:reviews test", "src:twitter hello lang:es",
                              "src:twitter lang:fr lang:de hello", "target:HAHA src:twitter #test",
                              "src:twitter id:test", "src:local year:2020", "src:local (2020)", "src:local \"film\"",
                              "src:imdb \"test\" lang:fr", "#tweet src:twitter maxentries:-10", "0 src:imdb"
                              "#tweet src:twitter maxentries:haha", "hello src:imdb"]


@pytest.mark.parametrize("req", invalid_semantics_requests)
def test_semantics_2(req):
    with pytest.raises(RequestSyntaxError):
        rh._RequestsHandler__interpret_request(req)
