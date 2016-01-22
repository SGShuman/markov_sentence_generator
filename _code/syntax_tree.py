from practnlptools.tools import Annotator
from nltk.tokenize import sent_tokenize
from collections import Counter
from nltk.tokenize.regexp import WhitespaceTokenizer
import itertools
import cPickle as pickle

class SyntaxTree(object):
    '''Return a syntax object
    Annotator comes from https://github.com/biplab-iitb/practNLPTools'''

    def __init__(self, fname, dep_parse=False):
        # Get corpus
        with open(fname, 'r') as f:
            self.corpus_txt = f.read().decode('utf-8').replace('\n', ' ')

        str_lst = sent_tokenize(self.corpus_txt)

        # (, ) break the annotator
        str_lst = [x.replace('(', '') for x in str_lst]
        self.sent_list_of_str = [x.replace(')','') for x in str_lst]

        # Get annotations for all sentences
        fpath = self._get_pkl_fname(fname)
        # Load from pkl if already fit once (saves two minutes)
        try:
            with open(fpath, 'r') as f:
                self.annotations_list = pickle.load(f)['annotations_list']
                print 'Loading from file'
        except:
            self.annotations_list = self._fit(self.sent_list_of_str, dep_parse)
        # Get syntax_list feature, among others available, x is dict
        self.syntax_list = [x['syntax_tree'] for x in self.annotations_list]
        self.pos_list = [x['pos'] for x in self.annotations_list]
        self.chunk_list = [x['chunk'] for x in self.annotations_list]
        self._get_word_pos()
        self._get_word_tag()
        self._get_grammar()

        self.api = dict(
        annotations_list=self.annotations_list,
        syntax_list=self.syntax_list,
        pos_list=self.pos_list,
        corpus_txt=self.corpus_txt,
        chunk_list=self.chunk_list,
        flat_tag_list=self.flat_tag_list,
        flat_pos_list=self.flat_pos_list,
        pos_dict=self.pos_dict,
        tag_dict=self.tag_dict,
        words_w_pos=self.words_w_pos,
        words_w_tag=self.words_w_tag,
        pos_w_words=self.pos_w_words,
        tag_w_words=self.tag_w_words,
        grammar_counter=self.grammar_counter,
        fname=fname
        )

        self.to_pkl(fpath)

    def _fit(self, sent_list_of_str, dep_parse):
        '''Return annotations from a list of strings, as a list of dicts
        dep_parse is dependency parsing optional feature (takes a long time)'''
        annotator = Annotator()
        return annotator.getBatchAnnotations(sent_list_of_str, dep_parse)

    def _get_word_pos(self):
        '''Return word pos in a variety of formats'''

        self.flat_pos_list = list(itertools.chain(*self.pos_list))

        # Count unique tuples
        self.pos_dict = Counter(self.flat_pos_list)

        # Get dictionary with key=word, value=list[pos]
        # Tags repeat, so choosing from them maintains probability
        self.words_w_pos = {}
        for word, pos in self.flat_pos_list:
            if word in self.words_w_pos:
                self.words_w_pos[word] += [pos]
            else:
                self.words_w_pos[word] = [pos]

        # Get dictionary with key=tag, value=list[words]
        self.pos_w_words = {}
        for word, pos in self.flat_pos_list:
            if pos in self.pos_w_words:
                self.pos_w_words[pos] += [word]
            else:
                self.pos_w_words[pos] = [word]

    def _get_word_tag(self):
        '''Return word tag in a variety of formats'''

        self.flat_tag_list = list(itertools.chain(*self.chunk_list))

        # Count unique tuples
        self.tag_dict = Counter(self.flat_tag_list)

        # Get dictionary with key=word, value=list[tag]
        # Tags repeat, so choosing from them maintains probability
        self.words_w_tag = {}
        for word, tag in self.flat_tag_list:
            if word in self.words_w_tag:
                self.words_w_tag[word] += [tag]
            else:
                self.words_w_tag[word] = [tag]

        # Get dictionary with key=tag, value=list[words]
        self.tag_w_words = {}
        for word, tag in self.flat_tag_list:
            if tag in self.tag_w_words:
                self.tag_w_words[tag] += [word]
            else:
                self.tag_w_words[tag] = [word]

    def _get_grammar(self):
        '''Return a counter dictionary of sentence structures'''
        sent_struct = []
        for sent in self.chunk_list:
            tmp = [y for x, y in sent]
            sent_struct.append(tuple(tmp))
        self.grammar_counter = Counter(sent_struct)

    def _get_pkl_fname(self, fname):
        '''Return the filename that would have been pkled automatically'''
        fname = fname.split('.')
        fname = ''.join(fname[:-1]) + '_markov_dict.pkl'
        return fname

    def to_pkl(self, fname):
        '''Pickle the api so it can be used without running'''
        with open(fname, 'wb') as f:
            pickle.dump(self.api, f)
