from nltk.tokenize.regexp import WhitespaceTokenizer
from collections import Counter

class TrueCase(object):
    '''True case from a corpus'''

    def __init__(self, fname):
        with open(fname, 'r') as f:
            self.corpus_txt = f.read().decode('utf-8').replace('\n', ' ')
        self.tokenizer = WhitespaceTokenizer()
        self.word_list = self.tokenizer.tokenize(self.corpus_txt)
        self.lower_word_list = [w.lower() for w in self.word_list]
        self.word_dict_count = Counter(self.word_list)

    def truecase(self, sent):
        '''Return a true_cased sentence to look well formatted'''
        if type(sent) == str:
            sent = self.tokenizer.tokenize(sent)

        output = []
        # If it appears capital more often, use that case
        for word in sent:
            capital = 0
            lower = 0
            all_caps = 0
            try:
                lower += self.word_dict_count[word]
            except:
                lower += 0
            try:
                capital += self.word_dict_count[word.capitalize()]
            except:
                capital += 0
            try:
                all_caps += self.word_dict_count[word.upper()]
            except:
                all_caps += 0

            # find max of those three options
            idx = np.argsort([all_caps, capital, lower])[-1]

            # If not found in dictionary, find original case
            if (all_caps + capital + lower) == 0:
                i = self.lower_word_list.index(word.lower())
                output.append(self.word_list[i])
            elif idx == 0:
                output.append(word.upper())
            elif idx == 1:
                output.append(word.capitalize())
            else:
                output.append(word)

        return ' '.join(output)

    def bulk_truecase(self, list_sent):
        '''Return a list of true_cased strings from an iterable'''
        output = []
        for sent in list_sent:
            output.append(self.truecase(sent))
        return output
