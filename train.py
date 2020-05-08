#!/usr/bin/env python

import sys
import argparse

if sys.version_info < (3, 0):
	print("Spaceless Segmentation requires Python 3.0 and above.")
	exit(1)

parser = argparse.ArgumentParser(description='Spaceless Segmentation Trainer.')
parser.add_argument('-d', '--dict', help='dictionary file', required=True)
parser.add_argument('-t', '--training', help='file which trained data is obtained from.', required=True)
parser.add_argument('-i', '--input', help='input files', required=True, nargs='*')
parser.add_argument('-j', help='number of threads used', default=4, type=int)
parser.add_argument('-a', '--amend', help='option to amend training data instead of creating new training file', action='store_true')

args = vars(parser.parse_args())

from tokeniser import tokeniser, dict, training

import os

def read_lock():
	read_files = []
	if os.path.exists("train.lock"):
		lock_file = open("train.lock", 'r')
		for line in lock_file:
			line = line.strip()
			if line == "":
				continue
			read_files.append(line)
		lock_file.close()
	return read_files

def write_lock(read_files):
	lock_file = open("train.lock", 'w+')
	for read_file in read_files:
		lock_file.write("%s\n" % read_file)
	lock_file.close()

def main(args):
	print("Using %d threads." % args['j'])
	if args['amend']:
		print("Loading previous training data...")
		training_data = training.read_data(args['training'])
		read_files = read_lock()
	else:
		print("Creating new training file...")
		training_data = {}
		read_files = []	

	dictionary = dict.Dictionary(args['dict'])
	trainer = training.Trainer(dictionary, tokeniser.Tokeniser(dictionary)
, args['j'])
	linecount = 0
	for filepath in args['input']:
		if filepath in read_files:
			print("Skipping %s; already indexed." % filepath)
			continue

		try:
			i_file = open(filepath, 'r')
			lines = []
			for line in i_file:
				line = line.strip()
				if line == "":
					continue
				lines.append(line)
			i_file.close()

			print("Loaded %d lines from '%s'." % (len(lines), filepath))
			training_data = trainer.train(training_data, lines)
			print("Finished processing '%s'." % filepath)
			training.write_data(args['training'], training_data)

			read_files.append(filepath)
			write_lock(read_files)

			linecount += len(lines)
		except KeyboardInterrupt:
			break # we'll skip the for loop
	print("")
	print("Number of files processed: %d" % len(read_files))
	print("Total number of tokens in dictionary: %d" % len(training_data))
	print("Number of lines processed: %d" % linecount)

main(args)