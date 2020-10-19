from WebScrappingPython.shared.basedFunction import *
import WebScrappingPython.shared.globalVariable as gv
from WebScrappingPython.shared.globalModule import *
from WebScrappingPython.services.crawlerServices.googleProgressService import GoogleProgress
from selenium.webdriver.common.action_chains import ActionChains

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

def crawl_data(threadName, threadID, urls_que, comment_ques, webdriver, worker_threads):
    t_id = threadID
    while not gv.exitFlag:
        webdriver.implicitly_wait(30)
        done, error = False, False
        time_out_counter = 0

        # gv.thread_queues_lock.acquire()
        # empty_que = urls_que.empty()
        # gv.thread_queues_lock.release()

        try:
            gv.timeout_flag[t_id] = False
            gv.user_review_list[t_id] = []
            gv.tmp_dict[t_id] = {'Name': ' ', 'Ranking': '', 'Address': ''}
            try:
                url = urls_que.get(False)
                while not error and not done:
                    try:
                        webdriver.get(url)
                        try:
                            WebDriverWait(webdriver, 20).until(
                                EC.presence_of_element_located((By.XPATH,
                                                                "//div[@class='section-hero-header-title-description"
                                                                "']/div[@jsinstance='*0']/h1"))
                            )
                        except NoSuchElementException:
                            print("I am", threadName, "no such element")
                        except TimeoutException:
                            print('Tttttttttttt')
                        else:
                            crawl_name(webdriver, gv.tmp_dict[t_id])
                            crawl_address(webdriver, gv.tmp_dict[t_id])
                            try:
                                # Crawl Overall review rate
                                crawl_review_rate(webdriver, gv.tmp_dict[t_id])
                                review_exist = True
                            except NoSuchElementException:
                                review_exist = False
                                # print(review_exist, "review_exist")
                            print(review_exist, "review_exist")

                            gv.tmp_dict[t_id]['URL'] = url

                            if review_exist:
                                counter = 0
                                while True:
                                    if get_review_ques(webdriver, comment_ques, t_id) or counter == 5:
                                        break;
                                    counter = counter + 1

                                numberOfWorker = 0
                                if comment_ques.qsize() >= gv.total_no_of_worker:
                                    numberOfWorker = gv.total_no_of_worker
                                else:
                                    numberOfWorker = comment_ques.qsize()
                            else:
                                gv.user_review_list[t_id].append({'Address': gv.tmp_dict[t_id]['Address'], 'Comment': 'No Comment'})

                    except TimeoutException as TEx:
                        print("Timeout Error", threadName, url)
                        if time_out_counter >= 1:
                            gv.url_retry.append(url)
                            gv.timeout_flag[t_id] = True
                            with comment_ques.mutex:
                                comment_ques.queue.clear()
                            error = True
                            urls_que.task_done()
                        elif time_out_counter < 1:
                            webdriver.refresh()
                        else:
                            pass

                        time_out_counter += 1
                    else:
                        comment_ques.join()
                        gv.res_info_dic.append(gv.tmp_dict[t_id])
                        gv.usr_info_dic.append(gv.user_review_list[t_id])
                        print("Done crawl ", gv.tmp_dict[t_id]['Name'],'\n', threadName)
                        done = True
                        urls_que.task_done()

                    if gv.interrupted:
                        print("Interrupted Gotta go")
                        break
                    print("This is total")
            except Queue.Empty:
                #print('Empty')
                raise Queue.Empty
        except Queue.Empty:
            time.sleep(1)


# Sub function to assist the main function for the google master thread. #

def crawl_review_rate(webdriver, tmp_dicts):
    finished = 0
    counter = 0
    while not finished:
        try:
            review_col = webdriver.find_element_by_xpath(
                "//span[@class='section-star-display' and @jsan='7.section-star-display,0.aria-hidden']")
            tmp_dicts['Ranking'] = review_col.get_attribute("textContent")
            # print(tmp_dicts['Ranking'])
            finished = 1
        except NoSuchElementException:
            if counter < 1:
                print("No review!")
            elif counter >= 1:
                print("No review xpath found", webdriver.current_url)
                tmp_dicts['Ranking'] = "0.0"
                finished = 1
                raise NoSuchElementException
            else:
                finished = 0
            counter += 1
        except TimeoutException:
            print("Time out crawl review")
            raise TimeoutException


def crawl_name(webdriver, tmp_dicts):
    finished = 0
    counter = 0
    while not finished:
        try:
            res_name_col = webdriver.find_element_by_xpath(
                "//div[@class='section-hero-header-title-description']/div[@jsinstance='*0']/h1")
            res_name = res_name_col.get_attribute("textContent")
            tmp_dicts['Name'] = res_name
            # print(tmp_dicts['Name'])
            finished = 1
        except NoSuchElementException:
            if counter < 1:
                print("No restaurant name")
            elif counter >= 1:
                print("No restuarant xpath found")
                print(webdriver.current_url)
                tmp_dicts['Name'] = "No Name"
                finished = 1
            else:
                finished = 0
            counter += 1
        except TimeoutException:
            print("Time out crawl name")
            raise TimeoutException


def crawl_address(webdriver, tmp_dicts):
    try:
        addr_col = webdriver.find_element_by_xpath(
            "//button[@data-item-id='address']/div/div[contains(@jsan, '7.ugiz4pqJLAG__text')]/div[contains(@jsan, '7.ugiz4pqJLAG__primary-text')]")
        addr_str = addr_col.get_attribute("textContent")
        tmp_dicts['Address'] = addr_str
    except NoSuchElementException:
        print('No Address for', tmp_dicts)


def scroll_review_section(webdriver):
    track_test = True
    while track_test:
        try:
            scroll_view = webdriver.find_element_by_xpath("//div[@jsan='t-WPtQSFf6msE,7.section-loading,7.noprint']")
            webdriver.execute_script("arguments[0].scrollIntoView();", scroll_view)
        except NoSuchElementException:
            track_test = False
            # print("At the most bottom")


def get_review_ques(webdriver, comment_ques, m_id):
    try:
        WebDriverWait(webdriver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@jsan='7.jqnFjrOWMVU__button,7.gm2-caption,0.ved,22.jsaction']"))
        )
    except TimeoutException:
        raise TimeoutException
    else:
        try:
            see_all_review = webdriver.find_element_by_xpath("//button[@aria-label ='See all reviews']")
            webdriver.execute_script("arguments[0].click()", see_all_review)
        except NoSuchElementException:
            print("See all Review Button is not exist")
            return False
        else:
            # Check if there other type of account
            # gv.only_google_acc_validator[m_id] = False
            try:
                reviews_parent = webdriver.find_element_by_xpath(
                    "//div[contains(@class, 'section-layout') and contains(@jsan, '7.section-layout')]")
            except NoSuchElementException:
                print("No reviews_parent")
                return False

            try:
                dropdownAccountType = webdriver.find_element_by_xpath(
                    "//div[contains(@role, 'menu') and @aria-label='All reviews']/div["
                    "@class='cYrDcjyGO77__dropdown-icon']")
                ActionChains(webdriver).move_to_element(dropdownAccountType).perform()
                ActionChains(webdriver).click(dropdownAccountType).perform()
                item_col1 = webdriver.find_elements_by_xpath(
                    "//div[contains(@id,'action-menu')]/ul/li")
                if len(item_col1) > 1:
                    # print(len(item_col1))
                    gv.only_google_acc_validator[m_id] = False
                else:
                    # print(len(item_col1))
                    gv.only_google_acc_validator[m_id] = True
            except NoSuchElementException:
                print('DropDown account type is not found')

            scroll_review_section(webdriver)

            try:
                reviews_parent = webdriver.find_element_by_xpath(
                    "//div[contains(@class, 'section-layout') and contains(@jsan, '7.section-layout')]")
            except NoSuchElementException:
                print("No reviews_parent")
                return False
            else:
                # print("Found parent")
                try:
                    reviews = reviews_parent.find_elements_by_xpath(
                        "//div[contains(@class, 'section-review ripple-container')]")
                except NoSuchElementException:
                    print("No reviews_parent")
                else:
                    #for review in reviews:
                    #    review_id = review.get_attribute("data-review-id")
                    #    try:
                    #        review_more = webdriver.find_element_by_xpath(
                    #            "//button[@data-review-id='{}' and @jsaction='pane.review.expandReview']".format(
                    #                review_id))
                    #        webdriver.execute_script("arguments[0].click()", review_more)
                    #    except NoSuchElementException:
                    #        pass
                    #    except StaleElementReferenceException:
                    #        print(review_more, ' Error review more click')
                    #        pass
                    review_more_btns = webdriver.find_elements_by_xpath("//button[@jsaction='pane.review.expandReview']")
                    for btn in review_more_btns:
                        webdriver.execute_script("arguments[0].click()", btn)
                    try:
                        reviews_parent = webdriver.find_element_by_xpath(
                            "//div[contains(@class, 'section-layout') and contains(@jsan, '7.section-layout')]")
                    except NoSuchElementException:
                        print("No reviews_parent")
                    else:
                        # print("Found parent")
                        try:
                            reviews = reviews_parent.find_elements_by_xpath(
                                "//div[contains(@class, 'section-review ripple-container')]")
                        except NoSuchElementException:
                            print("No reviews_parent")
                        else:
                            [comment_ques.put(review) for review in reviews]
                            print("Done. Manager ID: ", m_id, '. Comment_que size: ', gv.comment_que[m_id].qsize())
                            return True


# =============================================================================================================================#
# Google Worker Thread Functions
# =============================================================================================================================#
def get_review_info(webdriver, review_col, m_id, review_id):
    # webdriver.implicitly_wait(0)
    # print(review_id)
    # try:
    #     review_more = review_col.find_element_by_xpath(
    #         "//button[@data-review-id='{}' and @jsaction='pane.review.expandReview']".format(review_id))
    #     webdriver.execute_script("arguments[0].click()", review_more)
    # except NoSuchElementException:
    #     pass
    # except StaleElementReferenceException:
    #     print(review_more, ' Error review more click')
    #     pass

    usr_personal_rate_str = "0/0"
    if not gv.only_google_acc_validator[m_id]:
        usr_rating_acc_type_str = "//div[@data-review-id='{}']/div[@jsan='7.section-review-content']/div[@class = 'section-review-line']/div[contains(@jsan,'7.section-review-metadata,7.section-review-metadata-with-note')]".format(review_id)
        usr_personal_rate_str_tmp = webdriver.find_element_by_xpath(
            usr_rating_acc_type_str + "/span[@class='section-review-stars' or @class='section-review-numerical-rating']")
        usr_personal_rate_str = usr_personal_rate_str_tmp.get_attribute("textContent")
        usr_acc_type_str = webdriver.find_element_by_xpath(
            usr_rating_acc_type_str + "/span[@class='section-review-publish-date-and-source']/span[position()=2]")
        usr_acc_type_str = usr_acc_type_str.get_attribute('textContent')
    else:
        usr_acc_type_str = "Google"
        try:
            usr_personal_rate_str_tmp = webdriver.find_element_by_xpath(
                "//div[@data-review-id='{}']/div[@jsan='7.section-review-content']/div[@class = 'section-review-line']/div[contains(@jsan,'7.section-review-metadata,7.section-review-metadata-with-note')]/span[@class='section-review-stars' or @class='section-review-numerical-rating']".format(review_id))
            usr_personal_rate_str = usr_personal_rate_str_tmp.get_attribute("aria-label")
            if usr_personal_rate_str == "":
                usr_personal_rate_str = usr_personal_rate_str_tmp.get_attribute("textContent")

        except NoSuchElementException:
            print(gv.tmp_dict[m_id]['Name'])
    try:
        if usr_acc_type_str == "Agoda":
            usr_name_box = "//div[@data-review-id='{}']/div[@jsan='7.section-review-content']/div[@jsan='7.section-review-line,7.section-review-line-with-indent']/div[@style='position:relative']/div[contains(@jsan,'7.section-review-titles')]/a/div[contains(@jsan,'7.section-review-title')]/a".format(
                review_id)
        else:
            usr_name_box = "//div[@data-review-id='{}']/div[@jsan='7.section-review-content']/div[@jsan='7.section-review-line,7.section-review-line-with-indent']/div[@style='position:relative']/div[contains(@jsan,'7.section-review-titles')]/a/div[contains(@jsan,'7.section-review-title')]/span".format(
                review_id)

        usr_name = webdriver.find_element_by_xpath(usr_name_box)
        usr_name_str = usr_name.get_attribute("textContent")
    except NoSuchElementException:
        usr_name_str = "No User Name"

    try:
        str_user_acc_state = "//div[@data-review-id='{}']/div[@jsan='7.section-review-content']/div[@jsan='7.section-review-line,7.section-review-line-with-indent']/div[@style='position:relative']/div[contains(@jsan,'7.section-review-titles')]/a/div[@class='section-review-subtitle' and not(@style='display:none')]/span[1]".format(review_id)
        user_acc_state = webdriver.find_element_by_xpath(str_user_acc_state)
        user_acc_state_result = user_acc_state.get_attribute("textContent")
    except NoSuchElementException:
        user_acc_state_result = "Normal User"

    try:
        str_total_usr_review = "//div[@data-review-id='{}']/div[@jsan='7.section-review-content']/div[@class='section-review-line']/div[contains(@class,'section-review-metadata')]/span[@class='section-review-numerical-rating']".format(review_id)
        total_usr_review = webdriver.find_element_by_xpath(str_total_usr_review)
        total_usr_review_result = total_usr_review.get_attribute("textContent")
        if total_usr_review_result == "" or total_usr_review_result == " ":
            total_usr_review_result = 0
        else:
            total_usr_review_result = re.findall('\d+', total_usr_review_result)
            total_usr_review_result = int(total_usr_review_result[0])
    except NoSuchElementException:
        total_usr_review_result = 0
    try:
        review_box = "//div[@data-review-id='{}']/div[@jsan='0.data-review-id,22.jsaction']/div[" \
                     "@jsan='7.section-review-content']/div[@class='section-review-line']/div[" \
                     "@class='section-review-review-content']/span[@jsan='7.section-review-text']".format(review_id)
        review_message = webdriver.find_element_by_xpath(review_box)
        comment_str = review_message.get_attribute("textContent")
        if comment_str == "" or comment_str == " ":
            comment_str = "No review leave by the user"
    except NoSuchElementException:
        gv.user_review_list[m_id].append(
            {'Address': gv.tmp_dict[m_id]['Address'], 'User_Name': usr_name_str, 'Data_Review_ID': review_id,
             'User_Account_Type': usr_acc_type_str,
             'User Personal Rating': usr_personal_rate_str, 'Comment': 'No Comment',
             'User Account Rank': user_acc_state_result, 'Total number of contribution': total_usr_review_result})
    else:
        gv.user_review_list[m_id].append(
            {'Address': gv.tmp_dict[m_id]['Address'], 'User_Name': usr_name_str, 'Data_Review_ID': review_id,
             'User_Account_Type': usr_acc_type_str,
             'User Personal Rating': usr_personal_rate_str, 'Comment': comment_str,
             'User Account Rank': user_acc_state_result, 'Total number of contribution': total_usr_review_result})

# ===================================================================================== #
# ===================================================================================== #
# To crawl the url of the company on google map before looking into the company review  #
# ===================================================================================== #
# ===================================================================================== #
def crawl_url_google_map(str_div, url_driver, no_index):
    done_loop = 0
    counter_loop = 0

    while not done_loop:
        try:
            res_ele = url_driver.find_element_by_xpath(str_div)
            url_driver.execute_script("arguments[0].click();", res_ele)
            try:
                back_result_button = url_driver.find_element_by_xpath(
                    "//button[@class='section-back-to-list-button blue-link noprint']/span")
                try:
                    WebDriverWait(url_driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//h1[@jsan='7.section-hero-header-title-title,7.GLOBAL__gm2-headline-5']"))
                    )
                except NoSuchElementException:
                    raise NoSuchElementException
                else:
                    gv.urls_que.put(url_driver.current_url)
                    # urlService().createUrl(url_driver.current_url)
                url_driver.execute_script("arguments[0].click();", back_result_button)
                try:
                    # See if back it successfully back to search pages.
                    WebDriverWait(url_driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@jsan,'7.section-scrollbox,7.scrollable-y,7.scrollable-show')]"))
                    )
                except NoSuchElementException:
                    raise NoSuchElementException
                else:
                    done_loop = True
            except NoSuchElementException:
                if counter_loop > 5:
                    done_loop = True
                counter_loop += 1
                print("No back result button", url_driver.current_url)
        except NoSuchElementException:
            print("Cannot find {}".format(no_index))
            if counter_loop > 0:
                print("No url {}".format(no_index))
                done_loop = True
            counter_loop += 1
        except WebDriverException:
            print("Web driver error...")
            print("Exiting the program...")
            done_loop = True


def start_scrapper():
    # init driver
    # Choose the web driver for different OS
    # Then open the web driver for respective OS
    url_driver = getWebDriver()
    url_driver.get("https://www.google.com/maps/")
    counter = 1
    print(counter)

    try:
        try:
            WebDriverWait(url_driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchbox"))
            )
        except TimeoutException:
            raise TimeoutException
        else:
            # print("Done find search box")
            elem = url_driver.find_element_by_name("q")
            elem.send_keys(gv.text_to_search)
            #elem.send_keys("boutique hotel kampar")  # Uncomment this for testing
            elem.send_keys(Keys.RETURN)
            elem.send_keys(Keys.RETURN)

        try:
            WebDriverWait(url_driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@jsan,'7.section-scrollbox,7.scrollable-y,7.scrollable-show')]"))
            )
        except TimeoutException:
            raise TimeoutException
        else:
            # print("Done find section")
            url_driver.implicitly_wait(5)  # seconds

        start_time = time.time()
        while counter:
            elem2 = url_driver.find_element_by_xpath(
                "//div[contains(@jsan,'t-dgE5uNmzjiE,7.section-layout,7.section-scrollbox,7.scrollable-y,7.scrollable-show,7.section-layout-flex-vertical,7.section-layout-inset-shadow,0.aria-label,0.role')]")
            try:
                # While it reached to the end of the pages.
                url_driver.find_element_by_xpath(
                    "//button[@id='n7lv7yjyC35__section-pagination-button-next' and @disabled='true']/span["
                    "@class='n7lv7yjyC35__button-next-icon']")
                elem4 = int(((len(elem2.find_elements_by_xpath("./div")) - 1) / 2) + 1)
                # print(elem4)
                for i in range(elem4):
                    gv.no_index = i + 1
                    try:
                        str_div = "//div[@data-result-index='{}']".format(gv.no_index)
                        crawl_url_google_map(str_div, url_driver, gv.no_index)
                    except NoSuchElementException:
                        pass
                print('Finish all thread!')
            except NoSuchElementException:
                # print("Got Next Button")
                # While it is not the last pages.
                try:
                    WebDriverWait(url_driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//button[@id='n7lv7yjyC35__section-pagination-button-next"
                                                        "']/span[@class='n7lv7yjyC35__button-next-icon']"))
                    )
                finally:
                    # print("Done next Button")
                    elem4 = int(((len(elem2.find_elements_by_xpath("./div")) - 1) / 2) + 1)
                    print(elem4)
                    gv.totalJobs = gv.totalJobs + elem4
                for i in range(elem4):
                    gv.no_index = i + 1
                    str_div = "//div[@data-result-index='{}']".format(gv.no_index)
                    crawl_url_google_map(str_div, url_driver, gv.no_index)
                try:
                    WebDriverWait(url_driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "//button[@id='n7lv7yjyC35__section-pagination-button-next"
                                                        "']/span[@class='n7lv7yjyC35__button-next-icon']"))
                    )
                    try:
                        url_driver.find_element_by_xpath("//div[@class='section-no-result-title']")
                    except NoSuchElementException:
                        pass
                    else:
                        raise NoSuchElementException
                except NoSuchElementException:
                    print("No nextPage...")
                    print("Done exit.")
                    counter = 0
                else:
                    print('Next Page')
                    next_elem = url_driver.find_element_by_xpath(
                        "//button[@id='n7lv7yjyC35__section-pagination-button-next']/span["
                        "@class='n7lv7yjyC35__button-next-icon']")
                    url_driver.execute_script("arguments[0].click();", next_elem)
            else:
                print("Done exit.")
                counter = 0

        url_string = url_driver.current_url
        print("Done copying the url", url_string, "Time taken is:", str(time.time() - start_time), "seconds")
    except TimeoutException:
        url_driver.quit()
        print("Time out! Please try again")
        raise TimeoutException
    url_driver.quit()




# start_scrapper()
# while True:
#     try:
#         print(gv.urls_que.unfinished_tasks)
#         gv.urls_que.get_nowait()
#         print(gv.urls_que.unfinished_tasks)
#         gv.urls_que.task_done()
#         print(gv.urls_que.unfinished_tasks)
#     except Queue.Empty:
#         print('Empty')

# for i in tqdm(urls_que):
#     time.sleep(0.1)
