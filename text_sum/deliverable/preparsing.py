import pdb
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.corpus.reader.wordnet import WordNetError
from collections import OrderedDict
from functools import reduce

pruning_factor = 0.25
weight = 0.2


class Preparsing(object):
    def __init__(self, f):
        self.filename = f.split('.')[0]
        self.file = open(f, 'r')
        self.sentences = []
        self.total_words = 0
        self.total_nouns = 0
        self.total_sentences = 0
        self.word_usage = OrderedDict()
        self.term_sentence = []
        self.local_word_score = []
        self.total_score = 0.0
        self.global_score = []
        self.word_score = []
        self.sentence_scores = []
        self.all_sentences = []

        self.preprocessing()
        self.calc_local_word_score()
        self.word_pruning()
        self.calc_global_score()
        self.calc_word_score()
        self.sig_words()
        self.sentence_score()

    def to_json(self):
        return {
            'all_sentences': self.all_sentences,
            'sentences': self.sentences,
            'total_word': self.total_words,
            'total_nouns': self.total_nouns,
            'total_sentences': self.total_sentences,
            'word_usage': self.word_usage,
            'term_sentence': self.term_sentence,
            'local_word_score': self.local_word_score,
            'total_score': self.total_score,
            'global_score': self.global_score,
            'word_score': self.word_score,
            'sentence_scores': self.sentence_scores
        }

    def tokenize(self, sentence):
        return sentence.strip('.!?').split(' ')

    def remove_small(self, tokens):
        no_small = []
        for token in tokens:
            self.total_words += 1
            if token not in stopwords.words('english'):
                no_small.append(token)
        return no_small

    def nouns(self, tokens):
        # TODO: something better for identifying nouns
        nouns = []
        for word, pos in nltk.pos_tag(tokens):
            if pos in ['NN', 'NNP', 'NP', 'N']:
                nouns.append(word)
                self.total_nouns += 1
        return nouns

    def add_word_count(self, sentence):
        for word in sentence:
            if word in self.word_usage:
                self.word_usage[word] += 1
            else:
                self.word_usage[word] = 1

    def calc_local_word_score(self):
        count = 0
        for key in self.word_usage:
            self.local_word_score.append(weight * (self.word_usage[key] / self.total_words)
                                         + (1.0 - weight) * self.term_sentence[count])
            count += 1

    def similarity(self, key, global_word):
        try:
            k = wordnet.synset('{}.n.01'.format(key))
            gl = wordnet.synset('{}.n.01'.format(global_word))
        except WordNetError:
            return 0

        return k.path_similarity(gl)

    def calc_global_score(self):
        global_words = self.filename.replace('serverfile_', '').split('_')
        for key in self.word_usage:
            sum_of_sim = 0.0
            for global_word in global_words:
                sum_of_sim += self.similarity(key, global_word)
            self.global_score.append(sum_of_sim)

    def remove_word(self, k, i):
        # print('removing: {}'.format(k))
        self.total_nouns -= self.word_usage[k]
        del self.word_usage[k]
        del self.term_sentence[i]
        del self.local_word_score[i]

    def word_pruning(self):
        total_score = 0.0
        for local_score in self.local_word_score:
            total_score += local_score
        threshold = pruning_factor * total_score / self.total_nouns
        i = 0
        deleted = 0
        for key in list(self.word_usage):
            if self.local_word_score[i - deleted] < threshold:
                self.remove_word(key, i - deleted)
                deleted += 1
            i += 1

    def calc_word_score(self):
        for i in range(0, len(self.word_usage)):
            self.word_score.append(weight * self.local_word_score[i] + (1.0 - weight) * self.global_score[i])

    def sig_words(self):
        threshold = reduce(lambda x, y: x + y, self.word_score) / len(self.word_score)
        loop = True
        loop2 = True
        while loop:
            i = 0
            deleted = 0
            for key in list(self.word_usage):
                if self.word_score[i - deleted] < threshold:
                    self.remove_word(key, i - deleted)
                    loop2 = False
                    deleted += 1
                else:
                    i += 1

            if loop2:
                threshold = reduce(lambda x, y: x + y, self.word_score) / len(self.word_score)
            else:
                loop = False
            if len(self.word_usage) < 10:
                loop = False

    def sentence_local_score(self, sig_word, sentence):
        score = 0
        i = 0
        for word in sig_word:
            if word in sentence:
                score += 1
            i += 1
        return score / len(sig_word)

    def sentence_global_score(self, sig_word, sig_score, sentence):
        score = 0
        i = 0
        for word in sig_word:
            if word in sentence:
                score += sig_score[i]
            i += 1
        return score / len(sig_score)

    def sentence_score(self):
        i = 0
        for sentence in self.sentences:
            sentence_local = self.sentence_local_score(self.word_usage, sentence)
            sentence_global = self.sentence_global_score(self.word_usage, self.word_score, sentence)
            score = weight * sentence_local + (1.0 - weight) * sentence_global
            loc = i / len(self.sentences)
            if 0.33 < loc < 0.67:
                score *= 0.2
            else:
                score *= 0.4
            self.sentence_scores.append(score)
            i += 1

    def preprocessing(self):
        blob = self.file.read()
        self.all_sentences = nltk.sent_tokenize(blob.replace('\n', ' '))
        for all_sentence in self.all_sentences:
            tokens = self.tokenize(all_sentence)
            # self.all_sentences.append(tokens)
            # self.add_freq(tokens)
            short_tokens = self.remove_small(tokens)
            noun = self.nouns(short_tokens)

            self.sentences.append(noun)

        for sentence in self.sentences:
            self.add_word_count(sentence)
            self.total_sentences += 1

        # Term of sentences
        for key in self.word_usage:
            count = 0
            for sentence in self.sentences:
                if key in sentence:
                    count += 1
            self.term_sentence.append(count / self.total_sentences)
