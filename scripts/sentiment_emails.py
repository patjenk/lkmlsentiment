"""
Run through the files in the archive and grab the sentiment score and place it into the archive.
"""
from datetime import datetime
from json import dumps, load
import nltk
import os
import requests


class Splitter(object):
    """
    split text into individual sentences.
    """

    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class PartOfSpeechTagger(object):
    """
    """

    def __init__(self):
        pass

    def part_of_speech_tag(self, sentences):
        """
        input format: list of lists of words
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        output format: list of lists of tagged tokens. Each tagged tokens has a
        form, a lemma, and a list of tags
            e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                    [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']), ('one', 'one', ['CARD'])]]
        """

        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos


class DictionaryTagger(object):

    def __init__(self, dictionary_filename):
        self.max_key_size = 0
        self.dictionary = {}
        fh = open(dictionary_filename, 'r')
        for line in fh:
            data = line.rsplit("\t", 1)
            self.dictionary[data[0]] = int(data[1])
            self.max_key_size = max(self.max_key_size, len(data[0]))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """
        tag_sentence = []
        sentence_length = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = sentence_length
        i = 0
        while (i < sentence_length):
            j = min(i + self.max_key_size, sentence_length) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    #self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = self.dictionary[literal]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence


def value_of(sentiment):
    if isinstance(sentiment, int):
        return sentiment
    return 0


class SentimentByWords():
    """
    Encapsulates the code to score a piece of text by word content. Taken largely from
    https://github.com/fjavieralba/basic_sentiment_analysis/blob/master/basic_sentiment_analysis.py
    """
    def __init__(self):
        self.splitter = Splitter()
        self.part_of_speech_tagger = PartOfSpeechTagger()
        self.dictionary_tagger = DictionaryTagger("dictionaries/AFINN-111.txt")

    def score(self, text):
        """
        Examine the positive and negative words and create a sentiment score.
        This is a VERY VERY naive score.
        """
        split_text = self.splitter.split(text)
        part_of_speech_tagged_sentences = self.part_of_speech_tagger.part_of_speech_tag(split_text)
        dictionary_tagged_sentences = self.dictionary_tagger.tag(part_of_speech_tagged_sentences)
        result = 0.0
        for sentence in dictionary_tagged_sentences:
            for current_token in sentence:
               result += value_of(current_token[2])
        return result


def sentimentize_text(text):
    """
    Send the text to text-processing.com and return a sentiment score.
    http://text-processing.com/docs/sentiment.html
    """
    req = requests.post("http://text-processing.com/api/sentiment/", data={'text': text})
    return req.json()


def sentiment_emails():
    """
    Go through each file in archive/ and compute the various sentiment values.

    The file lkml.2012.12.23.75.email.json is a notorious rant by Linus that is
    a good example of confrontational communication.
    """
    sentiment_by_words = SentimentByWords()
    archive_dir = "archive/"
    #filenames = ["lkml.2010.10.27.102.email.json","lkml.2012.12.23.75.email.json"]
    #for filenum, filename in enumerate(filenames):
    for filenum, filename in enumerate(os.listdir(archive_dir)):
        if filenum % 10 == 0:
            print datetime.now(), filenum
        if filename.endswith(".email.json"):
            full_filename = os.path.join(archive_dir, filename)
            fh = open(full_filename, "r")
            email_data = load(fh)
            fh.close()

            modified = False

            if "naive-word-sentiment" not in email_data and "clean_body" in email_data:
                email_data["naive-word-sentiment"] = sentiment_by_words.score(email_data['clean_body'])
                modified = True

            if False and "tp.com-sentiment" not in email_data and "clean_body" in email_data:
                email_data['tp.com-sentiment'] = sentimentize_text(email_data['clean_body'])
                modified = True

            if modified:
                fh = open(full_filename, "w")
                fh.write(dumps(email_data))
                fh.close()


if __name__ == "__main__":
    sentiment_emails()
