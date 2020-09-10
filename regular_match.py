import re

# m = re.search('([a-zA-Z_0-9.-]{2,64}@[a-zA-Z0-9-]{2,200}\.[a-z]{2,6})', '我的邮箱是PaniiJian@outlook.com，和1025318325@qq.com')
email_pattern = re.compile('([1-9]\d{5}(?:1[9,8]\d{2}|20[0,1]\d)(?:0[1-9]|1[0-2])(?:0[1-9]|1[0-9]|2[0-9]|3[0,1])\d{3}[\dxX])')
print(email_pattern.findall('我的邮箱是AlgoRithM@outlook.com，和9865182517@qq.com, zhangsan@stu.hit.edu.cn，www.baidu.com，张三@me.com。下面就来看看33050119990124475x验证的正则表达式的检测成果吧。'))


class RegularFilter:
    def __init__(self, regular_format_address):
        self.patterns = []
        self.types = ['email', 'phone', 'id_18', 'car_id']
        try:
            regular_formats = open(regular_format_address, 'r', encoding='utf-8')
            for format in regular_formats:
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
            for word in words_list:
                sentence_replaced = sentence_replaced.replace(word, '*' * len(word))
        return sentence_replaced

    def file_filter(self, rf, wf, cf):
        try:
            read_file = open(rf, 'r', encoding='utf-8')
            write_file = open(wf, 'w', encoding='utf-8')
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


if __name__ == '__main__':
    RF = RegularFilter('regular.txt')
    print(RF.sentence_findall('我的邮箱是AlgoRithM@outlook.com, AlgoRithM@outlook.com，和9865182517@qq.com, zhangsan@stu.hit.edu.cn，www.baidu.com，张三@me.com。身份证是33050119990124475x，电话是13613060749，车牌号是浙E42184'))
    print(RF.sentence_replace('我的邮箱是AlgoRithM@outlook.com, AlgoRithM@outlook.com，和9865182517@qq.com, zhangsan@stu.hit.edu.cn，www.baidu.com，张三@me.com。身份证是33050119990124475x，电话是13613060749，车牌号是浙E42184'))
    RF.file_filter('raw.txt', 'filtered.txt', 'classify.txt')