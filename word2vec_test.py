import gensim

model = gensim.models.Word2Vec.load("wiki.zh.text.model")
result = model.most_similar(u"足球")
for e in result:
    print(e[0], e[1])