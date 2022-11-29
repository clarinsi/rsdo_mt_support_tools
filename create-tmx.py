from lxml import etree
import csv
import random
csv.field_size_limit(100000000)

pairs = []
errors = 0

IN_FILE = "" # bilingual csv
OUT_FILE = ""

private_len = 0
with open(IN_FILE, "r") as f:
    r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_ALL)
    for line in r:
        if len(line) == 2:
            pairs.append(line)
        else:
            errors += 1


print(len(pairs))
print(errors)

random.shuffle(pairs)


NSMAP = {"xml": "http://www.w3.org/XML/1998/namespace"}

root = etree.Element("tmx", version="1.4", nsmap = NSMAP)
root.append( etree.Element("header", admin_lang="en", srclang="en", datatype="PlainText", creationtool="rsdotool", creationtoolversion="1.0", tmf="csv"))
root.append( etree.Element("body"))

for pair in pairs:

    tu = etree.SubElement(root[1], "tu")
    tuv_en = etree.SubElement(tu, "tuv", attrib={"{http://www.w3.org/XML/1998/namespace}lang":"en"})
    seg_en = etree.SubElement(tuv_en, "seg")
    seg_en.text = pair[0]
    tuv_sl = etree.SubElement(tu, "tuv", attrib={"{http://www.w3.org/XML/1998/namespace}lang":"sl"})
    seg_sl = etree.SubElement(tuv_sl, "seg")
    seg_sl.text = pair[1]
    #for i in range(texts):


#print(etree.tostring(root, encoding='unicode', pretty_print=True))

et = etree.ElementTree(root)
et.write(OUT_FILE, encoding="utf-8", xml_declaration=True, pretty_print=True)