import pytest

from app.nlp import NLPEngine

nlp = NLPEngine()


def test__get_info():
    info = nlp.get_info('eng', 'moon', 'This is a moon')

    assert info.lemma == 'moon'
    assert info.pos == 'NOUN'
    assert info.word == 'moon'
    assert info.lang == 'eng'


def test__get_info_skip_det():
    info = nlp.get_info('eng', 'the moon', 'This is a moon')

    assert info.lemma == 'moon'
    assert info.pos == 'NOUN'
    assert info.word == 'moon'
    assert info.lang == 'eng'


def test__calc_similarity():
    assert nlp.similarity('eng', 'She has opened the door', 'The starship landed') == pytest.approx(0.586155248)
    assert nlp.similarity('eng', 'She has opened the door', 'The door was opened') == pytest.approx(0.9507504)
