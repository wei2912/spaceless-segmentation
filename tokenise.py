#!/usr/bin/env python

import sys
import argparse

if sys.version_info < (3, 0):
	print("Spaceless Segmentation requires Python 3.0 and above.")
	exit(1)

parser = argparse.ArgumentParser(description='Spaceless Segmentation.')
parser.add_argument('-d', '--dict', help='dictionary file', required=True)
parser.add_argument('-a', '--all', action='store_true', help='return all possible segmentations instead of using a ranking algorithm')
parser.add_argument('-t', '--training', help='file which trained data is obtained from. required if -a/--all is not set.')
parser.add_argument('-i', '--input', help='input file', required=True)

args = vars(parser.parse_args())

if not args['all'] and not args['training']:
	parser.error("Ranking algorithm is being used; training file is required.")
if args['all'] and args['training']:
	parser.error("All possible segmentations will be returned; training file provided will not be used.")

from tokeniser import tokeniser, dict, training

def main(args):
	dictionary = dict.Dictionary(args['dict'])
	tokeniser_obj = tokeniser.Tokeniser(dictionary)

	if not args['all']:
		training_data = training.read_data(args['training'])

	tokenised = []
	i_file = open(args['input'], 'r')
	for line in i_file:
		line = line.strip()
		if line == "":
			continue

		units = tokeniser_obj.tokenise(line)
		if not args['all']:
			units = training.rank(training_data, units)
		units = [unit.__repr__() for unit in units]
		print(' '.join(units))

main(args)