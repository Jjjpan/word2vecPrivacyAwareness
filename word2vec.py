import jieba

FR = open('test.txt', 'r', encoding='utf-8')
FW = open('wiki.zh.text.jian.cut', 'w', encoding='utf-8')
for sentence in FR:
    print(sentence)
    FW.write(sentence)




#FW.write(' '.join(sent_list))

FR.close()
FW.close()