import glob
import MeCab
import re
import math

wakati = MeCab.Tagger() 

"""
必要なこと

1. Mecab をインストール

2. 「livedoor ニュースコーパス」をダウンロードして解凍する
https://www.rondhuit.com/download.html#ldcc

"""

documents = [
    # {"filename": None, "header": None, "news": None},
]


def extract_words(document):
    node = wakati.parseToNode(document)

    types = ["名詞", "形容詞", "動詞"]

    words = []
    while node:
        if node.feature.split(",")[0] in types:
            words.append(node.surface)

        node = node.next

    return words

text_paths = glob.glob("./text/*/*")
for i, path in enumerate(text_paths):
    with open(path) as f:
        document = f.read()

    lines = document.split("\n")
    header = "\n".join(lines[0:2])
    body = "\n".join(lines[2:])

    documents.append({
        "filename": path,
        "header": header,
        "news": body,
        "words": extract_words(body)
    })
    
    if i >= 1000:  # 全部読むの長いから端折る
        break

print(i)

words_of_documents = [set(d["words"]) for d in documents]
def compute_tf_idf(words):
    keyword_counts = {k: 0 for k in set(words)}
    for k in words:
        keyword_counts[k] += 1

    results = {}
    for k in words:
        tf = keyword_counts[k] / sum(keyword_counts.values())
        
        k_contains = len([words for words in words_of_documents if k in words])
        idf = math.log(len(documents) / (k_contains + 1)) 

        tfidf = tf * idf
        results[k] = tfidf

    return results

def choice_keywords(document, choices=10):
    tf_idfs = compute_tf_idf(document)
    
    desc_sorted = sorted(tf_idfs.items(), key=lambda x:x[1], reverse=True)
    keywords = [k[0] for k in desc_sorted[0:choices]]
    return keywords


# add prime_words to documents
for d in documents:
    words = d["words"]
    keywords = choice_keywords(words)
    d["keywords"] = keywords


# show results
for i, d in enumerate(documents):
    print("filename:", d["filename"])
    print("Keywords:", d["keywords"])
    print("News:", d["news"])
    print("-------------------------------------------------------------------------")
    
    if i >= 10:
        break