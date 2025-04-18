#!/usr/bin/env python

import xml.etree.ElementTree as ET
import base64
from typing import Iterable

def iterate_in_chunks(s, chunk_size):
	for i in range(0, len(s), chunk_size):
		yield s[i:i + chunk_size]

def flatten(items):
	for x in items:
		if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
			for sub_x in flatten(x):
				yield sub_x
		else:
			yield x

def insert_substring(original_string, substring, index):
	new_string = original_string[:index] + substring + original_string[index:]
	return new_string

def find_node_level(root, level=1):
	to_return = []
	for child in root.findall("node"):
		to_return.append([child, level])
		if child.findall("node"):
			to_return.append(find_node_level(child, level+1))
	return list(flatten(to_return))

def parse(xmlfile):
	tree = ET.parse(xmlfile)
	root = tree.getroot()

	nodes = find_node_level(root)

	MD = ""
	for parent in root.iter("node"):
		# print(child.tag, child.attrib, child.text)
		
		for node, level in iterate_in_chunks(nodes, 2):
			if parent == node:
				if level > 6: level = 6
				MD += "\n\n" + level * "#" + " " + parent.attrib["name"] + "\n\n"
		
		inserts = []
		txt = ""
		for child in parent.iter():			
			if child.tag == "table":
				tbl = []
				for i, row in enumerate(child):
					r = ""
					for j, col in enumerate(row):
						if not col.text: col.text = ""
						if j == 0:
							r += "| " + col.text
						else:
							r += " | " + col.text
					r += " |"
					tbl.append(r)
					if i == 0:
						r = ""
						for j, col in enumerate(row):
							if j == 0:
								r += "| " + "---"
							else:
								r += " | " + "---"
						r += " |"
						tbl.append(r)
				
				header = tbl[-1]		
				firstrow = tbl[0]
				tbl.remove(header)
				tbl.remove(firstrow)
				tbl.insert(0, header)
				tbl.insert(2, firstrow)
				
				# MD += "\n" + "\n".join(tbl) + "\n"
				inserts.append([child, int(child.attrib["char_offset"]), "\n\n\n" + "\n".join(tbl) + "\n"])
				
			if child.tag == "codebox":
				tosave = f"""
	```
	{child.text}
	```
	"""
				inserts.append([child, int(child.attrib["char_offset"]), tosave])
				
			if child.tag == "encoded_png":
				inserts.append([child, int(child.attrib["char_offset"]), "\n"+f"![](data:image/png;base64,{child.text})"+"\n"])
			
		for child in parent.findall("rich_text"):	
			if not child.text: child.text = ""
			txt += child.text
			for i in inserts:
				if len(txt) == i[1]:
					child.text = insert_substring(child.text, i[2], len(txt)-i[1])
					inserts.remove(i)
				elif len(txt) > i[1]:
					child.text = insert_substring(child.text, i[2], len(child.text)-len(txt)-i[1])
					inserts.remove(i)
			if "scale" in child.attrib:
				if child.attrib["scale"] == "h1":
					MD += "# " + child.text
				elif child.attrib["scale"] == "h2":
					MD += "## " + child.text
				elif child.attrib["scale"] == "h3":
					MD += "### " + child.text
				elif child.attrib["scale"] == "h4":
					MD += "#### " + child.text
				elif child.attrib["scale"] == "h5":
					MD += "##### " + child.text
				elif child.attrib["scale"] == "h6":
					MD += "###### " + child.text
				elif child.attrib["scale"] == "sup":
					MD += "^" + child.text + "^"
				elif child.attrib["scale"] == "sub":
					MD += "~" + child.text + "~"
					
			elif "weight" in child.attrib and not "style" in child.attrib:
				if child.attrib["weight"] == "heavy":
					MD += "**" + child.text + "**"
				
			elif "style" in child.attrib and not "weight" in child.attrib:
				if child.attrib["style"] == "italic":
					MD += "*" + child.text + "*"
				
			elif "style" in child.attrib and "weight" in child.attrib:
				if child.attrib["style"] == "italic" and child.attrib["weight"] == "heavy":
					MD += "***" + child.text + "***"
				
			elif "strikethrough" in child.attrib:
				if child.attrib["strikethrough"] == "true":
					MD += "~~" + child.text + "~~"
				
			elif "link" in child.attrib:
				if "webs " in child.attrib["link"]:
					MD += "[" + child.text + "](" + child.attrib["link"].replace("webs ", "") + ")"
				
			else:
				if "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" in child.text:
					MD += child.text.replace("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" , "***")
				else:
					MD += child.text.replace("•", "-").replace("◇", "-").replace("▪", "-").replace("→", "-").replace("⇒", "-")
	return MD

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser("cherrymd")
	parser.add_argument("xmlfile", help="The path to the .ctd (XML) file from CherryTree without password protection.")
	parser.add_argument("out", help="A path to save the output.")
	args = parser.parse_args()
	
	if not ".ctd" in args.xmlfile:
		print("The xmlfile should be a .ctd file !")
	else:
		MD = parse(args.xmlfile)
		with open(args.out, "w") as f:
			f.write(MD)
