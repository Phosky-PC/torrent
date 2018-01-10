import json
import time
from queue import Queue
from multiprocessing.dummy import DummyProcess
from torent.response import get_etree_page
from torent.config import START_URL


class spider(object):
    """
    初始化三个存放数据的队列
    """
    def __init__(self):
        # 存放url的队列
        self.url_queue = Queue()
        # 存放html的队列
        self.html_queue = Queue()
        # 存放数据的队列
        self.get_data_queue = Queue()

    # 获取全部url
    def get_url(self):
        for i in range(1, 11):
            self.url_queue.put(START_URL.format(i))

    # 获取网页源码
    def get_html(self):
        while True:
            url = self.url_queue.get()
            self.html_queue.put(get_etree_page(url))
            self.url_queue.task_done()

    # 解析网页源码获取数据
    def get_data(self):
        while True:
            html = self.html_queue.get()
            if html is not None:
                html_list = html.xpath('//*[@id="archiveResult"]/tr[position()>1]')
                data_list = []
                for data in html_list:
                    item = {}
                    item['title'] = data.xpath('./td[1]/text()')[0]
                    item['size'] = data.xpath('./td[2]/text()')[0]
                    item['update'] = data.xpath('./td[3]/text()')[0]
                    item['link'] = data.xpath('./td[4]/a[2]/@href')[0]
                    data_list.append(item)
                print(data_list)
                self.get_data_queue.put(data_list)
            self.html_queue.task_done()

    # 保存数据
    def save_data(self):
        while True:
            data_list = self.get_data_queue.get()
            if data_list is not None:
                with open('./data.json', 'a', encoding='utf-8') as f:
                    for data in data_list:
                        f.write(json.dumps(data, ensure_ascii=False, indent=2))
                        f.write(',\n\n')
            print('Save Successful')
            self.get_data_queue.task_done()

    def run(self):
        thread_list = []
        # 创建获取url地址的子线程
        t_url = DummyProcess(target=self.get_url)
        thread_list.append(t_url)

        # 创建获取html页面的子线程
        for i in range(86):
            t_html = DummyProcess(target=self.get_html)
            thread_list.append(t_html)

        # 创建获取数据的子线程
        for i in range(86):
            t_parse = DummyProcess(target=self.get_data)
            thread_list.append(t_parse)

        # 创建保存数据的子线程
        t_save = DummyProcess(target=self.save_data)
        thread_list.append(t_save)

        # 将所有子进程启动
        for t in thread_list:
            # 让主线程结束之后子线程页结束
            t.setDaemon(True)
            t.start()

        # 让主进程等待子进程结束在结束
        for q in [self.url_queue, self.html_queue, self.get_data_queue]:
            q.join()

        print('\nCrawl Over...')
        print("Crawl Time:", time.clock())

if __name__ == '__main__':
    spider = spider()
    spider.run()