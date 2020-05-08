from tokeniser import tokeniser, threadpool, pb

import os
from queue import Queue

## CONSTANTS ##
DISCOUNT = 0.5 # vary for performance
## CONSTANTS ##

## IO ##
def read_data(filepath):
	frequencies = {}

	if not os.path.exists(filepath):
		f = open(filepath, 'w+')
		f.close()

	i_file = open(filepath, 'r')
	for line in i_file:
		line = line.strip()
		if line == "":
			continue

		values = line.split(":")
		if line.startswith(":"):
			# handle the special case where : is a token
			# resulting in ['', '', '2.5'] for example

			token = ":"
			frequency = float(values[2])
		else:
			token = values[0]
			frequency = float(values[1])

		frequencies[token] = frequency
	return frequencies

def write_data(filepath, frequencies):
	f = open(filepath, 'w+')
	for key in frequencies.keys():
		f.write("%s:%s\n" % (key, frequencies[key]))
	f.close()
## IO ##

def calc_score(token, frequencies, voc_size, total_count):
	freq_count = 0.0 # by default
	if token in frequencies:
		freq_count = frequencies[token]

	return (freq_count + DISCOUNT)/(total_count + (voc_size+1) * DISCOUNT)

def rank(frequencies, units):
	voc_size = len(frequencies)

	total_count = 0.0
	for token in frequencies.keys():
		total_count += frequencies[token]

	n_units = []
	for unit in units:
		scores = []
		for seq in unit.sequences:
			score = 1
			for token in seq:
				score *= calc_score(token, frequencies, voc_size, total_count)
			scores.append(score)

		scores = [score/sum(scores) for score in scores]

		max_score = -1
		max_index = -1
		for i in range(len(scores)):
			if scores[i] > max_score:
				max_score = scores[i]
				max_index = i

		for token in unit.sequences[max_index]:
			unit = tokeniser.Unit(token.word, [[token]])
			n_units.append(unit)
	return n_units

class Trainer:
	def __init__(self, dictionary, tokeniser, THREAD_COUNT):
		self.dict = dictionary
		self.pool = threadpool.ThreadPool(THREAD_COUNT)
		self.tokeniser = tokeniser
	def train(self, frequencies, lines):
		q = Queue()
		def count_frequencies(line):
			frequencies = {}
			units = self.tokeniser.tokenise(line)
			for unit in units:
				if not unit.sequences:
					continue
				seen = 1 / len(unit.sequences)
				for sequence in unit.sequences:
					for token in sequence:
						if token.word.startswith("*"):
							continue
						if token.word in frequencies:
							frequencies[token.word] += seen
						else:
							frequencies[token.word] = seen
			q.put(frequencies)

		for line in lines:
			self.pool.add_task(count_frequencies, line)
		while not self.pool.finished():
			continue # waiting...

		while not q.empty():
			small_frequencies = q.get()
			for word in small_frequencies.keys():
				if word in frequencies:
					frequencies[word] += small_frequencies[word]
				else:
					frequencies[word] = small_frequencies[word]
		return frequencies