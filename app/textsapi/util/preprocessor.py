from nltk.tokenize import sent_tokenize, word_tokenize


def preprocess(text):
    sentences = sent_tokenize(text)
    preprocessed = []

    for sent in sentences:
        preprocessed.append("\n".join(word_tokenize(sent)))

    preprocessed = "\n\n".join(preprocessed)

    return preprocessed
