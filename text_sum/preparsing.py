import pdb
import nltk
from nltk.corpus import stopwords

pruning_factor = 0.9


class PreParser(object):

    def __init__(self, f):
        self.file = open(f, 'r')

    def tokenize(self, sentence):

        return sentence.replace('\n', ' ').strip('.!?').split(' ')

    @staticmethod
    def remove_small(tokens):
        return [w for w in tokens if w not in stopwords.words('english')]

    @staticmethod
    def nouns(tokens):
        # TODO: something better for identifying nouns
        nouns = []
        for word, pos in nltk.pos_tag(tokens):
            if pos in ['NN', 'NNP', 'NP', 'N']:
                nouns.append(word)
        return nouns

    def preprocessing(self):
        processed = []
        blob = self.file.read()
        sentences = nltk.sent_tokenize(blob)
        for sentence in sentences:
            if not sentence:
                continue
            token = self.tokenize(sentence)
            short_tokens = self.remove_small(token)

            noun = self.nouns(short_tokens)
            if not noun:
                continue
            processed.append(noun)
        return processed

parser = PreParser('test.txt')
parsed = parser.preprocessing()
print(parsed)