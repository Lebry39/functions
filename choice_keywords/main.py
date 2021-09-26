import glob
import MeCab
import re
import math
import unicodedata

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
    document = unicodedata.normalize("NFKC", document)
    node = wakati.parseToNode(document)

    main_features = ["名詞", "形容詞", "動詞"]
    connect_features = ["助詞"]

    words = []
    while node:
        feature = node.feature.split(",")[0]
        word = node.surface

        words.append({
            "word": word,
            "feature": feature
        })
        node = node.next

    """
    
    （名詞｜形容詞）＋助動？＋（名詞｜動詞｜形容詞）

    """

    results = []
    skip_words = 0
    for i, w in enumerate(words):
        if len(words) - 1 - 2 <= i:
            break

        if skip_words >= 1:
            skip_words -= 1
            continue

        if not w["feature"] in main_features:
            continue

        connected_word = w["word"]
        if words[i+1]["feature"] in ["名詞", "形容詞"]:  # 名詞＋名詞
            connected_word += words[i+1]["word"]
            skip_words += 1
            if words[i+2]["feature"] in main_features:  # 名詞＋名詞＋名詞
                connected_word += words[i+2]["word"]
                skip_words += 1

            results.append(connected_word)
            continue


        if words[i+1]["feature"] in connect_features:
            connected_word += words[i+1]["word"]
            if words[i+2]["feature"] in main_features:  # 名詞＋助詞＋名詞
                connected_word += words[i+2]["word"]
                results.append(connected_word)
                continue

        results.append(w["word"])

    return results

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
    
    # if i >= 100:  # 全部読むの長いから端折る
    #     break

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
for i, d in enumerate(documents):
    words = d["words"]
    keywords = choice_keywords(words)
    d["keywords"] = keywords

    print("filename:", d["filename"])
    print("Keywords:", d.get("keywords"))
    print("\nNews:", d["news"])
    print("-------------------------------------------------------------------------")

    if i >= 10:
        break
