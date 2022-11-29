import sys
import os
import subprocess
import re
import fitz  
import classla
import unicodedata
import requests
from google.cloud import translate

GOOGLE_PROJECT = ""
RSDO_URL = ""
RSDO_USER = ""
RSDO_PASS = ""

#classla.download('sl') # uncomment on first run
# Also make sure you have Bleualign repository downloaded in project directory
# git clone https://github.com/rsennrich/Bleualign.git
nlp = classla.Pipeline('sl', processors='tokenize,ner,pos,lemma')


def print_log(message, end="\n"):
    print(message, end=end)
    sys.stdout.flush()


# removes prefix characters if are not part of the sentence
def cleane_line(s):
    #print(s, len(s))
    if len(s) == 0:
        return False
    eligible_character = 'ABCČDEFGHIJKLMNOPRSŠTUVZŽĐĆWQXY1234567890'
    svalid = False
    snew = s
    while not svalid:
        if len(snew) == 1:
            return ''#False
        if eligible_character.find(snew[0]) == -1:
            snew = snew[1:]
        else:
            svalid = True
    return str(snew)


def get_sentences(file):
    with fitz.open(file) as doc:
        text = ""
        page_counter = 0
        for page in doc:
            page_counter += 1

            text += unicodedata.normalize("NFKC", page.getText())

        text = re.sub(r'(\s[Pp])(ribl.)(\s)', '\g<1>ribližno\g<3>', text)

        chunks = []
        prev_chunk = ""
    
        for line in text.split('\n'):
            if line.strip() == "": 
                continue
            if prev_chunk == "":
                prev_chunk = line
            elif prev_chunk.strip()[-1:] not in ('-', ',') and line[0] == line[0].upper() and not line[0].isdigit():
                chunks.append(prev_chunk)
                prev_chunk = line 
            else:
                if prev_chunk[-1:] == '-':
                    prev_chunk = prev_chunk.replace('-', '').strip() + line
                else:
                    prev_chunk += ' ' + line

        tokenized_text = []
        for c in chunks:
            doc = nlp(c)
            tokenized_text += [s[9:] for s in doc.conll_file.conll_as_string().split('\n') if s[:6] == '# text']

    return [cleane_line(s) for s in tokenized_text], page_counter


def translate_google(output_filename, sentences, src, target, TR_LEN=200):
    client = translate.TranslationServiceClient()
    project_id = GOOGLE_PROJECT
    parent = f"projects/{project_id}/locations/global"

    sentences = [i for i in sentences if i.strip() != '']

    out = []
    n = len(sentences)
    i = 0
    while n != len(out):
        req = {
                "parent": parent,
                "contents": sentences[len(out):len(out)+TR_LEN],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": src,
                "target_language_code": target,
            }
        if len(req['contents']) != 0: 
            response = client.translate_text(request=req)

        for tr in response.translations:
            out.append(tr.translated_text)

    with open(output_filename, 'w') as output_file:
        for s in out:
            if s.strip() == '':
                continue
            output_file.write(str(s) + '\n')
    return out

def translate_rsdo(output_filename, src, target):
    files = {
    'src': (None, src),
    'dst': (None, target),
    'type': (None, 'text/plain')
    }

    print(output_filename)

    files['data'] = (output_filename, open(output_filename, 'rb'))
    response = requests.post(RSDO_URL, files=files, auth=(RSDO_USER, RSDO_PASS))
    tr_file = open(output_filename.replace('.txt', '_tr.txt'), 'w')
    tr_file.writelines(response.text)

    tr_file.close()

if __name__ == '__main__':
    start_time = time.time()
    data_path = sys.argv[1]
    print('runnning pipeline on directory:', data_path)

    FILES = []

    for filename in os.listdir(data_path):
        # skip if file is not pdf
        if '.pdf' not in filename:
            continue
        filename = os.path.join(data_path, filename)
        print_log("Working on a file: {}".format(filename))

        # create txt file from pdf
        print_log(" parsing pdf: ", end="")
        sentences, _ = get_sentences(filename)
        output_filename = filename.replace('.pdf', '.txt')
        with open(output_filename, 'w') as output_file:
            for s in sentences:
                s = s.strip()
                s = s.replace('..', '')
                if s == '':
                    continue
                output_file.write(str(s) + '\n')
        print_log("DONE")

        FILES.append(output_filename)

        # translate
        print_log(" translating text: ", end="")
        target = output_filename
        if 'en' in target:
            target = target.replace('en', 'sl')
            src_lang = "en"
            target_lang = "sl"
        else:
            target = target.replace('sl', 'en')
            src_lang = "sl"
            target_lang = "en"
        #translated_sentences = translate_sentences(output_filename, sentences, src_lang, target_lang) #google
        translate_rsdo(output_filename, src_lang, target_lang) #rsdo
        
        print_log("DONE")


    # bluealign
    HEADER = ["English", "Slovenian", "Ratio"]
    DELIMITER = "|"
    for filename in FILES:
        print_log("running Bleualign on: " + filename)

        source = filename
        target = filename
        if 'en' in filename:
            target = target.replace('en', 'sl')
        else:
            target = target.replace('sl', 'en')
        srctotarget = source.replace('.txt', '_tr.txt')
        targettosrc = target.replace('.txt', '_tr.txt')
        output = source.replace('.txt', '_bleu.txt')

        #python3 bleualign.py -s ../data/9001557154_sl.txt -t ../data/9001557156_en.txt --srctotarget ../data/9001557154_sl_tr.txt -o ../data/bleu_output.txt
        command = 'python3 ' + os.getcwd() + '/Bleualign/bleualign.py ' 
        command += '--source=' + source + ' '
        command += '--target=' + target + ' '
        command += ' --srctotarget=' + srctotarget + ' '
        command += ' --targettosrc=' + targettosrc + ' '
        command += '--output=' + output + ' '
        print(command)
        os.system(command)
        print_log("DONE")

        print_log("creating csv file ", end="")
        source_file = open(output + '-s', 'r')
        target_file = open(output + '-t', 'r')
        csv_filename = output.replace('.txt', '.csv')

        with open(csv_filename, 'w') as output_file:
            source_line = source_file.readline().strip()
            target_line = target_file.readline().strip()
            
            output_file.write(DELIMITER.join(HEADER) + '\n')

            while source_line and target_line:
                line = []
                if 'en' in csv_filename:                
                    line = [source_line, target_line, str(len(source_line)/len(target_line))]
                else:
                    line = [target_line, source_line, str(len(target_line)/len(source_line))]

                output_file.write(DELIMITER.join(line) + '\n')
                source_line = source_file.readline().strip()
                target_line = target_file.readline().strip()

        source_file.close()
        target_file.close()

        print("--- %s seconds ---" % (time.time() - start_time))
        print_log("DONE\n\n")

