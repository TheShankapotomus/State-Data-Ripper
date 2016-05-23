import csv
import os
import ast
import re
import bs4
from urllib import request
from html.parser import HTMLParser
from bs4 import BeautifulSoup

class SpecialSession:

	def __init__(self, input_file):

		self.congress, self.tag_order, self.defaults = [], [], []

		#get default values & urls to use
		with open(input_file, 'r') as input_data:

			for line in input_data:

				if("DEFAULTS:" in line):

					self.defaults = ast.literal_eval(line[10:])

				elif("HEADER:" in line):

					self.tag_order = ast.literal_eval(line[8:])

				else:

					self.congress.append(line)

	def scrape_table(self):

		members = []

		for chamber in self.congress:

			with request.urlopen(chamber) as page:

				parser = BeautifulSoup(page.read(), "html.parser")
				members += parser.find_all('tr', class_='dataRow')

		for data_set in self._tag_data(members):

			if len(data_set) > 6:

				yield self._populate(data_set[-4:])
			else:
				continue

	def _tag_data(self, table):

		for row in table:

			tag_data = []

			for tag in row.descendants:

				if(isinstance(tag, bs4.element.Tag)):

					tag_data.extend(data

										for data in tag.stripped_strings

											if data not in tag_data)

			yield [data for data in tag_data]

	def _populate(self, bs):

		clean_set = []
		party_map = {"D": "Democrat", "R": "Republican", "I": "Independent"}

		chamber = lambda ds: ['House', 'Representative'] if 'house' in ds else ['Senate', 'Senator']
		name = lambda str: [tkn for tkn in str.split("@")[0].split('.')]

		clean_set = [chamber(bs[3])[1],	   #Title
						name(bs[3])[0],    #First Name
						name(bs[3])[-1],   #Last Name
						party_map[bs[0]],  #Party
						chamber(bs[3])[0], #Chamber
						bs[1],			   #Street Address / Room Number
						"",				   #City
						"",				   #State
						"",				   #Zipcode
						bs[2],			   #Phone Number
						bs[3]]			   #Email

		for i in range(len(clean_set)):

			clean_set[i] = str(self.defaults[i] + clean_set[i])

		return clean_set

	def output(self, output_file):

		if(os.path.isfile(output_file) == False or os.stat(output_file).st_size != 0):

			open(output_file, 'w+').close()

		with open(output_file, 'r+', newline = '') as new_file:

			file = csv.writer(new_file, delimiter = ',')
			file.writerow(self.tag_order)

			for ds in self.scrape_table():

				file.writerow(ds)

if __name__ == "__main__":

	input_file = "input.txt"
	output_file = "Massachusetts.csv"

	ripper = SpecialSession(input_file)

	ripper.scrape_table()
	ripper.output(output_file)
