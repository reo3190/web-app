import MeCab
import gensim
import numpy as np
# from gensim.models import KeyedVectors
# from gensim.models.word2vec import Word2Vec
import time

mt = MeCab.Tagger('')
#model = gensim.models.word2vec.Word2Vec.load("./static/word2vec.gensim.model")
model_dir = './static/entity_vector.model.bin'
# model = Word2Vec.load("./static/word2vec.gensim.model")
model = gensim.models.KeyedVectors.load_word2vec_format(model_dir, binary=True)

# テキストのベクトルを計算
def get_vector(text):
    sum_vec = np.zeros(200)
    word_count = 0
    node = mt.parseToNode(text)
    while node:
        fields = node.feature.split(",")
        # 名詞、動詞、形容詞に限定
        if fields[0] == '名詞' or fields[0] == '動詞' or fields[0] == '形容詞':
            if node.surface in model.wv:
                sum_vec += model[node.surface]
                word_count += 1
                #print("hit:" + node.surface)
            
        node = node.next

    return sum_vec / word_count


# cos類似度を計算
def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


# if __name__ == "__main__":

#     start = time.time()

#     v1 = get_vector('高橋怜生')
#     v2 = get_vector('歴史')
#     v3 = get_vector('科学')

#     print(cos_sim(v1, v2))
#     print(cos_sim(v1, v3))
#     print(time.time() - start)