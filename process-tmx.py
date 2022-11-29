### get text from tmx files

import argparse
from lxml import etree
import re
import os.path
import csv
from slugify import slugify

def get_nodes(file):
    tree = etree.parse(file)
    root = tree.getroot()
    srcLang = root[0].attrib['srclang']
    langNodes = root.xpath('//tuv')
    langs = list(set([node.attrib['{http://www.w3.org/XML/1998/namespace}lang'] for node in langNodes]))
    langs.remove(srcLang)
    nodes = root.xpath('//tu')
    print('have nodes', len(nodes))
    return nodes, srcLang, langs

def get_text(node):
    text = ''.join(node.itertext()).replace('{}', '')
    text = re.sub(r'<.*?>', '', text)

    return text

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='file name')
    parser.add_argument('-o', '--outdir', help='file name')

    args = parser.parse_args()
    filename = args.file
    outdir = args.outdir


    nodes, srcLang, langs = get_nodes(filename)

    texts = {}
    for lang in langs:
        for node in nodes:
            nodeLangs = node.xpath('//tuv')
            nodeLangs = list(set([langNode.attrib['{http://www.w3.org/XML/1998/namespace}lang'] for langNode in nodeLangs]))
            if lang in nodeLangs:
                source = get_text(node.xpath('tuv[@xml:lang="{}"]/seg'.format(srcLang))[0]).strip()
                target = get_text(node.xpath('tuv[@xml:lang="{}"]/seg'.format(lang))[0]).strip()
                if lang not in texts:
                    texts[lang] = [(source, target),]
                else:
                    texts[lang].append((source, target))

    for lang in texts:
        with open(os.path.join(outdir, srcLang + '-' + lang + '_' + slugify(filename.split('/')[-1]) + '.csv'), 'w') as outfile:
            w = csv.writer(outfile, delimiter = '\t', quoting=csv.QUOTE_ALL)
            w.writerows(texts[lang])

