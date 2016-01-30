#!/usr/bin/python

#Su Doku solver

from SudokuPuzzle import SudokuPuzzle

import argparse
import sys
import wx

from itertools import product,ifilter
from bisect import insort_left,insort,bisect_left


parser = argparse.ArgumentParser(description='A Sudoku solver')
parser.add_argument('--input', nargs='?',type=argparse.FileType('r'),default=sys.stdin,
	help="An Input puzzle file.\nA Su Doku puzzle must be composed by 9 lines with 9 columns with numbers between 0 and 9, where 0 marks an open spot.\n Multiple puzzles can be solved on a single file, separated by a blank line each")

parser.add_argument('--verbose', action='store_true',help="Verbosely prints the steps taken to the solution")

parser.add_argument('--output', nargs='?',type=argparse.FileType('w'),default=sys.stdout,
	help="Output file to save the solutions. Defaults to standard output")

args = parser.parse_args()

game = 1
line_nr = 0
while True:
	sudoku_table=[]
	for x in range(9):		
		try:
			line=args.input.readline()			
			sudoku_line = [ int(line[i]) for i in xrange(9) ]
		except IndexError:
			msg = "Incorrect number of columns on line "+str(line_nr)+" (must have 9 columns)"
			sys.stderr.write("Error: " + msg + "\n")
			sys.exit(-1)
		except IOError:
			msg = "File ended before finishing a Su Doku table on line " + str(line_nr)
			sys.stderr.write("Error: " + msg + "\n")
			sys.exit(-2)
		except ValueError:
			msg = "Invalid value for a column detected on line " + str(line_nr)
			sys.stderr.write("Error: Invalid value for a column detected (numbers must be between 0 and 9)\n")
			sys.exit(-3)
		else:
			sudoku_table.append(sudoku_line)
			line_nr+=1

	sudoku = SudokuPuzzle(sudoku_table)

	sudoku.set_log(args.verbose,args.output)

	args.output.write("Game " + str(game) + "\n" + str(sudoku))

	sudoku.fill_unique_spots()

	sudoku.exhaustive_search()

	args.output.write("Solution:\n" + str(sudoku))
	game+=1	

	# try reading a blank line, if it doesn't, then all games were processed
	try:
		blank=args.input.readline()
		line_nr+=1
	except IOError:
		sys.exit(0)
	else:
		if blank.strip() is not '':
			sys.stderr.write("Error: Invalid marker for next sudoku table detected (must be a blank line)")
			sys.exit(-4)
			break
