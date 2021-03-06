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
import sys
import os
import re
from Bio import SeqIO

#################################################
def usage():
	print ('USAGE: python genbank_to_seed.py GenBank_file.gb organism_directory \n')

#################################################
def convert_contigs(argv):
	if len(argv) < 3:
		usage()
		return
	if '.' in argv[1]:
		gbk_file = argv[1] 
		org_dir = argv[2]
	else:
		gbk_file = argv[2] 
		org_dir = argv[1]

	try:
		cmd = 'mkdir '+ org_dir
		os.system(cmd)
	except:
		print ('Organism Directory: ',org_dir)
	
	try:
		f_contig = open(os.path.join(org_dir, 'contigs'),'w')
		f_func = open(os.path.join(org_dir, 'assigned_functions'),'w')

		os.mkdir(os.path.join(org_dir, 'Features'))
		os.mkdir(os.path.join(org_dir, 'Features/peg'))
		os.mkdir(os.path.join(org_dir, 'Features/rna'))

		f_peg = open(os.path.join(org_dir, 'Features/peg/tbl'), 'w')
		f_rna = open(os.path.join(org_dir, 'Features/rna/tbl'), 'w')
	except:
		print ('ERROR: Can\'t write file(s) in',org_dir)
		return

	name = ''
	seq = ''
	check_status = 0

	for seq_record in SeqIO.parse(gbk_file, "genbank"):
		try:
			name = seq_record.name.strip()
			if len(name)<3:
				name = seq_record.id.strip()
			seq = str(seq_record.seq.strip())
			seq = seq.upper()
			if seq.find('A')<0 and seq.find('C')<0 and seq.find('G')<0 and seq.find('T')<0:
				print ('In the GenBank file, the sequence is missing.')
				check_status = 1
				break
			f_contig.write('>'+name+'\n'+seq+'\n')
		except:
			print ('In the GenBank file, the sequence or contig_id is missing.')
			check_status = 1
			break

		# write some information about the genome
		orgout = open(os.path.join(org_dir, 'GENOME'), 'w')
		if 'source' in seq_record.annotations:
			orgout.write(seq_record.annotations['source'])
		elif 'organism' in seq_record.annotations:
			orgout.write(seq_record.annotations['organism'])
		else:
			sys.stderr.write("Couldn't find either source or organism so no information written\n")
		orgout.close()

		descout = open(os.path.join(org_dir, 'DESCRIPTION'), 'w')
		descout.write(seq_record.description)
		descout.close()

	  # for peg/tbl and assigned_functions
		records = seq_record.features

		if check_status == 1:
			break

		for r in records:
			if 'CD' in r.type.upper():
				try:
					id = r.qualifiers['locus_tag'][0]
					codon = name
				except:
					print ('In the GenBank file, for a gene, locus_tag is missing. locus_tag is required for each gene.\nPlease make sure that each gene has locus_tag and run the program again.')
					check_status = 1
					break
				try:
					function = r.qualifiers['product'][0]
				except:
					function = 'unknown'
				
				try:
					if r.strand == -1:
						start = str(r.location.nofuzzy_end)
						stop = str(r.location.nofuzzy_start+1)
					else:
						start = str(r.location.nofuzzy_start+1)
						stop = str(r.location.nofuzzy_end)
				except:
					print ('In the GenBank file, the location of a gene is missing.\nPlease make sure that each gene has its location and run the program again.')
					check_status = 1
					break
				
				f_peg.write(id+'\t'+codon+'_'+start+'_'+stop+'\n')
				f_func.write(id+'\t'+function+'\n')
				
			if 'RNA' in r.type.upper():
				try:
					id = r.qualifiers['locus_tag'][0]
					codon = name
				except:
					print ('In the GenBank file, for a gene/RNA, locus_tag is missing. locus_tag is required for each gene/RNA.\nPlease make sure that each gene/RNA has locus_tag and run the program again.')
					check_status = 1
					break

				try:
					function = r.qualifiers['product'][0]
				except:
					function = 'unknown'
				
				try:
					if r.strand == -1:
						start = str(r.location.nofuzzy_end)
						stop = str(r.location.nofuzzy_start+1)
					else:
						start = str(r.location.nofuzzy_start+1)
						stop = str(r.location.nofuzzy_end)
				except:
					print ('In the GenBank file, the location of a gene/RNA is missing.\nPlease make sure that each gene/RNA has its location and run the program again.')
					check_status = 1
					break

				f_rna.write(id+'\t'+codon+'_'+start+'_'+stop+'\t'+function+'\n')
				f_func.write(id+'\t'+function+'\n')

	f_contig.close()
	f_rna.close()
	f_func.close()
	f_peg.close()
	if check_status == 0:
		print ('Your GenBank file is successfully converted to the SEED format, which is located at',org_dir,'\nPlease use this directory to run PhiSpy.\n')
	else:
		print ('For your GenBank file, the SEED directory cannot be created.\nPlease check your GenBank file and run this program again.\n')
		try:
			#cmd = 'rm -fr '+ org_dir
			os.remove(org_dir+'/contigs')
			os.remove(org_dir+'/assigned_functions')
			os.remove(org_dir +'/Features/peg/tbl')
			os.remove(org_dir +'/Features/rna/tbl')
			os.rmdir(org_dir + '/Features/peg')
			os.rmdir(org_dir + '/Features/rna')
			os.rmdir(org_dir + '/Features')
			os.rmdir(org_dir)
		except:
			print ('Cannot remove',org_dir)
#################################################
if __name__== "__main__":
	convert_contigs(sys.argv)
	
	
