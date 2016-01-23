import numpy as np
from nltk.tokenize.regexp import WhitespaceTokenizer
from _code.truecase import TrueCase
from string import punctuation
from _code.syntax_tree import SyntaxTree

class SyntaxChain(object):
    '''Return random sentences with reasonable syntax
    gtype=syntax gives syntax tags
    gtype=pos gives part of speech tags
    gtype=syntax_pos gives both'''

    def __init__(self, fname, gtype='syntax'):
        self.tokenizer = WhitespaceTokenizer()
        self.truecaser = TrueCase(fname)
        self.SyntaxTree = SyntaxTree(fname)
        self.gtype = gtype
        if self.gtype == 'syntax':
            self.tup_list = self.SyntaxTree.chunk_list
        elif self.gtype == 'pos':
            self.tup_list = self.SyntaxTree.pos_list
        else:
            self.tup_list = self.SyntaxTree.chunk_pos_list

    def _pick_structure(self, min_appearances=2):
        '''Return a tuple of tags indicating basic sent structure'''
        grammar_dict = self.SyntaxTree.get_grammar(self.tup_list)

        # Get a list of the most common structures
        choice_list = []
        max_val = 0
        for key, value in grammar_dict.iteritems():
            max_val = max([max_val, value])
            if value >= min_appearances:
                choice_list.append(key)
        if not choice_list:
            print 'Set min_appearances below %' % max_val
            return None
        return np.random.choice(choice_list)

    def _fill_words(self, struct):
        '''Return a list of words based on struct'''
        sent = []
        _, _, tag_w_words = self.SyntaxTree.get_tools(self.tup_list)
        for tag in struct:
            word_list = tag_w_words[tag]
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
        if struct:
            sent = self._fill_words(struct)
            sent_str = ' '.join(sent)
            sent_str = self._clean_sent(sent_str)
            sent_str = self.truecaser.truecase(sent_str)
        else:
            sent_str = 'Try Again!'
        return sent_str
