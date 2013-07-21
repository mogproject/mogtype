# -*- coding: utf-8 -*-

import re

# Kana table
ASC2KANA = {
    '1234567890-=': u'ぬふあうえおやゆよわほ゜',
    'qwertyuiop[]\\': u'たていすかんなにらせ゛むへ',
    'asdfghjkl;\'': u'ちとしはきくまのりれけ',
    'zxcvbnm,./': u'つさそひこみもねるめ',
    '#$%^&*()': u'ぁぅぇぉゃゅょを',
    'E}': u'ぃー',
    '"': u'ろ',
    'Z<>?': u'っ、。・',
}

# Functions
re_hiragana = re.compile(ur'[ぁ-ゔ]')
re_katakana = re.compile(ur'[ァ-ヴ]')
re_dakuten = re.compile(ur'[がぎぐげござじずぜぞだぢづでどばびぶべぼゔ]')
re_handakuten = re.compile(ur'[ぱぴぷぺぽ]')


def hiragana(text):
    """Convert katakana to hiragana."""
    return re_katakana.sub(lambda x: unichr(ord(x.group(0)) - 0x60), text)


def katakana(text):
    """Convert hiragana to katakana."""
    return re_hiragana.sub(lambda x: unichr(ord(x.group(0)) + 0x60), text)


def split_sound(text):
    """Split dakuten and handakuten characters into pairs.
        This function works for only hiragana characters.
    """
    def f(ch):
        if ch == u'ゔ':
            return u'う゛'
        return unichr(ord(ch) - 1) + u'゛'
    text = re_dakuten.sub(lambda x: f(x.group(0)), text)
    text = re_handakuten.sub(
        lambda x: unichr(ord(x.group(0)) - 2) + u'゜', text)
    return text


def normalize(text):
    return split_sound(hiragana(text))

# Conversion table
ord2kana = {}
kana2ord = {}

for i in ASC2KANA:
    for (j, k) in enumerate(i):
        ord2kana[ord(k)] = ASC2KANA[i][j]
        kana2ord[ASC2KANA[i][j]] = ord(k)


def ords(unicode_text):
    return [kana2ord.get(u) for u in normalize(unicode_text)]


def get_kana(ch):
    return ord2kana.get(ch)


def is_valid(ch):
    return ch in ord2kana
