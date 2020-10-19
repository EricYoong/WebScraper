from .workerCrawlerHotelService import *

class TACrawlerManager(threading.Thread):
    def __init__(self, threadID, thread_name, urls_que):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = thread_name
        self.urls_que = urls_que
        self.worker_threads = []
        self.webdriver = getWebDriver()

    def run(self):
        self.webdriver.set_page_load_timeout(120)
        for j in range(gv.total_no_of_worker):
            w_thread = TACrawlerHotelWorker("W" + str(j), "Worker " + str(j), self.threadID, self.webdriver)
            w_thread.start()
            self.worker_threads.append(w_thread)
        crawl_data(self.name, self.threadID, self.urls_que, gv.comment_que[self.threadID], self.webdriver)
        gv.worker_exit_flag[self.threadID] = True
        [worker_thread.join() for worker_thread in self.worker_threads]
        self.webdriver.quit()
        print("Manager Exiting " + self.name)


def initiate_manager():
    gv.exitFlag = False
    no_of_manager = 0;
    gv.totalJobs = gv.urls_que.qsize()
    if gv.total_no_of_manager > gv.totalJobs:
        no_of_manager = gv.totalJobs
    else:
        no_of_manager = gv.total_no_of_manager

    for i in range(no_of_manager):
        thread = TACrawlerManager(i, "Manager " + str(i), gv.urls_que)
        thread.start()
        gv.crawler_thread_pool.append(thread)
    gv.urls_que.join()

def terminate_manager():
    gv.exitFlag = True
    print("Exit.....")
    [i.join() for i in gv.crawler_thread_pool]
    print("Exited!!")
