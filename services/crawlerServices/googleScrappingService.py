from .googleWorkerCrawlerService import *
from .googleManagerCrawlerService import initiate_manager, terminate_manager


class googleScrappingService(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        start_time = time.time()
        try:
            try:
                start_scrapper()
            except StaleElementReferenceException:
                start_scrapper()
            except TimeoutException:
                start_scrapper()
            initiate_manager()
            terminate_manager()
            saveResult(gv.res_info_dic, gv.usr_info_dic, start_time)
            gv.startScrappingFlag = False
            #psg.Popup('Test Done')
        except TimeoutException:
            gv.timeoutFlag = True
