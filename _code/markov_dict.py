from nltk.tokenize import sent_tokenize
from nltk.tokenize.regexp import WhitespaceTokenizer
import cPickle as pickle
from _code.syntax_tree import SyntaxTree
import itertools
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter

class MarkovDict(object):
    '''Contains Markov Dict for both forward and backwards

    Input: filename of the corpus, len of Markov Chain
    Output: use md.api to access info
    use md.wordcloud() for a wordcloud over any corpus
    gtype=naive is a dict without syntax
    gtype=syntax is a dict with syntax included
    gtype=pos is dict with part of speech
    gtype=syntax_pos is both'''

    def __init__(self, fname, gram_size, gtype='naive'):
        # Load text and get rid of line breaks
        with open(fname, 'r') as f:
            self.corpus_txt = f.read().decode('utf-8').replace('\n', ' ')
        self.gtype = gtype

        self.gram_size = gram_size
        if gtype != 'naive':
            print 'Fitting Syntax Model'
            self.SyntaxTree = SyntaxTree(fname)
            print 'Syntax Model Complete'
            self._fit_syntax()
        else:
            self._fit()
        self.word_list = list(itertools.chain(*self.f_sent))
        self.stats = self._make_stats()
        self.api = dict(
            corpus_txt=self.corpus_txt,
            gram_size=self.gram_size,
            word_list=self.word_list,
            unq_words=set(self.word_list),
            f_sent=self.f_sent,
            b_sent=self.b_sent,
            f_dict=self.f_dict,
            b_dict=self.b_dict,
            stats=self.stats,
            fname=fname,
            gtype=gtype
            )

    def _fit(self):
        '''Tokenize the documents, make backwards and forwards lists
        call the make_dictionary method'''

        tokenizer = WhitespaceTokenizer()
        # Get the sentences from the corpus
        sent_list_of_str = sent_tokenize(self.corpus_txt.lower())
        # Capitalize and save the punctuation from the end
        sent_cap = [(sent.capitalize()[:-1], sent[-1]) for sent in sent_list_of_str]
        # Word tokenize to keep contractions, add back on punc
        self.f_sent = [tokenizer.tokenize(word_tuple[0]) + [word_tuple[1]] for word_tuple in sent_cap]
        # Reverse those sentences
        self.b_sent = [list(reversed(word_list)) for word_list in self.f_sent]
        self.f_dict = self._make_dictionary(self.f_sent)
        self.b_dict = self._make_dictionary(self.b_sent)

    def _fit_syntax(self):
        '''Fit sentences that have already been split into syntax components'''
        # Choose iterable based on type of dictionary available
        if self.gtype == 'syntax':
            iter_list = self.SyntaxTree.chunk_list
        elif self.gtype == 'pos':
            iter_list = self.SyntaxTree.pos_list
        else:
            iter_list = self.SyntaxTree.chunk_pos_list

        # Lowercase the words
        self.f_sent = []
        for sent in iter_list:
            tmp = [tuple([tup[0].lower(), tup[1:]]) for tup in sent]
            self.f_sent.append(tmp)

        self.b_sent = [list(reversed(chunk_list)) for chunk_list in self.f_sent]
        self.f_dict = self._make_dictionary(self.f_sent)
        self.b_dict = self._make_dictionary(self.b_sent)

    def _make_dictionary(self, sentences):
        '''Return a markov dictionary from a list of sentences

        Keys are tuples of len gram_size; Values are lists of lists
        Each sub_list contains a tuple of words that follow the key'''

        dictionary = {}
        for sentence in sentences:
            sen_len = len(sentence)
            for word_idx in xrange(sen_len):
                if word_idx <= (sen_len - self.gram_size):
                    key_end = word_idx + self.gram_size
                    key_to_insert = [sentence[i] for i in xrange(word_idx, key_end)]

                    value_to_insert = sentence[key_end:key_end+self.gram_size]
                    key_to_insert = tuple(key_to_insert)
                    value_to_insert = tuple(value_to_insert)

                # Put both key an item in dictionary
                if key_to_insert not in dictionary:
                    dictionary[key_to_insert] = [value_to_insert]
                else:
                    dictionary[key_to_insert] += [value_to_insert]
        return dictionary

    def to_pkl(self, fname):
        '''Pickle the api so it can be used without running'''
        with open(fname, 'wb') as f:
            pickle.dump(self.api, f)

    def _make_stats(self):
        '''Create common stats most users would want to know'''
        stats = dict(
            num_sentences=len(self.f_sent),
            num_words=sum([len(sent) for sent in self.f_sent]),
            unq_words=len(set(self.word_list)),
            )
        # Get the distribution of value lengths
        if self.gtype != 'naive':
            val_list = [val for key, val in self.f_dict.iteritems()]
            len_list = [len(lst) for lst in val_list]
            stats['dist_of_val_len'] = Counter(len_list)
        return stats

    def wordcloud(self, **args):
        '''Display a wordcloud from the corpus'''
        wordcloud = WordCloud(**args)\
                    .generate(self.corpus_txt)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()

    def plot_dist(self, log=True):
        '''Display a histogram of log value lengths from the dictionary'''
        df = pd.DataFrame.from_dict(self.stats['dist_of_val_len'], orient='index')
        if log:
            tmp = df.apply(lambda x: np.log(x))
            tmp.hist()
            xlabel = 'Log Number of Values'
        else:
            xlabel = 'Number of Values'
            df.hist()
        plt.xlabel(xlabel)
        plt.ylabel('Number of Keys')
        plt.title('Distribution of Value Lengths for unique Keys')
        plt.show()
