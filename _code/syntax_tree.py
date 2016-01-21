from practnlptools.tools import Annotator
from nltk.tokenize import sent_tokenize
from collections import Counter
from nltk.tokenize.regexp import WhitespaceTokenizer

class SyntaxSent(object):
    '''Return a syntax object'''

    def __init__(self, fname):
        with open(fname, 'r') as f:
            self.corpus_txt = f.read().decode('utf-8').replace('\n', ' ')
        self.sent_list_of_str = sent_tokenize(self.corpus_txt)
        self.annotations_list = self._fit(self.sent_list_of_str)
        self.syntax_list = [x['syntax_tree'] for x in self.annotations_list]
        self._get_word_tags()

        self.api = dict(
        annotations_list=self.annotations_list,
        syntax_list=self.syntax_list,
        corpus_txt=self.corpus_txt,
        tag_list=self.tag_list,
        tags=self.tags,
        words_w_tag=self.words_w_tags,
        tags_w_words=self.tags_w_words
        )

    def _fit(self, sent_list_of_str):
        annotator = Annotator()
        return annotator.getBatchAnnotations(sent_list_of_str)

    def _get_word_tags(self):
        '''Return word tags'''
        # Get tags from corpus as strings
        tag_list_str = []
        for syntax_repr in self.syntax_list:
            for i in xrange(len(syntax_repr)):
                if syntax_repr[i] == '(':
                    for j in xrange(i+1, i+1 + len(syntax_repr[i+1:])):
                        if syntax_repr[j] == '(':
                            break
                        elif syntax_repr[j] == ')':
                            tag_list_str.append(syntax_repr[i:j+1])
                            break

        # Turn string tags into tuples
        tokenizer = WhitespaceTokenizer()
        self.tag_list = []
        for tag_str in tag_list_str:
            tokens = tokenizer.tokenize(tag_str)
            self.tag_list.append((tokens[0][1:], tokens[1][:-1]))

        self.tags = Counter(self.tag_list)

        self.words_w_tags = {}
        for tag, word in self.tag_list:
            if word in self.words_w_tags:
                self.words_w_tags[word] += [tag]
            else:
                self.words_w_tags[word] = [tag]

        self.tags_w_words = {}
        for tag, word in self.tag_list:
            if tag in self.tags_w_words:
                self.tags_w_words[tag] += [word]
            else:
                self.tags_w_words[tag] = [word]

    def to_pkl(self, fname):
        '''Pickle the api so it can be used without running'''
        with open(fname, 'wb') as f:
            pickle.dump(self.api, f)
