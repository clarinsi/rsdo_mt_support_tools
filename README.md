# DS4-podporna-orodja

## Introduction
This repository contains various tools and scripts used to convert, process and prepare the texts received as part of the text collection activities in work package 4 of the Slovene in the Digital Environment project.

## pipeline.py

This script converts all pdfs in a folder to text, translates them with a machine translation service and then aligns them with Bleualign (https://github.com/rsennrich/Bleualign).

### Language support
The scripts supports English and Slovene, but can easily be adapted to other languages.

### Input
The script expects pairs of pdfs in a separate folder. For each pdf file, you need to add either `en` or `sl` to the end of the filename:
```
    filename_en.pdf
    filename_sl.pdf
```

### MT support
By default, the script uses the the RSDO machine translation service, but you can also switch to Google Translate (uncomment line 168). Note that you need to set up a Google Cloud account in order to use this functionality.

## process-tmx.py

This script converts tmx files into bilingual csv files.

## create-tmx.py

This script creates a tmx file from a bilingual csv

## anon.py

This script anonymises text using an external anonymisation service (e.g. https://gitlab.com/MAPA-EU-Project/mapa_project)