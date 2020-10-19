from WebScrappingPython.shared.globalModule import *

# multi threaded setting for the scrapper
# no_size_threadpool = 8
no_size_threadpool = 20 # Control the number of the master thread to spawn
total_no_of_manager = no_size_threadpool
total_no_of_worker = 5 # Control the number of the worker thread to spawn

# Initialize data information Storage Variable
thread_queues_lock = threading.Lock()
restaurant_worker_lock = []
usr_info_dic = []
urls, url_retry = [], []
crawler_thread_pool = []

# Flag
exitFlag = False  # Exit flag for all the manager thread
interrupted = False  # See if is interupt by the user
quit_flag = False  # exit the program
startScrappingFlag = False
timeoutFlag = False

text_to_search = "Hotel Kampar"
urls_que = Queue.Queue()
no_index, totalJobs,  start_time = 0, 0, 0
timestr = ""

# tmp data information storage variable
tmp_dict, user_review_list = [], []
timeout_flag = []
worker_exit_flag = []
comment_que = []
user_review_list = []

# Initiate the value for all the array variable
[tmp_dict.append([]) for o in range(total_no_of_manager)]
[user_review_list.append([]) for o in range(total_no_of_manager)]
[timeout_flag.append(False) for o in range(total_no_of_manager)]
[worker_exit_flag.append(False) for o in range(total_no_of_manager)]
[comment_que.append(Queue.Queue()) for o in range(total_no_of_manager)]
[restaurant_worker_lock.append(threading.Lock()) for o in range(total_no_of_manager)]

options = Options()
prefs = {'profile.managed_default_content_settings.images':2}
options.add_experimental_option("prefs", prefs)
#options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument("--start-fullscreen")
options.add_argument("--no-proxy-server")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--dns-prefetch-disable")


def reset_variable():
    global thread_queues_lock
    global urls_que
    global res_info_dic
    global usr_info_dic
    global url_retry
    global tmp_dict
    global user_review_list
    global timeout_flag
    global worker_exit_flag
    global comment_que
    global exitFlag
    global no_index

    thread_queues_lock = threading.Lock()
    res_info_dic, usr_info_dic = [], []
    url_retry = []
    exitFlag = False
    no_index = 0
    urls_que = Queue.Queue()

    # Google worker variable
    tmp_dict, user_review_list = [], []
    timeout_flag, worker_exit_flag = [], []
    comment_que = []

    [tmp_dict.append([]) for o in range(total_no_of_manager)]
    [user_review_list.append([]) for o in range(total_no_of_manager)]
    [timeout_flag.append(False) for o in range(total_no_of_manager)]
    [worker_exit_flag.append(False) for o in range(total_no_of_manager)]
    [comment_que.append(Queue.Queue()) for o in range(total_no_of_manager)]
    [restaurant_worker_lock.append(threading.Lock()) for o in range(total_no_of_manager)]