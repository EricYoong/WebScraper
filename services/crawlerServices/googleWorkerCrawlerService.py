from .googleBaseCrawlerService import *


class GoogleCrawlerWorker(threading.Thread):
    def __init__(self, threadID, thread_name, manager_id, webdriver):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = thread_name
        self.manager_id = manager_id
        self.webdriver = webdriver

    def run(self):
        while not gv.worker_exit_flag[self.manager_id]:
            self.google_worker_job()
        print(self.name, 'exiting...')

    def google_worker_job(self):
        # gv.google_worker_lock[m_id].acquire()
        # cq_empty_flag = gv.comment_que[m_id].empty()
        # gv.google_worker_lock[m_id].release()
        # if not cq_empty_flag and not gv.timeout_flag[m_id]:
        if not gv.timeout_flag[self.manager_id]:
            try:
                review_col = gv.comment_que[self.manager_id].get(False)
                review_id = review_col.get_attribute("data-review-id")
                get_review_info(self.webdriver, review_col, self.manager_id, review_id)
                gv.comment_que[self.manager_id].task_done()
            except Queue.Empty:
                pass
            except ConnectionResetError:
                print("ConnectionResetError")
                review_col = gv.comment_que[self.manager_id].get(False)
                review_id = review_col.get_attribute("data-review-id")
                get_review_info(self.webdriver, review_col, self.manager_id, review_id)
                gv.comment_que[self.manager_id].task_done()
            except BrokenPipeError as broken:
                print(broken)
            except Exception as ec:
                print(ec)
            time.sleep(1)
