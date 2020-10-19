from .baseCrawlerService import *

class TACrawlerHotelWorker(threading.Thread):
    def __init__(self, threadID, thread_name, manager_id, webdriver):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = thread_name
        self.manager_id = manager_id
        self.webdriver = webdriver

    def run(self):
        while not gv.worker_exit_flag[self.manager_id]:
            self.ta_worker_job()
        print(self.name, 'exiting...')

    def ta_worker_job(self):
        # gv.google_worker_lock[m_id].acquire()
        # cq_empty_flag = gv.comment_que[m_id].empty()
        # gv.google_worker_lock[m_id].release()
        # if not cq_empty_flag and not gv.timeout_flag[m_id]:
        counter = 0
        if not gv.timeout_flag[self.manager_id]:
            try:
                review_col = gv.comment_que[self.manager_id].get(False)
                get_review_info(self.webdriver, review_col, self.manager_id)
                gv.comment_que[self.manager_id].task_done()
            except Queue.Empty:
                pass
            except ConnectionResetError:
                print("ConnectionResetError")
                return
            except BrokenPipeError as broken:
                print(broken)
                return
            except Exception as ec:
                PrintException()
                print("{} - Manager {}".format(self.name, self.manager_id))
                try:
                    get_review_info(self.webdriver, review_col, self.manager_id)
                    gv.comment_que[self.manager_id].task_done()
                except Exception as ec:
                    time.sleep(1)
                    PrintException()
                    print("Second Error {} - Manager {}".format(self.name, self.manager_id))
                    gv.comment_que[self.manager_id].task_done()

                return

            time.sleep(1)
