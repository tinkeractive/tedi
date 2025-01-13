import sys
import os
import io
import re
import argparse
import tarfile
import json
import xml.etree.ElementTree
import xml.dom.minidom

class Parser:
	def __init__(
			self,
			segment_delimiter='\\\\[\r\n]*',
			element_delimiter='*'):
		self.segment_delimiter = segment_delimiter
		self.element_delimiter = element_delimiter

	def translate(self, segment, elements):
		result = {}
		if isinstance(segment, (str)):
			values = segment.split(self.element_delimiter)
		else:
			values = segment
		segment_id = values[0]
		values = values[1:]
		for i, v in enumerate(elements[segment_id]):
			if i<len(values):
				result[v[0]] = values[i]
			else:
				result[v[0]] = ''
		return result

	def get_interchange_type_segment(self, segments):
		return segments[0]

	def get_functional_group_segment(self, segments):
		return segments[1]

	def get_functional_group(self, segments, elements):
		segment = self.get_functional_group_segment(segments) 
		return self.translate(segment, elements)['GS01']

	def get_transaction_set_segment(self, segments):
		return segments[2]

	def get_transaction_set(self, segments, elements):
		segment = self.get_transaction_set_segment(segments) 
		return self.translate(segment, elements)['ST01'] 

	def valid_segment(self, schema_segments, segment):
		result = False
		segment_id = segment.split(self.element_delimiter)[0]
		if segment_id in ['ISA', 'GS', 'GE', 'IEA'] \
			or segment_id in schema_segments or segment_id == '':
			result = True
		return result

	def parse(self, document):
		segments = document.strip().split(self.segment_delimiter)
		# NOTE re.split removed since we should not be regex splitting
		# NOTE the segment delimiter specified in the edi, NOT a regex
		# segments = re.split(self.segment_delimiter, document.strip())
		segments = [x.strip() for x in segments]
		schema_path = os.path.dirname(__file__)
		schema_path = '.' if schema_path == '' else schema_path
		elem_file = schema_path + '/schema/x12/elements.json'
		with open(elem_file, 'r') as f:
			elements_raw = f.read()
		elements = json.loads(elements_raw) 
		func_group = self.get_functional_group(segments, elements)
		tran_set = self.get_transaction_set(segments, elements)
		tran_set_file = f'{schema_path}/schema/x12/{func_group}/{tran_set}.json'
		with open(tran_set_file, 'r') as f:
			schema_raw = f.read()
		schema = json.loads(schema_raw)
		schema_segments = re.findall(r'"([A-Z0-9]+)"', json.dumps(schema))
		# NOTE a segment delimiter may appear in item description
		# NOTE when this happens, item description to be split as if a segment
		# check for valid segments by inspecting first element of each segment
		decoded_segment_delimiter = self.segment_delimiter.encode().decode('unicode_escape') 
		for i, v in enumerate(segments):
			if not self.valid_segment(schema_segments, v):
				segments[i-1] = '{}{}{}'.format(
					segments[i-1],
					decoded_segment_delimiter,
					segments[i]
				)
				segments[i] = None
		segments = list(filter(None, segments))
		matrix = [x.split(self.element_delimiter) for x in segments] 
		envelope = matrix[:2] + matrix[-2:]
		tree = xml.etree.ElementTree.Element('EDI') 
		interchange = self.translate(envelope[0], elements) 
		interchange_tree = xml.etree.ElementTree.SubElement(
			tree,
			envelope[0][0],
			interchange
		)
		functional_group = self.translate(envelope[1], elements) 
		functional_group_tree = xml.etree.ElementTree.SubElement(
			tree.find('.//ISA'),
			envelope[1][0],
			functional_group
		)
		path = ['ISA','GS']
		stack = [schema]
		matrix = matrix[2:-1]
		cache = [interchange_tree, functional_group_tree]
		while len(matrix) > 1000:
			self.recurse(elements, cache, stack, matrix[:1000])
			matrix = matrix[1000:]
		self.recurse(elements, cache, stack, matrix[:1000])
		functional_group_trailer = self.translate(envelope[-2], elements)
		xml.etree.ElementTree.SubElement(
			cache[0],
			envelope[-2][0],
			functional_group_trailer
		)
		interchange_trailer = self.translate(envelope[-1], elements)
		xml.etree.ElementTree.SubElement(
			cache[0],
			envelope[-1][0],
			interchange_trailer
		)
		return cache[0]

	def recurse(self, elements, cache, stack, matrix):
		if 0 == len(matrix):
			return
		s = matrix.pop(0)
		el = xml.etree.ElementTree.Element(s[0], self.translate(s, elements)) 
		if s[0] in stack[-1].keys():
			if 'segments' in stack[-1][s[0]].keys():
				stack.append(stack[-1][s[0]]['segments'])
				cache.append(el) 
			else:
				cache[-1].append(el)
			self.recurse(elements, cache, stack, matrix)
		else:
			matrix = [s] + matrix
			if len(stack) > 1:
				stack.pop()
				tmp = cache.pop()
				cache[-1].append(tmp) 
			else:
				return
			self.recurse(elements, cache, stack, matrix)

def main():
	args = get_args() 
	with open(args.edi_file, 'r') as f:
		edi = f.read()
	segment_separator = edi[105]
	element_separator = edi[3]
	parser = Parser(segment_separator, element_separator) 
	parsed = parser.parse(edi)
	xml_string = xml.etree.ElementTree.tostring(parsed)
	dom = xml.dom.minidom.parseString(xml_string.decode('utf-8'))
	print(dom.toprettyxml())

def get_args():
	parser = argparse.ArgumentParser(description='EDI.')
	parser.add_argument('-f', '--edi_file', type=str, required=True)
	args = parser.parse_args()
	return args

if __name__ == '__main__':
	sys.setrecursionlimit(2000)
	sys.exit(main())
