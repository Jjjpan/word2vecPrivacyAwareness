# -*- coding: UTF-8 -*-
import jieba
import jieba.posseg
import jieba.analyse
import gensim
import re
import os
import sys

import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename, level='info', when='D',backCount=3,
                 fmt='%(asctime)s - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)


class RegularFilter:

    def __init__(self, regular_format_address):
        self.patterns = []
        self.types = ['email', 'phone', 'id_18', 'car_id']
        self.log = Logger('RF.log', level='debug')
        try:
            regular_formats = open(regular_format_address, 'r', encoding='utf-8')
            self.log.logger.info("Opened file:" + regular_format_address)
            for format in regular_formats:
                # print(format)
                pattern = re.compile(format.strip('\n'))
                self.patterns.append(pattern)
            self.log.logger.info("Set regular types: ['email', 'phone', 'id_18', 'car_id']")
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
                    result = item[0]
                    info = ' '.join(item[1])
                    classify_file.write(result + ' ' + info + '\n')
                classify_file.write('\n')
            self.log.logger.info("Sentence is covered by symbol *.")
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
        self.log = Logger('NF.log', level= 'debug')

    def dic_init(self):
        self.log.logger.info("Read extended dictionary from file: "+ self.rf)
        for keyword in open(self.dic, encoding='utf-8'):
            self.keywords.append(keyword.strip('\n'))
        self.log.logger.info("Dictionary has been read.")

    def word_split(self):
        res = []
        for sentence in open(self.rf, encoding='utf-8'):
            sentence_splited = jieba.posseg.cut(sentence.strip())
            res.append(sentence_splited)
        self.log.logger.info("Sentence cut by Prefix dict of dumping model: jieba.cache.")
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

        try:
            RF = RegularFilter("regular.txt")
            RF.file_filter(self.rf, regular_filtered, "download/classify.txt")
            self.log.logger.info("Regular filtered in download/classify.txt")
            write_file = self.wf
            output = open(write_file, 'w', encoding='utf-8')
            filtered_file = open(filtered, 'w', encoding='utf-8')
            input = open(self.rf, 'r', encoding='utf-8')
            input_RF = open(regular_filtered, 'r', encoding='utf-8')
            sentence_sensed_results = self.sense()
            for sentence_sensed_result, sentence_orign, sentence, sentence_splited in zip(sentence_sensed_results, input, input_RF, self.word_split()):
                output.write(sentence_orign.strip('\n') + ' ')
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
                for w in sentence_words:
                    sentence_filtered = sentence_filtered.replace(w, '*' * len(w))
                filtered_file.write(sentence_filtered)
            output.close()
            input.close()
            filtered_file.close()
            self.log.logger.info("Input has been filtered by extended user's dictionary, result in " + self.wf)

        except IOError:
            print("文件读写异常")


class Dictionary:
    def __init__(self, user_defined_dic, dictionary):
        self.log = Logger('DIC.log', level='debug')
        self.log.logger.info("Start loading model [wiki.zh.text.model].")
        self.model = gensim.models.Word2Vec.load("语料库/wiki.zh.text.model")
        self.log.logger.info("Loaded model from wiki.zh.text.model with dimension 200.")
        self.entries = set()
        try:
            user_dic = open(user_defined_dic, 'r', encoding='utf-8')
            dic_ex = open(dictionary, 'w', encoding='utf-8')
            self.log.logger.info("Extending user's dictionary.")
            for entry in user_dic:
                entry = entry.strip('\n')
                entry_extend = self.word_extend(entry)
                entry_extend.append(entry)
                for word in entry_extend:
                    self.entries.add(word)
                    dic_ex.write(word + '\n')

            user_dic.close()
            dic_ex.close()
            self.log.logger.info("Extended dictionary is built.")
        except IOError:
            print("读写文件异常")

    def word_extend(self, word):
        res = []
        most_simular_words = self.model.wv.most_similar(word)
        for i in range(5):
            res.append(most_simular_words[i][0])
        return res


if __name__ == "__main__":
    Dic = Dictionary('upload/user_dic.txt', 'download/dictionary.txt')
    filter = NormalFilter("upload/input.txt", "download/output.txt", "download/dictionary.txt")
    filter.dic_init()
    filter.filter("download/filtered.txt", "download/regular_filtered.txt")
