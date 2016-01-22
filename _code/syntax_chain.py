import numpy as np
from nltk.tokenize.regexp import WhitespaceTokenizer
from _code.truecase import TrueCase
from string import punctuation

class SyntaxChain(object):
    '''Return random sentences with reasonable syntax'''

    def __init__(self, syntax_dict):
        self.syntax_dict = syntax_dict
        self.tokenizer = WhitespaceTokenizer()
        self.truecaser = TrueCase(self.syntax_dict['fname'])

    def _pick_structure(self, min_appearances=2):
        '''Return a tuple of tags indicating basic sent structure'''
        grammar_dict = self.syntax_dict['grammar_counter']

        # Get a list of the most common structures
        choice_list = []
        for key, value in grammar_dict.iteritems():
            if value >= min_appearances:
                choice_list.append(key)
        return np.random.choice(choice_list)

    def _fill_words(self, struct):
        '''Return a list of words based on struct'''
        sent = []
        for tag in struct:
            word_list = self.syntax_dict['tag_w_words'][tag]
            sent.append(np.random.choice(word_list))
        return sent

    def _clean_sent(self, sent_str):
        '''Return a sentence with the spacing fixed'''
        clean_str = ''
        for i, char in enumerate(sent_str):
            if char == ' ' and sent_str[i + 1] in punctuation:
                continue
            else:
                clean_str += char
        if clean_str[-1] not in punctuation:
            clean_str += '.'
        return clean_str

    def run(self, min_appearances=2):
        struct = self._pick_structure(min_appearances)
        sent = self._fill_words(struct)
        sent_str = ' '.join(sent)
        sent_str = self._clean_sent(sent_str)
        # sent_str = self.truecaser.truecase(sent_str)
        return sent_str
