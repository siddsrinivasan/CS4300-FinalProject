import gc
import json
import scipy
import pickle
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

"""NOTE: this file contains a lot of random stuff from attempts to vectorize
the data. At present, only the vectorize function (immedietely below) and vectorize reddit are used.
There contains code to create a custom tfidf matrix but it is slow. There also
exists code to tfidf the all the news dataset."""

def vectorize():
    """
    The proper method to run to vectorize the reuters headlines.
    Handles both data cleaning and creating and saving the data neccesary
    to create the tfidf matrix a vectorize future queries.
    """
    news = pd.read_csv('data/reu_identifiers.csv', names=['date', 'id', 'title'],usecols=['id', 'title'])
    news = news[news['title'].isnull() == False]
    news = news.drop_duplicates(subset='title')
    news = news[news.title.str.contains('UPDATE') == False]
    news = news[news.title.str.contains('CORRECTED') == False]
    news = news[news.title.str.contains('CORRECTION') == False]
    news.index = np.arange(len(news))
    gc.collect()
    vectorizer = TfidfVectorizer(min_df=3, stop_words='english',  dtype=np.int16)
    gc.collect()
    X = vectorizer.fit_transform((title for title in news['title'])).astype(dtype=np.float16)
    gc.collect()
    matrix_ix_to_id = {}
    for ix, row in news.iterrows():
        matrix_ix_to_id[ix] = row['id']
    gc.collect()
    scipy.sparse.save_npz('tfidf_mat.npz', X)
    gc.collect()
    #pickle.dump(id_to_vec, open('reu_tfidf.p', 'wb'))
    with open('matrix_ix_to_id.json', 'w') as f:
        json.dump(matrix_ix_to_id, f)
    gc.collect()

    with open('vocab_to_ix.json', 'w') as f:
        json.dump(vectorizer.vocabulary_, f)
    gc.collect()
    np.save('idf_vals.npy', vectorizer.idf_)

def vectorize_reddit():
    """
    Method used to vectorize reddit data. Creates tfidf matrix,
    and saves useful information corresponding to the tfidf matrix.
    """
    data = pd.read_csv('data/reddit_data.csv', names=['date', 'score', 'number of comments', 'title', 'url'], skiprows=1)
    vectorizer = TfidfVectorizer(min_df=3, stop_words='english')
    titles = data['title']
    reddit_tfidf = vectorizer.fit_transform(title for title in titles)
    scipy.sparse.save_npz('reddit_tfidf_mat.npz', reddit_tfidf)

    mat_idx_to_tup = {}
    for idx, row in data.iterrows():
        tup = (row['date'], row['score'], row['number of comments'], row['url'])
        mat_idx_to_tup[idx] = tup

    with open('reddit_ix_to_tup.json', 'w') as f:
        json.dump(mat_idx_to_tup, f)
    f.close()

    with open('reddit_vocab_to_ix.json', 'w') as f:
        json.dump(vectorizer.vocabulary_, f)
    f.close()

    np.save('reddit_idf_vals.npy', vectorizer.idf_)

def reu_id_to_title():
    id_to_title = {}
    for ix, row in news.iterrows():
        id_to_title[row['id']] = row['title']
    with open('id_to_reu_headline.json', 'w') as f:
            json.dump(id_to_title, f)

def vectorize_reu_iden():
    helper = TfidfVectorizer(min_df=3, stop_words='english',  dtype=np.int16)
    tfidf_preprocessor = helper.build_preprocessor()
    tfidf_tokenizer = helper.build_tokenizer()

    news = pd.read_csv('data/reu_identifiers.csv', names=['date', 'id', 'title'],usecols=['id', 'title'])
    news = news[news['title'].isnull() == False]
    news = news[2283884:] #2016 on
    news.reindex(labels=np.arange(len(news)))
    gc.collect()

    article_tf = {}
    doc_freq = defaultdict(lambda : 0)
    unique_toks = set()
    for ix, story in news.iterrows():
        tf_dict = defaultdict(lambda : 0)
        tokens = tfidf_tokenizer(story['title'])
        story_unique_toks = set(tokens)

        for tok in tokens:
            tf_dict[tok] += 1

        for tok in story_unique_toks:
            unique_toks.add(tok)
            doc_freq[tok] += 1

        article_tf[story['id']] = tf_dict

    gc.collect()

    return article_tf, doc_freq, unique_toks


def create_tfidf(article_tf, doc_freq, unique_toks):
    word_to_ix = {}
    for ix, word in enumerate(list(unique_toks)):
        word_to_ix[word] = ix

    gc.collect()

    tfidf_dict = {}
    for term_freq in article_tf:
        tfidf_dict[doc] = {}
        for word in term_freq:
            tfidf_weight = term_freq[word] / doc_freq[word]
            tfidf_dict[doc][word_to_ix[word]] = tfidf_weight
    gc.collect()
    return tfidf_dict, word_to_ix, doc_freq



def tokenize(text):
    """Returns a list of words that make up the text.

    Note: for simplicity, lowercase everything.
    Requirement: Use Regex to satisfy this function

    Params: {text: String}
    Returns: Array
    """
    # YOUR CODE HERE
    lower = text.lower()
    tokens = re.findall('[a-z]+', lower)
    return tokens


def make_tf_dict(data):
    article_tf = {}
    unique_toks = set()
    for ix, article in data.iterrows():
        tf_dict = defaultdict(lambda: 0)
        tokens = tokenize(article['content'])
        for tok in tokens:
            tf_dict[tok] += 1
            unique_toks.add(tok)
        article_tf[article['id']] = tf_dict
    return article_tf, unique_toks


def iterate_data():
    dat1 = pd.read_csv('data/articles1.csv')
    dat2 = pd.read_csv('data/articles2.csv')
    dat3 = pd.read_csv('data/articles3.csv')

    article_tf1, unique_toks1 = make_tf_dict(dat1)
    article_tf2, unique_toks2 = make_tf_dict(dat2)
    article_tf3, unique_toks3 = make_tf_dict(dat3)

    unique_toks = unique_toks1.union(unique_toks2).union(unique_toks3)
    print('Unique Tokens:', len(unique_toks))
    article_tf = copy.copy(article_tf1.update(article_tf2).update(article_tf3))

    doc_freq = defaultdict(lambda: 0)

    for article in article_tf:
        for word in article:
            doc_freq[word] += 1


def custom_tfidf():
    article_tf, doc_freq, unique_toks = vectorize_reu_iden()
    tfidf_dict, word_to_ix, doc_freq = create_tfidf(article_tf, doc_freq, unique_toks)
    with open('tfidf_dict.json', 'w') as f:
        json.dump(tfidf_dict, f)
    with open('word_to_ix.json', 'w') as f:
        json.dump(word_to_ix, f)
    with open('doc_freq.json', 'w') as f:
        json.dump(doc_freq, f)

if __name__ == '__main__':
    vectorize_reddit()
