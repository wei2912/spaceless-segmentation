import re
import sys
from collections import OrderedDict

class Entry:
	def __init__(self, word, root_form, postags):
		self.word = word
		self.root_form = root_form
		self.postags = postags

	def __repr__(self):
		chars = []
		for postag in self.postags:
			chars.append("<")
			chars.append(postag)
			chars.append(">")
		return "%s:%s%s" % (self.word, self.root_form, ''.join(chars))

entry_regex = "(.*?):(.*?)(?:<(.*?)>)+"
entry_regex = re.compile(entry_regex)

class Dictionary:
	def __init__(self, filepath):
		self.transitions = {}
		self.finals = set()
		self.tags = {}

		max_state = 0

		f = open(filepath, "r")
		for line in f:
			line = line.strip()
			if line == "":
				continue
			current_state = 0 # initial state

			entry = self.parse_entry(line)
			if entry.word in self.tags:
				self.tags[entry.word].append((entry.root_form, entry.postags))
			else:
				self.tags[entry.word] = [(entry.root_form, entry.postags)]

			chars = list(entry.word)
			for char in chars:
				if not (current_state, char) in self.transitions:
					max_state += 1
					new_state = max_state

					self.transitions[(current_state, char)] = new_state
				else:
					new_state = self.transitions[(current_state, char)]
				
				current_state = new_state
			self.finals.add(current_state)
	def parse_entry(self, line):
		search = entry_regex.search(line)
		if search:
			groups = search.groups()
			return Entry(groups[0], groups[1], groups[2:])
		return None
