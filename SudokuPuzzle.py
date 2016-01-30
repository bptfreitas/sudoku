#!/usr/bin/python

#Su Doku solver

import argparse
import sys

from copy import deepcopy
from itertools import product,ifilter
from bisect import insort_left,insort,bisect_left

def binary_search(x,a):
	i = bisect_left(a, x)
	if i != len(a) and a[i] == x:
		return True
	else:
		return False

class SudokuPuzzle:

	def __init__(self,matrix):
		if len(matrix)!=9:
			raise IndexError("Input matrix doesn't have 9 lines")

		for line in xrange(9):
			if len(matrix[line])!=9:
				raise IndexError("Input matrix doesn't have 9 columns on line"+str(line+1))

		for (l,c) in product(range(9),range(9)):
			if type(matrix[l][c])!=int:
				msg = "Element ("+str(l)+","+str(c)+") must be an integer between 0 and 9"
				raise TypeError(msg)
			
		self.__sudoku = matrix;
		self.__original = deepcopy(self.__sudoku)

		self.__log = False

	def set_log(self,opt,logfile):
		if type(opt)!=bool:
			raise TypeError("opt must be a Boolean value")
		self.__log = opt
		self.__logfile = logfile

	def get_logopt(self):
		return self.__log

	def get_logfile(self):
		return self.__logfile

	# Returns the value at position 'key'				
	def __getitem__(self,key):
		x = key[0]
		y = key[1]
		if type(x)!=int or type(y)!=int:
			raise AttributeError

		if x not in set(range(10)) or y not in set(range(10)):
			raise IndexError

		return self.__sudoku[x][y]

	# Returns 'value' at position 'key'. 'key' is a tuple (x,y), where x,y are matrixes coordinates
	def __setitem__(self,key,value):
		x = key[0]
		y = key[1]
		if type(x)!=int or type(y)!=int:
			raise AttributeError

		if ( x not in set(range(10)) ) or ( y not in set(range(10)) ):
			raise IndexError

		if value not in set(range(10)):
			raise ValueError

		self.__sudoku[x][y]=value

	# String representation of a Su Doku table for printing
	def __str__(self):
		string = ""
		for x in xrange(9):
			if x%3==0:
				string += ''.join([ "-" for s in xrange(25) ])
				string +='\n'
			for y in xrange(9):
				if y==0:
					string+='| '
				string+= str(self[x,y]) if self[x,y]!=0 else "*"
				if (y+1)%3==0:
					string+=' | '
				else:
					string+= " "
			string+="\n"
		string += ''.join([ "-" for s in xrange(25) ]) + '\n'

		return string

	# Searches if 'value' is present on 'line'
	# value: a number between 1 and 9
	# line: line to search, a number between 0 and 8
	def search_value_on_line(self,value,line):
		if line not in set(range(9)):
			raise IndexError

		if value not in set(range(1,10)):
			raise ValueError

		for y in xrange(9):
			if self[line,y]==value:
				return True
		return False

	# Searches if 'value' is present on column 'col'
	# value: a number between 1 and 9
	# col: column to search, a number between 0 and 8
	def search_value_on_col(self,value,col):
		if col not in set(range(9)):
			raise IndexError

		if value not in set(range(1,10)):
			raise ValueError

		for x in xrange(9):
			if self[x,col]==value:
				return True
		return False

	# Searches if 'value' is present on a 3x3 block of numbers
	# value: number between 1 and 9
	# bx: block row index, between 0 and 2
	# by: block column index, between 0 and 2
	def search_value_on_block(self,value,bx,by):
		if bx not in set(range(3)):
			raise IndexError

		if by not in set(range(3)):
			raise IndexError

		if value not in set(range(1,10)):
			raise ValueError

		for (x,y) in product(range(bx*3,bx*3+3),range(by*3,by*3+3)):
			if self[x,y]==value:
				return True

		return False
	
	# Returns a list of unique values that can be put into position (line,col)
	def find_uniques(self,line,col):
		if line not in set(range(9)):
			raise IndexError

		if col not in set(range(9)):
			raise IndexError

		uniques = []		
		for value in xrange(1,10):
			found_value = False	
			if debug:
				print "value=",value

			#eliminate 'value' if it appears col or line
			for z in xrange(9):
				if debug:
					print "\t", (z,col), "\t", (line,z)
				if self[z,col]==value or self[line,z]==value:
					found_value=True
					break

			if found_value:
				continue

			# eliminate 'value' if it appears on a block
			block_col = col//3
			block_line = line//3

			for (x,y) in product(range(block_line*3,block_line*3+3),range(block_col*3,block_col*3+3)):
				if debug:
					print "\t\t", (x,y), "=", self[x,y]
				if self[x,y]==value:
					found_value=True
					break

			if found_value:
				continue

			uniques.append(value)
		
		return uniques

	# Tests if puzzle has open spots to put numbers
	def has_open_spots(self):
		for (x,y) in product(range(9),repeat=2):
			if self[x,y]==0:
				return True
		return False

	# Tests if line is valid by testing if it has duplicate values
	def validade_line(self,line):
		if line not in set(range(9)):
			raise IndexError

		digits = range(1,10)
		for y in xrange(9):
			if self[line,y]!=0:
				try:
					digits.remove(self[line,y]);
				except:
					return False

		return True

	# Tests if column is valid by testing if it has duplicate values
	def validade_col(self,col):
		if col not in set(range(9)):
			raise IndexError

		digits = range(1,10)
		for x in xrange(9):
			if self[x,col]!=0:
				try:
					digits.remove(self[x,col]);
				except:
					return False

		return True

	# Tests if 3x3 block is valid by testing if it has duplicate values
	def validade_block(self,block_line,block_col):
		if block_line not in set(range(3)):
			raise IndexError

		if block_col not in set(range(3)):
			raise IndexError

		digits = range(1,10)
		for (x,y) in product(range(block_line*3,block_line*3+3),range(block_col*3,block_col*3+3)):
			#print "\t(",x,",",y , ")"
			if self[x,y]!=0:
				try:
					digits.remove(self[x,y]);
				except:
					return False
		return True

	# Tries to solve the puzzle by filling positions only if they have 1 possible value
	def fill_unique_spots(self):
		added_value=True
		while added_value:
			added_value=False

			for (x,y) in product(range(9),repeat=2):
				if self[x,y]==0:
					uniques = self.find_uniques(x,y)
					if len(uniques) == 1:
						self[x,y]=uniques[0]
						added_value=True
					else:
						block_line = x//3
						block_col = y//3	

						uniques2 = []
						for u in uniques:
							check_lines=check_col=False

							if x==3*block_line:
								check_lines=self.search_value_on_line(u,x+1) and self.search_value_on_line(u,x+2)
							elif x==3*block_line+1:
								check_lines=self.search_value_on_line(u,x-1) and self.search_value_on_line(u,x+1)
							elif x==3*block_line+2:
								check_lines=self.search_value_on_line(u,x-1) and self.search_value_on_line(u,x-2)
							else:
								raise Exception("Fatal error")
						
							if y==3*block_col:
								check_col=self.search_value_on_col(u,y+1) and self.search_value_on_col(u,y+2)
							elif y==3*block_col+1:
								check_col=self.search_value_on_col(u,y-1) and self.search_value_on_col(u,y+1)
							elif y==3*block_col+2:
								check_col=self.search_value_on_col(u,y-1) and self.search_value_on_col(u,y-2)
							else:
								raise Exception("Fatal error")

							if check_lines and check_col:
								uniques2.append(u)

						if len(uniques2)==1:
							self[x,y]=uniques2[0]
							added_value=True
						elif len(uniques2)>0:
							raise Exception("Fatal error");

	def test_values(self,position,stack_unused,stack_used):

		valid_position = False
		
		while len(stack_unused)>0:

			value = stack_unused[len(stack_unused)-1]			

			self[position]=value
				
			test_line = self.validade_line(position[0])
			test_col = self.validade_col(position[1])
			test_block = self.validade_block(position[0]//3,position[1]//3)
			
			#print test_line, " ", test_col, " ", test_block

			valid_position = (test_line and test_col and test_block)

			if valid_position:
				break
			else:				
				stack_used.append(stack_unused.pop())				
	
		if not valid_position:
			self[position]=0
		
		return [stack_unused,stack_used]

	# Solves the puzzle by exhaustive search on all solution space
	def exhaustive_search(self,open_spots={}):

		if open_spots == {}:
			# fills a dictionary where its keys are open coordinates on the puzzle
			# and values are the numbers can be put into them
			open_spots = {}
			for (x,y) in product(range(9),repeat=2):
				if self[x,y]==0:
					open_spots[(x,y)]= self.find_uniques(x,y)

			if len(open_spots)==0:
				return False

			pos = min(open_spots, key = lambda p: len(open_spots[p]))
			values = open_spots[pos]
			
			if self.get_logopt():
				msg = "Start: " + str(len(open_spots))
				self.get_logfile.write(msg+'\n')

			del open_spots[pos]

			for i in xrange(len(values)):
				val = values[i]
				self[pos]=val	

				if self.__log:
					print "+ " , len(open_spots)+1 , ": ", i+1, "/",len(values), "= ", pos, val

				found = self.exhaustive_search(open_spots)

				if found:
					return True

			return False
		else:
			last_open_spots = { k:v for k,v in open_spots.items() }

			# select next position;
			# remove it from the remaining positions to search;
			pos = min(last_open_spots, key = lambda p: len(last_open_spots[p]))
			values = list(last_open_spots[pos])

			del last_open_spots[pos]
			
			# for each possible number that can be put into position 'pos':
			# - test if it can be put into it
			# if it can: 
			# - remove the position from the list
			# - set 'pos' with that number,
			# - call recursively the function with the updated puzzle

			if self.get_logopt():
				msg ="-> Starting step"+str(len(last_open_spots)+1)+" choosing position "+str(pos)
				self.get_logfile().write(msg+'\n')
			
			for i in range(len(values)):
				val = values[i]
				self[pos]=val

				if self.get_logopt():
					msg = "+ Step "+str( len(last_open_spots)+1 ) + ", position "+ str(pos)+ ": testing value " 
					msg+= str(i+1) + "/" + str ( len(values) ) + "= " +str(val)
					self.get_logfile().write(msg+'\n')

				x = pos[0]
				y = pos[1]

				bx = x//3
				by = y//3

				line_ok = self.validade_line(x)
				col_ok = self.validade_col(y)
				block_ok = self.validade_block(bx,by)

				if (not line_ok) or (not col_ok) or (not block_ok):
					continue

				if len(last_open_spots)==0:
					return True
				
				new_open_spots = deepcopy(last_open_spots)

				invalid=False

				# filters out the selected 'val' on the list of possible values for positions with the 
				# same row, column or block as the selected position 'pos'
				for (line,col) in [ (l,c) for (l,c) in new_open_spots.keys() if l==x or c==y or ((l//3==bx) and (c//3==by)) ]:
					if binary_search(val,new_open_spots[line,col]):
						new_open_spots[line,col].remove(val)

						if self.get_logopt():
							msg = "\tRemoved: " + str(val) + " from " + str((line,col))
							msg += "(" + str( len(new_open_spots[line,col]) ) + ")\n"
							self.get_logfile().write(msg)

						if len(new_open_spots[line,col])==0:
							if self.get_logopt():
								msg = "\tPosition " + str((line,col)) + " became invalid, testing next value"
								self.get_logfile().write(msg+"\n")
							invalid=True
							break
				
				if invalid:
					continue
																						
				found = self.exhaustive_search(new_open_spots)
				if found:
					return True

			if self.get_logopt():
				msg = "- Going back to step" + str(len(open_spots))
				self.get_logfile().write(msg+"\n")
				
			#all possible values for 'pos' were tested:
			# - mark 'pos' as open again and go back on recursion, returning False
			self[pos]=0
			return False
