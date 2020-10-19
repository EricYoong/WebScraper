from WebScrappingPython.services.tripAdvisorCrawlerService.scrapping import *


def Progress(window):
    if not gv.urls_que.unfinished_tasks == 0 and not gv.exitFlag:
        window.FindElement('update').Update(value=gv.urls_que.unfinished_tasks)
        # print(gv.urls_que.unfinished_tasks, 'unfinished task')
        time.sleep(1)
    else:
        window.FindElement('update').Update(value=gv.urls_que.unfinished_tasks)

def main_menu():
    layout = [
        [psg.Text(
            'Please choose a state or federal terrority as well as your catogories that you wish to scrape :')],
        [psg.Text('Please choose a state: ', size=(45, 1)), psg.InputCombo(('Kuala Lumpur', 'Perak', 'Penang Island',
                                                                            'Johor', 'Selangor', 'Sabah', 'Sarawak',
                                                                            'Kedah', 'Negeri Sembilan', 'Perlis',
                                                                            'Pahang', 'Terengganu', 'Kelantan',
                                                                            'Malacca', 'Putrajaya', 'Labuan',
                                                                            'Kampar'), key='state', size=(20, 5))],
        [psg.Text('Please choose a which catagories: ', size=(45, 1)),
         psg.InputCombo(("Hotels", "Restaurants", "Things To Do"), key='userChoice', size=(20, 5))],
        [psg.Submit(key='submit'), psg.Cancel(key='cancel'), psg.Text('',size=(5,1), key='update')]
    ]

    window = psg.Window('Web Scraper for Malaysia Tourism').Layout(layout)

    # class="section-loading noprint"

    while not gv.quit_flag:
        button, values = window.Read(timeout=10)
        Progress(window)

        gv.text_to_search = "{} in {}".format(values['userChoice'], values['state'])
        if button == "cancel" or button == "None":
            htm()
            atm()
            rtm()
            gv.quit_flag = True
            window.FindElement('submit').update(disabled=False)
            break
        elif button == "submit":
            gv.start_time = time.time()
            gv.timestr = time.strftime("%Y%m%d-%H%M%S")
            try:
                gv.reset_variable()
                window.FindElement('submit').update(disabled=True)
                scrapper = taScrappingService(window)
                scrapper.daemon = True
                scrapper.start()
                gv.startScrappingFlag = True
                print(gv.start_time)
            except TimeoutException:
                window.FindElement('submit').update(disabled=False)
                psg.PopupError("Unable to connect to google")

        if gv.urls_que.unfinished_tasks == 0 and not gv.startScrappingFlag:
            window.FindElement('submit').update(disabled=False)

        if gv.timeoutFlag and gv.startScrappingFlag:
            gv.timeoutFlag = False
            gv.startScrappingFlag = False
            window.FindElement('submit').update(disabled=False)
    if not gv.quit_flag:
        print("This is not exiting... Lolllll")

    window.Close()


def progressBar():
    progressBarLayout = [
        [psg.ProgressBar(max_value=100, key='progressBar')],
        [psg.Button('Cancel')]
    ]

    progressBarWindow = psg.Window('Loading...').Layout(progressBarLayout)
    while True:
        event, values = progressBarWindow.Read()
        if event is None or event == 'Cancel':
            break

    progressBarWindow.Close()


main_menu()
