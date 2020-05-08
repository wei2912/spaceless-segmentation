class Tokeniser:
	def __init__(self, dictionary):
		self.dict = dictionary
	def tokenise(self, text):
		chars = list(text)

		alive_states = [(0, 0)] # spos, state
		
		tokens = []
		units = []

		spos = 0
		cpos = 0
		for char in chars:
			cpos += 1

			new_states = []
			terminated_states = []
			start_new = False
			for state in alive_states:
				state_spos = state[0]
				cur_state = state[1]
				
				if (cur_state, char) in self.dict.transitions:
					new_state = self.dict.transitions[(cur_state, char)]
					new_states.append((state_spos, new_state))

					if (new_state) in self.dict.finals:
						word = ''.join(chars[state_spos:cpos])
						token = Token(state_spos, word, cpos)
						tokens.append(token)
						start_new = True

					if cpos < len(chars):
						nxt_char = chars[cpos]
						if not (new_state, nxt_char) in self.dict.transitions:
							terminated_states.append(state)
					else:
						terminated_states.append(state)
				else:
					terminated_states.append(state)
					start_new = True

			if start_new:
				new_states.append((cpos, 0))

			if alive_states == terminated_states:
				for i in range(spos, cpos):
					char = chars[i]
					token = Token(i, "*"+char, i+1)

					valid = False
					if (0, char) in self.dict.transitions:
						new_state = self.dict.transitions[(0, char)]
						if new_state in self.dict.finals:
							valid = True

					if not token in tokens and not valid:
						tokens.append(token)
				sequences = self.get_all_sequences(tokens, spos)
				unit = Unit(''.join(chars[spos:cpos]), sequences)
				units.append(unit)

				spos = cpos
				tokens = []

			alive_states = new_states

		return units

	def get_tags(self, word):
		if word in self.dict.tags:
			return self.dict.tags[word]
		return []

	def get_all_sequences(self, tokens, spos):
		sequences = []
		start_tokens = []
		for token in tokens:
			if token.start == spos:
				start_tokens.append(token)

		if len(start_tokens) == 0:
			return [[]]

		for token in start_tokens:
			if token.word.startswith("*"):
				# let's see if there's an alternative valid token
				orig_word = token.word[1:] # strip off "*"

				found = False
				for match_token in start_tokens:
					if match_token.word.startswith(orig_word):
						found = True
						break

				if found: # there's an alternative valid token
					continue
			n_sequences = self.get_all_sequences(tokens, token.end)
			for i in range(len(n_sequences)):
				n_sequences[i] = [token] + n_sequences[i]
			sequences.extend(n_sequences)
		return sequences

class Unit:
	def __init__(self, orig, sequences):
		self.orig = orig
		self.sequences = sequences
	def __repr__(self):
		chars = ['^', self.orig]
		for sequence in self.sequences:
			chars.append('/')
			words = [token.__repr__() for token in sequence]
			chars.append('+'.join(words))
		chars.append('$')
		return ''.join(chars)

class Token:
	def __init__(self, start, word, end):
		word = word.strip()
		if word == "":
			raise Exception("Empty token.")

		if start == end:
			raise Exception("Start of token is equal to end (%d)." % start)

		self.start = start
		self.word = word
		self.end = end
	def __repr__(self):
		return self.word