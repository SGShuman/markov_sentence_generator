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
        self.chunk_pos_list = self._get_chunk_pos(self.chunk_list, self.pos_list)

        self.api = dict(
        annotations_list=self.annotations_list,
        syntax_list=self.syntax_list,
        pos_list=self.pos_list,
        corpus_txt=self.corpus_txt,
        chunk_list=self.chunk_list,
        chunk_pos_list=self.chunk_pos_list,
        fname=fname
        )

        self.to_pkl(fpath)

    def _get_chunk_pos(self, chunk_list, pos_list):
        '''Return a list of three tuples (word, chunk, pos)'''
        chunk_pos_list = []
        for chunk_sent, pos_sent in zip(chunk_list, pos_list):
            tmp = []
            for chunk, pos in zip(chunk_sent, pos_sent):
                #            word      grammar  part of speech
                tmp.append((chunk[0], chunk[1], pos[1]))
            chunk_pos_list.append(tmp)
        return chunk_pos_list

    def _fit(self, sent_list_of_str, dep_parse):
        '''Return annotations from a list of strings, as a list of dicts
        dep_parse is dependency parsing optional feature (takes a long time)'''
        annotator = Annotator()
        return annotator.getBatchAnnotations(sent_list_of_str, dep_parse)

    def get_tools(self, sent_list):
        '''Return sent_list in a variety of formats'''

        flat_list = list(itertools.chain(*sent_list))

        # Count unique tuples
        count_dict = Counter(flat_list)

        # Get dictionary with key=tag, value=list[words]
        tag_w_words = {}
        for tup in flat_list:
            # tup[0] is word, tup[1:] is tuple of tags
            if tup[1:] in tag_w_words:
                tag_w_words[tup[1:]] += [tup[0]]
            else:
                tag_w_words[tup[1:]] = [tup[0]]
        return flat_list, count_dict, tag_w_words

    def get_grammar(self, sent_list):
        '''Return a counter dictionary of sentence structures'''
        sent_struct = []
        for sent in sent_list:
            tmp = []
            for tup in sent:
                tmp.append(tup[1:])
            sent_struct.append(tuple(tmp))
        grammar_counter = Counter(sent_struct)
        return grammar_counter

    def _get_pkl_fname(self, fname):
        '''Return the filename that would have been pkled automatically'''
        fname = fname.rsplit(".", 1)[0] + '_markov_dict.pkl'
        return fname

    def to_pkl(self, fname):
        '''Pickle the api so it can be used without running'''
        with open(fname, 'wb') as f:
            pickle.dump(self.api, f)
