import WebScrappingPython.shared.globalVariable as gv
from WebScrappingPython.shared.globalModule import *


def GoogleProgress(window):
        if not gv.urls_que.unfinished_tasks == 0 and not gv.exitFlag:
            window.FindElement('update').Update(value=gv.urls_que.unfinished_tasks)
            # print(gv.urls_que.unfinished_tasks, 'unfinished task')
            time.sleep(1)
        else:
            window.FindElement('update').Update(value=gv.urls_que.unfinished_tasks)
        # print(gv.urls_que.unfinished_tasks, 'unfinished task')
        # self.window.FindElement('submit').Update(disabled=False)

