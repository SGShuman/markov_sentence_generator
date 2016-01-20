import re
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize.regexp import WhitespaceTokenizer
from string import ascii_uppercase
from collections import Counter

class MarkovChain(object):
	'''Create a MarkovChain from the given dictionary and parameters,
	run() returns a sentence given a seed'''

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
		text = ' '.join(key[-self.key_gram_size:])

		while (not self._check_punc(text)) & (not self._check_upper(text)):
			# Values is a list of lists, each sublist is a tuple
			# If key in dictionary, run, else, use last word of key as seed
			values = dir_dict[key]

			probabilities = np.array([value[1] for value in values])
			probabilities = probabilities / float(np.sum(probabilities))

			# Choose a value with probability, 0 index gives words from tuple
			value = values[np.random.choice(len(values), p=probabilities)][0]
						
			# Add the beginning of value to the text
			words_from_value = value[:self.value_gram_size]
			# If value ends a sent or begins a sent, use the whole thing
			val_string = ''.join(value)
			if self._check_punc(val_string) | self._check_upper(val_string):
				text += ' ' + ' '.join(value)
			else:
				text += ' ' + ' '.join(words_from_value)

			# Create new lookup key
			key = text.split()
			key = tuple(key[-self.markov_dict['chain_len']:])
		return text

	def _rev_sentence(self, sent):
		'''Return a reverse a string sentence'''
		word_list = list(reversed(self.tokenizer.tokenize(sent)))
		return ' '.join(word_list)

	def _check_upper(self, text):
		'''Return True if uppercase letter in text'''
		for char in text:
			if char in ascii_uppercase:
				return True
		return False

	def _check_punc(self, text):
		'''Return True if uppercase letter in text'''
		for char in text:
			if char in '.?!':
				return True
		return False

	def _get_sentence(self, seed):
		'''Return a sentence given a seed'''
		f_text = self._run_chain(seed, self.markov_dict['f_dict'])
		b_text = self._run_chain(seed, self.markov_dict['b_dict'])
		# b_text is backwards obviously, so turn it around
		b_text = self._rev_sentence(b_text)

		# Only include seed once
		sent = b_text[:-len(seed)-1] + ' ' + f_text

		return sent

	def _true_case(self, sent):
		'''Return a truce_case sentence to look well formatted'''
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

	def run(self, input_text, key_gram_size=2, value_gram_size=1):
		'''Return a sentence based on gram_size
		Larger gram_size is more deterministic phrases
		gram_size cannot be larger than chain_len'''
		self.key_gram_size = min(key_gram_size, self.markov_dict['chain_len'])
		self.value_gram_size = min(value_gram_size, self.markov_dict['chain_len'])
		seed = self._get_input(input_text)
		# If seed not in corpus and no neighbor found, return random sent
		if not seed:
			return np.random.choice(self.not_found_list)
		sent = self._get_sentence(seed)
		# Fix space before punc
		sent = sent[:-2] + sent[-1]
		sent = self._true_case(sent)
		return sent

