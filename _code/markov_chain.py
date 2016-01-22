import re
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize.regexp import WhitespaceTokenizer
from collections import Counter
from _code.truecase import TrueCase

class MarkovChain(object):
	'''Create a MarkovChain from the given dictionary and parameters,
	run() returns a sentence given a seed

	markov_dict should be a MarkovDict().api dictionary'''

	def __init__(self, markov_dict, priority_list, not_found_list, neighbor_dict):
		self.markov_dict = markov_dict
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
		return word in self.markov_dict['unq_words']

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
			# Look at the last gram_size words in the key
			# First word in that gram_size phrase must match seed
			if seed == key[-self.key_gram_size]:
				key_list.append(key)
		return key_list[np.random.choice(len(key_list))]

	def _run_chain(self, seed, dir_dict):
		'''Return a string of words generated from seed
		Iterate through dictionary until a period or capital is reached'''
		key = self._generate_key(seed, dir_dict)
		text = list(key[-self.key_gram_size:])

		while (not self._check_punc(text)) & (not self._check_upper(text)):
			# Values is a list of lists, each sublist is a tuple
			# If key in dictionary, run, else, use last word of key as seed
			values = dir_dict[key]

			# Choose a value with probability equal to distribution in corpus
			value = np.random.choice(values)

			# Add the beginning of value to the text
			words_from_value = value[:self.value_gram_size]
			# If value ends a sent or begins a sent, use the whole thing
			val_string = ''.join(value)
			if self._check_punc(val_string) | self._check_upper(val_string):
				text += value
			else:
				text += words_from_value

			# Create new lookup key
			key = tuple(text[-self.markov_dict['chain_len']:])
		return text

	def _rev_sentence(self, sent):
		'''Return a reverse a string sentence'''
		word_list = list(reversed(self.tokenizer.tokenize(sent)))
		return ' '.join(word_list)

	def _check_upper(self, text):
		'''Return True if uppercase letter in text'''
		if isinstance(text, basestring):
			for char in text:
				if char.isupper():
					return True

		else:
			for word in text:
				for char in word:
					if char.isupper():
						return True
		return False

	def _check_punc(self, text):
		'''Return True if uppercase letter in text'''
		if isinstance(text, basestring):
			for char in text:
				if char in '.?!':
					return True
		else:
			for word in text:
				for char in word:
					if char in '.?!':
						return True
		return False

	def _get_sentence(self, seed):
		'''Return a sentence given a seed'''
		f_text = self._run_chain(seed, self.markov_dict['f_dict'])
		b_text = self._run_chain(seed, self.markov_dict['b_dict'])
		# b_text is backwards obviously, so turn it around
		b_text = list(reversed(b_text))

		# Only include seed once
		sent = b_text[:-1] + f_text

		return sent

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
		sent_str = ' '.join(sent)
		# Fix space before punc
		sent_str = sent_str[:-2] + sent_str[-1]
		output = self.truecaser.truecase(sent_str)
		return output
