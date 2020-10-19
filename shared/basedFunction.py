from WebScrappingPython.shared.globalModule import *
import WebScrappingPython.shared.globalVariable as gv


def getWebDriver():
    if platform == "darwin":
        return WD.Chrome(executable_path="./../../Driver/chromedriver_mac", options=gv.options)
    elif platform == 'win32':
        return WD.Chrome(executable_path="./../../Driver/chromedriver.exe", options=gv.options)
    elif platform == 'linux' or platform == 'linux2':
        return WD.Chrome(executable_path="./../../Driver/chromedriver_linux", options=gv.options)


def saveResult(usr_infos_dic, start_time):
    gv.thread_queues_lock.acquire()
    try:
        ts_res_com = pd.DataFrame(usr_infos_dic)

        if os.path.isfile("../Result/{}-{}.csv".format(gv.text_to_search, gv.timestr)):
            with open(r"../Result/{}-{}.csv".format(gv.text_to_search, gv.timestr), 'a', encoding="utf-8", newline='') as file:
                ts_res_com.to_csv(file, mode='a', index=False, header=False)
        else:
            with open(r"../Result/{}-{}.csv".format(gv.text_to_search, gv.timestr), 'a', encoding="utf-8", newline='') as file:
                ts_res_com.to_csv(file, mode='a', index=False, header=True)

        str_output = "Done. Time taken is: {} \nSaved the file to {}-{}.csv\nThanks for using the tools".format(
        time.time() - start_time, gv.text_to_search, gv.timestr)
        print(str_output)
    except Exception:
        PrintException()

    gv.thread_queues_lock.release()

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


