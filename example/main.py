import sys
import argparse
import tedi
import xml

def main():
	args = get_args()
	edi = sys.stdin.read()
	parser = tedi.Parser()
	parsed = parser.parse(edi)
	xml_string = xml.etree.ElementTree.tostring(parsed)
	if args.pretty_print:
		dom = xml.dom.minidom.parseString(xml_string)
		print(dom.toprettyxml())
	else:
		print(xml_string.decode('utf-8'))
	return 0

def get_args():
	parser = argparse.ArgumentParser('')
	parser.add_argument('-p', '--pretty_print', action=argparse.BooleanOptionalAction)
	return parser.parse_args()

if __name__ == '__main__':
	sys.setrecursionlimit(2000)
	sys.exit(main())
