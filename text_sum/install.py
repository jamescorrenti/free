#!/usr/bin/python3

import nltk

def install_lib(lib):
    print('[+] Installing NLTK Library: {}'.format(lib))
    try:
        nltk.download(lib)
        print('[+] Completed installing NLTK Library: {}'.format(lib))
    except:
        print('[-] Issue installing NLTK Library: {}'.format(lib))

install_lib('punkt')
install_lib('stopwords')
install_lib('averaged_perceptron_tagger')
install_lib('wordnet')
