# -*- coding: UTF-8 -*-
import jieba
import jieba.posseg
import jieba.analyse
import gensim
import re
import os
import sys


class RegularFilter:
    def __init__(self, regular_format_address):
        self.patterns = []
        self.types = ['email', 'phone', 'id_18', 'car_id']
        try:
            regular_formats = open(regular_format_address, 'r', encoding='utf-8')
            for format in regular_formats:
                # print(format)
                pattern = re.compile(format.strip('\n'))
                self.patterns.append(pattern)
        except IOError:
            print("文件读取失败")

    def sentence_findall(self, sentence):
        res = []
        for i in range(len(self.types)):
            regular_type = self.types[i]
            regular_pattern = self.patterns[i]
            result = regular_pattern.findall(sentence)
            res.append([regular_type, result])
        return res

    def sentence_replace(self, sentence):
        sentence_replaced = sentence
        match_res = self.sentence_findall(sentence)
        for result in match_res:
            words_list = result[1]
            # print(words_list)
            for word in words_list:
                sentence_replaced = sentence_replaced.replace(word, '*' * len(word))
        return sentence_replaced

    def file_filter(self, rf, wf, cf):
        try:
            read_file = open(rf, 'r', encoding='utf-8')
            # print('1')
            write_file = open(wf, 'w', encoding='utf-8')
            # print('2')
            classify_file = open(cf, 'w', encoding='utf-8')
            for sentence in read_file:
                sentence_replaced = self.sentence_replace(sentence)
                write_file.write(sentence_replaced)
                res = self.sentence_findall(sentence)
                for item in res:
                    result =item[0]
                    info = ' '.join(item[1])
                    classify_file.write(result + ' ' + info + '\n')
                classify_file.write('\n')
            read_file.close()
            write_file.close()
            classify_file.close()
        except IOError:
            print("文件读取失败")


class NormalFilter:
    def __init__(self, read_file, write_file, dictionary):
        self.rf = read_file
        self.wf = write_file
        self.dic = dictionary
        self.keywords = []

    def dic_init(self):
        for keyword in open(self.dic, encoding='utf-8'):
            self.keywords.append(keyword.strip('\n'))

    def word_split(self):
        res = []
        for sentence in open(self.rf, encoding='utf-8'):
            sentence_splited = jieba.posseg.cut(sentence.strip())
            res.append(sentence_splited)
        return res

    def sense(self):
        res = []
        for sentence in self.word_split():
            flag = 0
            words = []
            for x in sentence:
                if x.word in self.keywords:
                    flag = 1
                    words.append(x.word)
                '''
                if x.flag == 'nr' or x.flag == 'ns':
                    flag = 1
                    words.append(x.word)
                '''
            res.append([words, flag])
        return res

    def filter(self, filtered, regular_filtered):
        sentence_sensed_results = test_filter.sense()
        try:
            write_file = self.wf
            output = open(write_file, 'w', encoding='utf-8')
            filtered_file = open(filtered, 'w', encoding='utf-8')
            input = open(self.rf, 'r', encoding='utf-8')
            for sentence_sensed_result, sentence, sentence_splited in zip(sentence_sensed_results, input, self.word_split()):
                output.write(sentence.strip('\n') + ' ')
                sentence_flag = sentence_sensed_result[1]
                sentence_words = sentence_sensed_result[0]
                output.write(str(sentence_flag) + ' ')
                for word in sentence_words:
                    output.write(word + ' ')
                output.write('\n')

                words = []
                for x in sentence_splited:
                    if x.flag == 'nr' or x.flag == 'ns':
                        words.append(x.word)

                sentence_filtered = sentence
                for w in words:
                    sentence_filtered = sentence_filtered.replace(w, '*' * len(w))
                filtered_file.write(sentence_filtered)
            output.close()
            input.close()
            filtered_file.close()
            RF = RegularFilter("regular.txt")

            RF.file_filter(filtered, regular_filtered, "download/classify.txt")

        except IOError:
            print("文件读写异常")


class Dictionary:
    def __init__(self, user_defined_dic, dictionary):
        self.model = gensim.models.Word2Vec.load("语料库/wiki.zh.text.model")
        self.entries = []
        try:
            user_dic = open(user_defined_dic, 'r', encoding='utf-8')
            dic_ex = open(dictionary, 'w', encoding='utf-8')
            for entry in user_dic:
                entry_extend = self.word_extend(entry)
                entry_extend.append(entry)
                for word in entry_extend:
                    dic_ex.write(word + '\n')
                self.entries.append(entry_extend)

            user_dic.close()
            dic_ex.close()
        except IOError:
            print("读写文件异常")

    def word_extend(self, word):
        res = []
        most_simular_words = self.model.most_similar(word)
        for i in range(5):
            res.append(most_simular_words[i][0])
        return res


if __name__ == "__main__":
    Dic = Dictionary('upload/user_dic.txt', 'download/dictionary.txt')
    test_filter = NormalFilter("upload/input.txt", "download/output.txt", "download/dictionary.txt")

    test_filter.dic_init()
    # print(test_filter.keywords)
    sentence_sensed = test_filter.sense()

    # print(sentence_sensed)
    test_filter.filter("download/name_address_filtered.txt", "download/filtered.txt")
