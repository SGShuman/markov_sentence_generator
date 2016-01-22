import re
import numpy as np
import cPickle as pickle
from nltk.corpus import stopwords
from nltk.tokenize.regexp import WhitespaceTokenizer
from collections import Counter
from _code.truecase import TrueCase
from _code.markov_dict import MarkovDict
from string import punctuation

class MarkovChain(object):
	'''Create a MarkovChain from the given dictionary and parameters,
	run() returns a sentence given a seed

	markov_dict should be a MarkovDict().api dictionary'''

	def __init__(self, markov_dict, priority_list, not_found_list, neighbor_dict):
		self.markov_dict = markov_dict
		self.gtype = self.markov_dict['gtype']
		self.stop_words = set(stopwords.words('english'))
		self.priority_list = priority_list
		self.not_found_list = not_found_list
		self.neighbor_dict = neighbor_dict
		self.tokenizer = WhitespaceTokenizer()
		self.word_list = self.tokenizer.tokenize(self.markov_dict['corpus_txt'])
		self.lower_word_list = [w.lower() for w in self.word_list]
		# Count of word freq, maintaining case
		self.word_dict_count = Counter(self.word_list)
		self.truecaser = TrueCase(self.markov_dict['fname'])

	def _get_input(self, input_phrase):
		'''Take in the raw input from the user'''
		# Lowercase and remove common punc
		input_phrase = input_phrase.lower()
		input_phrase = re.sub('\?', '', input_phrase)
		input_phrase = re.sub('\.', '', input_phrase)
		input_phrase = re.sub(',', '', input_phrase)
		input_phrase = re.sub('!', '', input_phrase)

		# List of words from a potential input phrase
		word_list = input_phrase.split()

		# Make a list of words that are in priority_list
		priority_words = [w for w in word_list if w in self.priority_list]

		# If no priority words, look for non stop words
		content = [w for w in word_list if w not in self.stop_words]

		# Look for priority words first, content second, and finally random
		if priority_words:
			seed = np.random.choice(priority_words)
		elif content:
			seed = np.random.choice(content)
		else:  # Final option is a random word
		    seed = np.random.choice(content)

		# if the words is not in text, find neighbors
		if not self._in_text(seed):
			seed = self._get_neighbor(seed)

		return seed


	def _in_text(self, word):
		'''Return true if word is in the corpus'''
		return word.lower() in set(self.lower_word_list)

	def _get_neighbor(self, seed):
		'''Return the nearest neighbor to seed from a database'''
		neighbors = self.neighbor_dict[seed]

		good_neighbors = []
		for word in neighbors:
			if self._in_text(word):  # Only pick a neighbor if in text
				good_neighbors.append(word)
		if good_neighbors:
			return np.random.choice(good_neighbors)
		else:
			return None

	def _generate_key(self, seed, dir_dict):
		'''Return key from a chosen seed'''
		key_list = []
		for key in dir_dict:
			# Look at the last key_gram_size words in the key
			# First word in that key_gram_size len phrase must match seed
			if seed in key[-self.key_gram_size]:
				key_list.append(key)
		return key_list[np.random.choice(len(key_list))]

	def _run_chain(self, seed, dir_dict):
		'''Return a list of words generated from seed
		Iterate through dictionary until a period or capital is reached'''
		key = self._generate_key(seed, dir_dict)
		text = list(key[-self.key_gram_size:])

		# If not end/begin of sent, run
		while True:
			# Values is a list of lists
			values = dir_dict[key]

			# Choose a value with probability equal to distribution in corpus
			value = values[np.random.choice(len(values))]
			if (() in value) | (value == ()): # End condition
				break

			# Add a value_gram_size phrase to the text
			words_from_value = value[:self.value_gram_size]
			text += words_from_value

			# Create new lookup key
			key = tuple(text[-self.markov_dict['chain_len']:])
		return text

	def _get_sentence(self, seed):
		'''Return a sentence given a seed'''
		f_text = self._run_chain(seed, self.markov_dict['f_dict'])
		b_text = self._run_chain(seed, self.markov_dict['b_dict'])

		# b_text is backwards obviously, so turn it around
		b_text = list(reversed(b_text))

		# Only include seed once
		sent = b_text[:-1] + f_text

		return sent

	def _get_sentence_str(self, sent):
		'''Return a string representation of a list'''
		if self.gtype == 'syntax':
			sent = [w[0] for w in sent]
		text = ' '.join(sent)

		punc_w_space = [' ' + x for x in punctuation]
		for i in xrange(len(text)-1):
			if text[i:i+2] in punc_w_space:
				text = text[:i] + text[i+1:]
		return text

	def run(self, input_text, key_gram_size=2, value_gram_size=1):
		'''Return a sentence based on gram_size
		Larger gram_size is more deterministic phrases
		gram_size cannot be larger than chain_len'''
		self.key_gram_size = min(key_gram_size, self.markov_dict['chain_len'])
		self.value_gram_size = min(value_gram_size, self.markov_dict['chain_len'])
		while self.key_gram_size + self.value_gram_size < self.markov_dict['chain_len']:
			self.value_gram_size += 1

		seed = self._get_input(input_text)
		# If seed not in corpus and no neighbor found, return random sent
		if not seed:
			return np.random.choice(self.not_found_list)
		sent = self._get_sentence(seed)

		# Turn into string for output
		sent_str = self._get_sentence_str(sent)

		# Fix space before punc
		output = self.truecaser.truecase(sent_str)
		return output

if __name__ == '__main__':
	print 'Fitting Dictionary'
	fname = 'data/obama_corpus.txt'
	chain_len = int(raw_input('Set markov chain length: '))
	md = MarkovDict(fname, chain_len, gtype='syntax')

	print 'Opening Neighbors'
	with open('data/neighbours.pkl') as f:
	    neighbor_dict = pickle.load(f)

	print 'Fitting Chain'
	priority_list = ['america', 'iran', 'iraq', 'health', 'terrorism']
	not_found_list = [
	    'Change will not come if we wait for some other person or some other time. We are the ones we\'ve been waiting for. We are the change that we seek.',
	    'If you\'re walking down the right path and you\'re willing to keep walking, eventually you\'ll make progress.',
	    'The future rewards those who press on. I don\'t have time to feel sorry for myself. I don\'t have time to complain. I\'m going to press on.',
	    'I don\'t oppose all wars. What I am opposed to is a dumb war. What I am opposed to is a rash war.',
	    'There\'s not a liberal America and a conservative America - there\'s the United States of America.'
	]
	mc = MarkovChain(md.api, priority_list, not_found_list, neighbor_dict)

	while True:
		seed = raw_input('Enter a word or phrase to start: ')
		print mc.run(seed, 1, 1)
		another = raw_input('Keep playing? (y/n): ')
		if another == 'n':
			break
		else:
			continue
