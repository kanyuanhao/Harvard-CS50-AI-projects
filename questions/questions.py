import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    corpus = {}

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            with open(file_path, "r", encoding='utf8') as file:
                corpus[filename] = file.read()

    return corpus


def tokenize(document): 
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    sentence = document.lower()

    # remove punctuation
    for char in sentence:
        if char in string.punctuation:
            sentence = sentence.replace(char, " ")

    words = nltk.word_tokenize(sentence)

    # remove stopwords
    stopwords = nltk.corpus.stopwords.words("english")
    for word in words:
        if word in stopwords:
            words.remove(word)
    
    return words
  


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    docu_num = len(documents)
    idfs = {}
    for document in documents:
        for word in documents[document]:
            if word not in idfs:
                word_count = 0
                for document in documents:
                    if word in documents[document]:
                        word_count += 1
                idf = math.log(docu_num / word_count)
                idfs[word] = idf
    
    return idfs




def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    
    query = list(query)
    file_score = {}

    # calculate scores for each file
    for file in files:
        score = 0
        word_used = []
        for word in files[file]:
            if word in query and word not in word_used:
                tf = files[file].count(word)    # term frequency
                idf = idfs[word]
                tf_idf = tf * idf
                score += tf_idf
                word_used.append(word)
        file_score[file] = score
        
    top = dict(sorted(file_score.items(), key=lambda x:x[1], reverse = True)[:n])  # pick the n highest files
    topfiles = []
    for file in top:
        topfiles.append(file)

    return topfiles

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    query = list(query)
    sentence_score = {}
    
    for sentence in sentences:
        score = 0
        word_used = []
        qr = 0  #query term times
        for word in sentences[sentence]:
            if word in query and word not in word_used:
                idf = idfs[word]
                score += idf
                qr += 1
                word_used.append(word)
        qr_density = qr / len(sentences[sentence])
        sentence_score[sentence] = [score, qr_density]

    top = dict(sorted(sentence_score.items(), key=lambda x:(x[1][0], x[1][1]), reverse = True)[:n]) # sort by IDF first, and then query term density
    topsentences = []
    for sentence in top:
        topsentences.append(sentence)

    return topsentences


if __name__ == "__main__":
    main()
