#!/usr/bin/env python
#############################################################################################
## PhiSpy is a computer program written in C++, Python and R to 
## identify prophages in a complete bacterial genome sequences.
##
## Initial versions of PhiSpy were written by
## Sajia Akhter (sajia@stanford.edu) PhD Student Edwards Bioinformatics Lab 
## (http://edwards.sdsu.edu/labsite/), Computational Science Research Center 
## (http://www.csrc.sdsu.edu/csrc/), San Diego State University (http://www.sdsu.edu/)
##
## Improvements, bug fixes, and other changes were made by
## Katelyn McNair Edwards Bioinformatics Lab (http://edwards.sdsu.edu/labsite/) 
## San Diego State University (http://www.sdsu.edu/)
## 
## The MIT License (MIT)
## Copyright (c) 2016 Rob Edwards
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
## 
## Improvements, bug fixes and other changes (2019) were made by forking the github version: 
## - Conversion from python2 -> python3
## - Add prophage.tbl
## - Simplification of code and integration into BacterialGenotyper
##
#############################################################################################
import os
import sys
import re
import subprocess
import argparse

## get file path
toolDir = os.path.dirname(os.path.realpath(__file__)) + '/'
INSTALLATION_DIR = toolDir
sys.path.append(toolDir)

## load modules
from PhiSpy_tools import makeTest
from PhiSpy_tools import classification
from PhiSpy_tools import evaluation
from PhiSpy_tools import unknownFunction

#################################################
def call_phiSpy(organismPath, output_dir, trainingFlag, INSTALLATION_DIR, evaluateOnly, threshold_for_FN,
				phageWindowSize, quietMode, keep):

	sys.stderr.write("Running PhiSpy on " + organismPath + "\n")
	if (not evaluateOnly):
		if (quietMode == 0):
			print ('Making Test Set... (need couple of minutes)')

		my_make_test_flag = makeTest.call_make_test_set(organismPath, output_dir, INSTALLATION_DIR)
		if (my_make_test_flag == 0):
			print ('The input organism is too small to predict prophages. Please consider large contig (having at least 40 genes) to use PhiSpy.')
			return
		if (quietMode == 0):
			print ('Start Classification Algorithm')
		classification.call_classification(organismPath, output_dir, trainingFlag, phageWindowSize, INSTALLATION_DIR)

		if (quietMode == 0):
			print ('Done with classification Algorithm')

		###### added in this version 2.2 ##### 
		if (trainingFlag == 0):
			if (quietMode == 0):
				print ('As training flag is zero, considering unknown functions')
			unknownFunction.consider_unknown(output_dir)
		######################################

	if (quietMode == 0):
		print ('Start evaluation...')
	evaluation.call_start_end_fix(output_dir, organismPath, INSTALLATION_DIR, threshold_for_FN, phageWindowSize)
	if (quietMode == 0):
		print ('Done!!!')

#################################################
def print_list():
	printstr = ''
	try:
		f = open(INSTALLATION_DIR + "/data/trainingGenome_list.txt", "r")
	except:
		print ('cannot find list')
	for line in f:
		line = line.strip()
		temp = re.split('\t', line)
		if int(temp[3]) == 1:
			printstr = printstr + temp[0] + ' ' + temp[2] + '\n'
	print (printstr)
	f.close()

#################################################
def start_propgram(argv):
	## check Rscript is installed
	args_parser = argparse.ArgumentParser(
		description="phiSpy is a program for identifying prophages from among microbial genome sequences",
		epilog="(c) 2008-2018 Sajia Akhter, Katelyn McNair, Rob Edwards, San Diego State University, San Diego, CA")
	args_parser.add_argument('-t', '--training_set', default=0, type=int,
							 help='Choose a training set from the list of training sets.')
	args_parser.add_argument('-l', '--list', type=bool, default=False, const=True, nargs='?',
							 help='List the available training sets and exit')
	args_parser.add_argument('-c', '--choose', type=bool, default=False, const=True, nargs='?',
							 help='Choose a training set from a list (overrides -t)')
	args_parser.add_argument('-e', '--evaluate', type=bool, default=False, const=True, nargs='?',
							 help='Run in evaluation mode -- does not generate new data, but reruns the evaluation')
	args_parser.add_argument('-n', '--number', default=5, type=int,
							 help='Number of consecutive genes in a region of window size that must be prophage genes to be called')
	args_parser.add_argument('-w', '--window_size', default=30, type=int,
							 help='Window size of consecutive genes to look through to find phages')
	args_parser.add_argument('-i', '--input_dir', help='The input directory that holds the genome')
	args_parser.add_argument('-o', '--output_dir', help='The output directory to write the results')
	args_parser.add_argument('-qt', '--quiet', type=bool, default=False, const=True, nargs='?',
							 help='Run in quiet mode')
	args_parser.add_argument('-k', '--keep', type=bool, default=False, const=True, nargs='?',
							 help='Do not delete temp files')

	args_parser = args_parser.parse_args()

	if (args_parser.list):
		print_list()
		sys.exit(0)

	if not args_parser.input_dir and not args_parser.output_dir:
		print(sys.argv[0] + " [-h for help] [-l to list training sets] OPTIONS")
		print("Input and output directories are required")
		sys.exit(0)

	output_dir = args_parser.output_dir
	organismPath = args_parser.input_dir
	trainingFlag = args_parser.training_set

	output_dir = output_dir.strip()
	if output_dir[len(output_dir) - 1] != '/':
		output_dir = output_dir + '/'
	try:
		f = open(output_dir + 'testing.txt', 'w')
	except:
		try:
			os.makedirs(output_dir)
			f = open(output_dir + 'testing.txt', 'w')
		except:
			print ("Cannot create the output directory or write file in the output directory", output_dir)
			return
	f.close()
	os.system("rm " + output_dir + 'testing.txt')

	organismPath = organismPath.strip()
	if organismPath[len(organismPath) - 1] == '/':
		organismPath = organismPath[0:len(organismPath) - 1]

	try:
		f_dna = open(organismPath + '/contigs', 'r')
		f_dna.close()
	except:
		print ("Cannot open", organismPath + '/contigs')
		return
	try:
		f = open(organismPath + '/Features/peg/tbl', 'r')
		f.close()
	except:
		print ("Cannot open", organismPath + '/Features/peg/tbl')
		return
	try:
		f = open(organismPath + '/assigned_functions', 'r')
		f.close()
	except:
		print ("Cannot open", organismPath + '/assigned_functions')
		# return
	try:
		f = open(organismPath + '/Features/rna/tbl', 'r')
		f.close()
	except:
		print ("Cannot open", organismPath + '/Features/rna/tbl')
		# return

	if (args_parser.choose):
		while (1):
			print_list()
			temp = raw_input(
				"Please choose the number for a closely related organism we can use for training, or choose 0 if you don't know: ")
			try:
				trainingFlag = int(temp)
			except:
				continue
			if trainingFlag < 0 or trainingFlag > 30:
				continue
			break
		print ()


	call_phiSpy(organismPath, output_dir, trainingFlag, INSTALLATION_DIR, args_parser.evaluate, args_parser.number,
				args_parser.window_size, args_parser.quiet, args_parser.keep)

#################################################
## main
#################################################
if __name__== "__main__":
	start_propgram(sys.argv)
