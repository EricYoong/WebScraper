from WebScrappingPython.shared.basedFunction import *
import WebScrappingPython.shared.globalVariable as gv
from WebScrappingPython.shared.globalModule import *
from selenium.webdriver.common.action_chains import ActionChains


def crawl_data(threadName, threadID, urls_que, comment_ques, webdriver):
    t_id = threadID
    while not gv.exitFlag:
        webdriver.implicitly_wait(5)
        done, error = False, False
        time_out_counter = 0

        try:
            gv.timeout_flag[t_id] = False
            gv.user_review_list[t_id] = []
            gv.tmp_dict[t_id] = {'Name': 'None', 'Ranking': 'None', 'Cuisine': 'None', 'Address': 'None', 'Country': 'None', 'Postcode': '0', 'City': 'None'}
            try:
                url = urls_que.get(False)
                while not error and not done:
                    try:
                        webdriver.get(url)
                        try:
                            if gv.text_to_search.find("Restaurants") >= 0:
                                WebDriverWait(webdriver, 20).until(
                                    EC.presence_of_element_located((By.XPATH,
                                                                    "//h1[@data-test-target='top-info-header']"))
                                )
                            else:
                                WebDriverWait(webdriver, 20).until(
                                    EC.presence_of_element_located((By.XPATH,
                                                                    "//h1[@id='HEADING']"))
                                )
                        except NoSuchElementException:
                            print("I am", threadName, "no such element")
                        except TimeoutException:
                            print('Tttttttttttt')
                            raise TimeoutException
                        else:
                            time.sleep(5) #Wait the website to be fully loaded
                            crawl_name(webdriver, gv.tmp_dict[t_id])
                            crawl_address(webdriver, gv.tmp_dict[t_id])

                            if gv.text_to_search.find("Restaurants") >= 0:
                                crawlRestaurantType(webdriver, gv.tmp_dict[t_id])

                            try:
                                # Crawl Overall review rate
                                crawl_review_rate(webdriver, gv.tmp_dict[t_id])
                                review_exist = True
                            except NoSuchElementException:
                                review_exist = False

                            print(review_exist, "review_exist")

                            gv.tmp_dict[t_id]['URL'] = url

                            if review_exist:
                                get_review_ques(webdriver, comment_ques, t_id)
                            else:
                                gv.user_review_list[t_id].append({
                                    'Name': gv.tmp_dict[t_id]['Name'],
                                    'Ranking': gv.tmp_dict[t_id]['Ranking'],
                                    'Cuisine': gv.tmp_dict[t_id]['Cuisine'],
                                    'Address': gv.tmp_dict[t_id]['Address'],
                                    'Country': gv.tmp_dict[t_id]['Country'],
                                    'Postcode': gv.tmp_dict[t_id]['Postcode'],
                                    'City': gv.tmp_dict[t_id]['City'],
                                    'URL': gv.tmp_dict[t_id]['URL'],
                                    'Username': 'None',
                                    'User Location': 'None',
                                    'User Rating': '0',
                                    'User Contribution': '0',
                                    'User Helpful Vote': '0',
                                    'Comment': 'None',
                                    'User Response Date': 'None',
                                    'Date Of Stay / Experienced / Visit': 'None',
                                    'User Traveller Type': 'None'
                                })
                    except TimeoutException:
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
                        saveResult(gv.user_review_list[t_id], gv.start_time)
                        print("Done crawl ", gv.tmp_dict[t_id]['Name'], '\n', threadName)
                        done = True
                        urls_que.task_done()
                    if gv.interrupted:
                        print("Interrupted Gotta go")
                        break
                    print("This is total")
            except Queue.Empty:
                raise Queue.Empty
        except Queue.Empty:
            time.sleep(1)
        except Exception as ec:
            PrintException()
            print(threadName)
            gv.url_retry.append(url)
            urls_que.task_done()
            time.sleep(1)
            continue


# Sub function to assist the main function for the trip advisor master thread. #

def crawl_review_rate(webdriver, tmp_dicts):
    finished = 0
    counter = 0
    while not finished:
        try:
            if gv.text_to_search.find("Things To Do") >= 0:
                review_col = webdriver.find_element_by_xpath("//span[contains(@class, 'ui_bubble_rating')]")
                tmp_dicts['Ranking'] = ".".join(list(review_col.get_attribute("class").split(" ")[1].split("_")[1]))
            elif gv.text_to_search.find("Hotels") >= 0:
                review_col = webdriver.find_element_by_xpath(
                    "//div[@id='ABOUT_TAB']/div[contains(@class, 'ui_columns')]/div[1]/div[1]/span")
                tmp_dicts['Ranking'] = review_col.get_attribute("textContent")
            elif gv.text_to_search.find("Restaurants") >= 0:
                review_col = webdriver.find_element_by_xpath(
                    "//a[@href='#REVIEWS']/span[1]")
                tmp_dicts['Ranking'] = review_col.get_attribute("aria-label").split(" ")[0]
            # print(tmp_dicts['Ranking'])
            finished = 1
        except NoSuchElementException:
            if counter < 1:
                print("No review!")
            elif counter >= 1:
                print("No review xpath found", webdriver.current_url)
                tmp_dicts['Ranking'] = "0.0"
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
            if gv.text_to_search.find("Restaurants") >= 0:
                res_name_col = webdriver.find_element_by_xpath("//h1[@data-test-target='top-info-header']")
            else:
                res_name_col = webdriver.find_element_by_xpath("//h1[@id='HEADING']")

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
        except StaleElementReferenceException:
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
        if gv.text_to_search.find("Things To Do") >= 0:
            addr_col = webdriver.find_element_by_xpath(
                "//div[@id='NEARBY_TAB']/div[2]/div/div[contains(text(), 'Location')]/parent::div/div[2]/div[2]/div[1]/span[2]")
        elif gv.text_to_search.find("Hotels") >= 0:
            addr_col = webdriver.find_element_by_xpath(
                "//div[@id='LOCATION']/div[contains(@class, 'ui_columns')]/div[1]/div[2]/span[2]/span")
        elif gv.text_to_search.find("Restaurants") >= 0:
            addr_col = webdriver.find_element_by_xpath(
                "//a[@href='#MAPVIEW']")

        addr_str = addr_col.get_attribute("textContent")

        if (len(addr_str) > 0):
            addrText = addr_str.split(", ")
            addrText = ', '.join(addrText[:-1])
            print(addr_str.split(", ")[-1])

            tmp_dicts['Address'] = addrText
            tmpSplit = addr_str.split(", ")[-1].split(" ")
            poscodeFound = False
            for i in range(len(tmpSplit)):
                if tmpSplit[i].isdigit():
                    poscodeFound = i
                    break

            if poscodeFound:
                tmp_dicts['Postcode'] = addr_str.split(", ")[-1].split(" ")[poscodeFound]
                tmp_dicts['City'] = ' '.join(addr_str.split(", ")[-1].split(" ")[0: poscodeFound])
            else:
                tmp_dicts['Postcode'] = "None"
                tmp_dicts['City'] = addr_str.split(", ")[-1].split(" ")[0]

            tmp_dicts['Country'] = addr_str.split(", ")[-1].split(" ")[-1]
        else:
            tmp_dicts['Address'] = "None"
    except NoSuchElementException:
        tmp_dicts['Address'] = "None"
        tmp_dicts['Postcode'] = "None"
        tmp_dicts['City'] = "None"
        print('No Address for', tmp_dicts)

def crawlRestaurantType(webdriver, tmp_dicts):
    try:
        resType = webdriver.find_element_by_xpath("//div[contains(text(), 'CUISINES')]/parent::div/div[2]")
        tmp_dicts['Cuisine'] = resType.get_attribute("textContent")
    except NoSuchElementException:
        tmp_dicts['Cuisine'] = "None"

def clickNextReviewSection(webdriver):
    try:
        nextBtn = webdriver.find_element_by_class_name(
            "next"
        )

        if nextBtn.get_attribute("class").find("disabled") >= 0:
            return False

        webdriver.execute_script("arguments[0].click()", nextBtn)
        time.sleep(1)
        return True
    except NoSuchElementException:
        return False
    except selenium.common.exceptions.ElementClickInterceptedException:
        return False
        # print("At the most bottom")


def get_review_ques(webdriver, comment_ques, m_id):
    while not gv.exitFlag:
        try:
            if gv.text_to_search.find("Things To Do") >= 0:
                reviewsDiv = WebDriverWait(webdriver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         "//div[contains(@data-test-target, 'reviews-tab')]/div/div[contains(@class, 'Dq9MAugU T870kzTX LnVzGwUB')]"))
                )
            elif gv.text_to_search.find("Hotels") >= 0:
                WebDriverWait(webdriver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         "//div[contains(@data-test-target, 'reviews-tab')]/div[contains(@data-test-target, 'HR_CC_CARD')]"))
                )
            elif gv.text_to_search.find("Restaurants") >= 0:
                WebDriverWait(webdriver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         "//div[contains(@data-contextchoice, 'DETAIL')]/div[not(contains(@class, 'cms-wrapper'))]"))
                )
        except TimeoutException:
            raise TimeoutException
        else:
            try:
                ###########################################################################################################
                # Expand comment
                ###########################################################################################################

                if gv.text_to_search.find("Things To Do") >= 0:
                    review = reviewsDiv.find_element_by_xpath(
                        ".//div[@data-test-target='expand-review']/span[contains(@class, '_3maEfNCR')]")
                    webdriver.execute_script("arguments[0].click();", review)

                    reviews = webdriver.find_elements_by_xpath(
                        "//div[contains(@data-test-target, 'reviews-tab')]/div/div[contains(@class, 'Dq9MAugU T870kzTX LnVzGwUB')]")
                    time.sleep(1)
                elif gv.text_to_search.find("Hotels") >= 0:
                    time.sleep(2)

                    review = webdriver.find_elements_by_xpath(
                        ".//div[@data-test-target='expand-review']/span")
                    webdriver.execute_script("arguments[0].click();", review[1])

                    reviews = webdriver.find_elements_by_xpath(
                        "//div[contains(@data-test-target, 'reviews-tab')]/div[contains(@data-test-target, 'HR_CC_CARD')]")

                elif gv.text_to_search.find("Restaurants") >= 0:
                    time.sleep(2)

                    review = webdriver.find_elements_by_xpath(
                        "//div[contains(@data-contextchoice, 'DETAIL')]/div[not(contains(@class, 'cms-wrapper'))]"
                    )

                    for xx in review:
                        try:
                            review = xx.find_element_by_xpath(
                                ".//span[contains(@class, 'ulBlueLinks')]"
                            )
                            webdriver.execute_script("arguments[0].click();", review)
                            break
                        except NoSuchElementException:
                            print("No view more review btn")

                    reviews = webdriver.find_elements_by_xpath(
                        "//div[contains(@data-contextchoice, 'DETAIL')]/div[not(contains(@class, 'cms-wrapper')) and not(contains(text(), 'View more reviews'))]")[0:-1]

            except NoSuchElementException:
                print("No reviews_parent")
                return False
            except StaleElementReferenceException:
                return False
            else:
                for i in range(len(reviews)):
                    comment_ques.put(i)
                comment_ques.join()
                if not clickNextReviewSection(webdriver):
                    return False
                print("Done. Manager ID: ", m_id, '. Name: ', gv.tmp_dict[m_id]["Name"])

# =============================================================================================================================#
# trip advisor Worker Thread Functions
# =============================================================================================================================#
def get_review_info(webdriver, col_id, m_id):
    userInfo = {
        'Name': gv.tmp_dict[m_id]['Name'],
        'Ranking': gv.tmp_dict[m_id]['Ranking'],
        'Address': gv.tmp_dict[m_id]['Address'],
        'Country': gv.tmp_dict[m_id]['Country'],
        'Postcode': gv.tmp_dict[m_id]['Postcode'],
        'City': gv.tmp_dict[m_id]['City'],
        'URL': gv.tmp_dict[m_id]['URL'],
        'Username': 'None',
        'User Location': 'None',
        'User Rating': '0',
        'User Contribution': '0',
        'User Helpful Vote': '0',
        'Comment': 'None',
        'User Response Date': 'None',
        'Date Of Stay / Experienced / Visit': 'None',
        'User Traveller Type': 'None'
    }

    if gv.text_to_search.find("Things To Do") >= 0:
        reviewStr = "//div[contains(@data-test-target, 'reviews-tab')]/div/div[contains(@class, 'Dq9MAugU T870kzTX LnVzGwUB')]"
        reviewTabStr = "//div[@data-test-target = 'reviews-tab']/div/div/div[contains(@class, 'ui_column')]/div"
        dateOfStr = "Date of experience: "
    elif gv.text_to_search.find("Hotels") >= 0:
        reviewStr = "//div[contains(@data-test-target, 'reviews-tab')]/div[contains(@data-test-target, 'HR_CC_CARD')]"
        reviewTabStr = "//div[@data-test-target = 'reviews-tab']/div/div[contains(@class, 'ui_column')]/div"
        dateOfStr = "Date of stay: "

    # userInfo['Address'] = gv.tmp_dict[m_id]['Address']
    ###########################################################################################################
    # Preprocess TravellerType
    try:
        reviewTabs = webdriver.find_elements_by_xpath(reviewTabStr)
    except NoSuchElementException:
        travel = "None None"
    else:
        try:
            travellerType = False
            for xx in reviewTabs:
                if xx.find_element_by_xpath(".//div").get_attribute("textContent").find("Traveller type") >= 0:
                    travellerType = xx.find_elements_by_xpath(".//ul/li")
                    break

            if not travellerType:
                print("0 traverller type")
        except StaleElementReferenceException:
            print("0 traverller type")
        except NoSuchElementException:
            travel = "0 traverller type"

        types = []
        [types.append(type.text) for type in travellerType]

    ###########################################################################################################
    ###########################################################################################################
    # User Name
    name = "Unknown name"
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        name = review_col.find_element_by_class_name('ui_header_link')
    except NoSuchElementException:
        name = "Unknown name"
    else:
        try:
            name = name.get_attribute("textContent")
        except StaleElementReferenceException:
            name = "Unknown name"
        # name_csv.append(name.text)

    # print(name)
    userInfo['Username'] = name
    ###########################################################################################################
    ###########################################################################################################
    # User Location
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        userLoc = review_col.find_element_by_xpath(
            ".//span[contains(@class, 'small')]")
    except NoSuchElementException:
        userLoc = "No Country"
    else:
        try:
            userLoc = userLoc.get_attribute("textContent")
            if len(userLoc) == 0:
                userLoc = "No Country"
        except StaleElementReferenceException:
            userLoc = "No Country"
    # userLoc_csv.append(userLoc.text)
    userInfo['User Location'] = userLoc

    ###########################################################################################################
    ###########################################################################################################
    # Contributions
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        checkContri = review_col.find_elements_by_xpath(
            ".//span[not(contains(@class, 'small')) and contains(@class, '_3fPsSAYi')]")
    except NoSuchElementException:
        contri = "0"
    else:
        contri = False
        for xx in checkContri:
            if xx.get_attribute("textContent").find("contribution") >= 0:
                contri = xx.find_element_by_xpath(".//span").get_attribute("textContent")
                contri = contri.split(" c")[0]
                break
        if not contri:
            contri = "0"

    userInfo['User Contribution'] = contri
    ###########################################################################################################
    ###########################################################################################################
    # User Rating
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        userRating = review_col.find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating')]")
    except NoSuchElementException:
        userRating = "0"
    else:
        userRating = ".".join(list(userRating.get_attribute("class").split(" ")[1].split("_")[1]))

    userInfo['User Rating'] = userRating
    ###########################################################################################################
    ###########################################################################################################
    # Helpful Votes
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        checkVote = review_col.find_elements_by_xpath(
            ".//span[not(contains(@class, 'small')) and contains(@class, '_3fPsSAYi')]")
    except NoSuchElementException:
        vote = "0"
    else:
        vote = False
        for xx in checkVote:
            if xx.get_attribute("textContent").find("helpful vote") >= 0:
                vote = xx.find_element_by_xpath(".//span").get_attribute("textContent")
                vote = vote.split(" help")[0]
                break
        if not vote:
            vote = "0"

    userInfo['User Helpful Vote'] = vote

    ###########################################################################################################
    ###########################################################################################################
    # Reply and ResponseDate
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        reply = review_col.find_element_by_xpath(".//q")
    except NoSuchElementException:
        reply = "None"
        # reply_csv.append("None")
        # responseDate_csv.append("None")
    else:
        try:
            reply = reply.get_attribute("textContent")
        except StaleElementReferenceException:
            reply = "None"
            # reply = driver.find_element_by_css_selector("div.listContainer.hide-more-mobile > div:nth-child(" + x + ") div.mgrRspnInline > div.prw_rup.prw_reviews_text_summary_hsx")
        # reply_csv.append(reply.text)

        try:
            review_col = webdriver.find_elements_by_xpath(reviewStr)[
                col_id]
            responseDate = review_col.find_elements_by_xpath(
                ".//span[not(contains(@class, 'small'))]")
        except NoSuchElementException:
            date = "None"
        else:
            date = False
            for xx in responseDate:
                if xx.get_attribute("textContent").find(" wrote a review ") >= 0:
                    date = xx.get_attribute("textContent")
                    date = date.split(" wrote a review ")[1]
                    break
            if not date:
                date = "None"

    userInfo['Comment'] = reply
    userInfo['User Response Date'] = date

    ###########################################################################################################

    ###########################################################################################################
    # Stay
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        dateStays = review_col.find_elements_by_xpath(
            ".//span[not(contains(@class, 'small')) and contains(@class, '_34Xs-BQm')]")
    except NoSuchElementException:
        date = "None"
    else:
        try:
            date = False
            for xx in dateStays:
                if xx.get_attribute("textContent").find(dateOfStr) >= 0:
                    date = xx.get_attribute("textContent").split(dateOfStr)[1]
                    break

            if not date:
                date = "None"
        except StaleElementReferenceException:
            date = "None"

    userInfo['Date Of Stay / Experienced / Visit'] = date
    # dateOfStay_csv.append(stay.text)
    ###########################################################################################################
    ###########################################################################################################
    # Trip type: Travelled on business
    ###########################################################################################################
    try:
        review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
        divs = review_col.find_element_by_class_name('trip_type_label')
    except NoSuchElementException:
        tripType = "None"
    else:
        try:
            tripType = divs.find_element_by_xpath(".//parent::span").get_attribute("textContent")
            for tt in types:
                if tt.find("Families") >= 0:
                    if tripType.find("family") >= 0:
                        tripType = tt
                        break

                if tt.find("Couples") >= 0:
                    if tripType.find("couple") >= 0:
                        tripType = tt
                        break

                if tripType.find(tt.lower()) >= 0:
                    tripType = tt
                    break

            if not tripType:
                tripType = "None"
        except StaleElementReferenceException:
            tripType = "None"

    userInfo['User Traveller Type'] = tripType
    ###########################################################################################################
    gv.user_review_list[m_id].append(userInfo)
    return

def get_review_info_restaurant(webdriver, col_id, m_id):
    userInfo = {
        'Name': gv.tmp_dict[m_id]['Name'],
        'Ranking': gv.tmp_dict[m_id]['Ranking'],
        'Cuisine': gv.tmp_dict[m_id]['Cuisine'],
        'Address': gv.tmp_dict[m_id]['Address'],
        'Country': gv.tmp_dict[m_id]['Country'],
        'Postcode': gv.tmp_dict[m_id]['Postcode'],
        'City': gv.tmp_dict[m_id]['City'],
        'URL': gv.tmp_dict[m_id]['URL'],
        'Username': 'None',
        'User Location': 'None',
        'User Rating': '0',
        'User Contribution': '0',
        'User Helpful Vote': '0',
        'Comment': 'None',
        'User Response Date': 'None',
        'Date Of Stay / Experienced / Visit': 'None',
        'User Traveller Type': 'None'
    }

    reviewStr = "//div[contains(@data-contextchoice, 'DETAIL')]/div[not(contains(@class, 'cms-wrapper'))]"
    dateOfStr = "Date of visit: "
    try:
        ###########################################################################################################
        ###########################################################################################################
        # User Name
        name = "Unknown name"
        try:
            review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
            name = review_col.find_element_by_class_name('info_text').find_element_by_xpath(".//div[1]")
        except NoSuchElementException:
            name = "Unknown name"
        else:
            try:
                name = name.get_attribute("textContent")
            except StaleElementReferenceException:
                name = "Unknown name"
            # name_csv.append(name.text)

        # print(name)
        userInfo['Username'] = name
        ###########################################################################################################
        ###########################################################################################################
        # User Rating
        userRating = "0"
        try:
            review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
            userRating = review_col.find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating')]")
        except NoSuchElementException:
            userRating = "0"
        else:
            try:
                userRating = ".".join(list(userRating.get_attribute("class").split(" ")[1].split("_")[1]))
            except StaleElementReferenceException:
                time.sleep(1)
                userRating = ".".join(list(userRating.get_attribute("class").split(" ")[1].split("_")[1]))

        userInfo['User Rating'] = userRating
        ###########################################################################################################
        ###########################################################################################################
        # Reply and ResponseDate
        try:
            review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
            reply = review_col.find_element_by_xpath(".//p")
        except NoSuchElementException:
            reply = "None"
            # reply_csv.append("None")
            # responseDate_csv.append("None")
        else:
            try:
                reply = reply.get_attribute("textContent")
            except StaleElementReferenceException:
                reply = "None"
                # reply = driver.find_element_by_css_selector("div.listContainer.hide-more-mobile > div:nth-child(" + x + ") div.mgrRspnInline > div.prw_rup.prw_reviews_text_summary_hsx")
            # reply_csv.append(reply.text)

            try:
                review_col = webdriver.find_elements_by_xpath(reviewStr)[
                    col_id]
                responseDate = review_col.find_element_by_class_name("ratingDate")
            except NoSuchElementException:
                date = "None"
            else:
                date = responseDate.get_attribute("textContent").split("Reviewed ")[1]

        userInfo['Comment'] = reply
        userInfo['User Response Date'] = date

        ###########################################################################################################
        ###########################################################################################################
        # Stay
        try:
            review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
            dateStays = review_col.find_element_by_class_name("stay_date_label").find_element_by_xpath(".//parent::div")
        except NoSuchElementException:
            date = "None"
        else:
            try:
                date = dateStays.get_attribute("textContent").split(dateOfStr)[1]
            except StaleElementReferenceException:
                date = "None"

        userInfo['Date Of Stay / Experienced / Visit'] = date
        # dateOfStay_csv.append(stay.text)
        ###########################################################################################################
        ###########################################################################################################
        # Open User Profile

        gv.restaurant_worker_lock[m_id].acquire()

        try:
            review_col = webdriver.find_elements_by_xpath(reviewStr)[col_id]
            name = review_col.find_element_by_class_name('info_text').find_element_by_xpath(".//div[1]")
        except NoSuchElementException:
            name = "Unknown name"
        else:
            webdriver.execute_script("arguments[0].click();", name)
            time.sleep(1)

        ###########################################################################################################
        # User Location
        try:
            userLoc = webdriver.find_element_by_xpath(
                "//ul[@class='memberdescriptionReviewEnhancements']/li[2]")
        except NoSuchElementException:
            userLoc = "No Country"
        else:
            try:
                userLoc = userLoc.get_attribute("textContent").split("rom ")[1]
                if len(userLoc) == 0:
                    userLoc = "No Country"
            except StaleElementReferenceException:
                userLoc = "No Country"
        # userLoc_csv.append(userLoc.text)
        userInfo['User Location'] = userLoc

        ###########################################################################################################
        ###########################################################################################################
        # Contributions
        try:
            checkContri = webdriver.find_elements_by_xpath(
                "//ul[@class='countsReviewEnhancements']/li[@class='countsReviewEnhancementsItem']/span[2]")
        except NoSuchElementException:
            contri = "0"
        else:
            contri = False
            for xx in checkContri:
                if xx.get_attribute("textContent").find("Contributions") >= 0:
                    contri = xx.get_attribute("textContent").split(" C")[0]
                    break
            if not contri:
                contri = "0"

        userInfo['User Contribution'] = contri
        ###########################################################################################################
        ###########################################################################################################
        # Helpful Votes
        try:
            checkVote = webdriver.find_elements_by_xpath(
                "//ul[@class='countsReviewEnhancements']/li[@class='countsReviewEnhancementsItem']/span[2]")
        except NoSuchElementException:
            vote = "0"
        else:
            vote = False
            for xx in checkVote:
                if xx.get_attribute("textContent").find("Helpful votes") >= 0:
                    vote = xx.get_attribute("textContent").split(" Helpful")[0]
                    break
            if not vote:
                vote = "0"

        userInfo['User Helpful Vote'] = vote
        ###########################################################################################################
        ###########################################################################################################
        # Close player Profile
        try:
            closeBtn = webdriver.find_element_by_xpath("//span/div[@class='ui_close_x']")
        except NoSuchElementException:
            closeBtn = "Unknown btn"
        else:
            webdriver.execute_script("arguments[0].click();", closeBtn)
            time.sleep(1)

        ###########################################################################################################
    except Exception as ec:
        PrintException()
    finally:
        gv.restaurant_worker_lock[m_id].release()
        gv.user_review_list[m_id].append(userInfo)

    return


# ===================================================================================== #
# ===================================================================================== #
# To crawl the url of the company on trip advisor map before looking into the company review  #
# ===================================================================================== #
# ===================================================================================== #

def start_scrapper():
    # init driver
    # Choose the web driver for different OS
    # Then open the web driver for respective OS
    url_driver = getWebDriver()
    url_driver.get("https://www.tripadvisor.com.my/")
    counter = True

    try:
        try:
            elem = WebDriverWait(url_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Where to?')]"))
            )
        except TimeoutException:
            raise TimeoutException
        else:
            # print("Done find search box")
            elem.click()
            elem.send_keys(gv.text_to_search)
            # elem.send_keys("boutique hotel kampar")  # Uncomment this for testing
            elem.send_keys(Keys.RETURN)
            try:
                WebDriverWait(url_driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "//div[contains(@class,'prw_rup prw_meta_hsx_responsive_listing ui_section listItem')]"))
                )
            except TimeoutException:
                raise TimeoutException
            else:
                start_time = time.time()
                tmpList = []
                while counter:
                    # While it reached to the end of the pages.
                    # print(elem4)
                    time.sleep(5)
                    try:
                        for i in url_driver.find_elements_by_xpath(
                                "//div[contains(@class,'prw_rup prw_meta_hsx_responsive_listing ui_section listItem')]"
                        ):
                            a = i.find_element_by_xpath(".//a[contains(@class,'property_title')]")
                            if a.get_attribute('href') not in tmpList:
                                print(a.get_attribute('href'))
                                tmpList.append(a.get_attribute('href'))
                                gv.urls_que.put(a.get_attribute('href'))

                        div = url_driver.find_element_by_xpath(
                            "//div[contains(@class,'unified ui_pagination standard_pagination ui_section listFooter')]")
                        # Press next btn
                        try:
                            nextBtn = div.find_element_by_xpath(
                                ".//a[contains(@class,'next') and not(contains(@class,'disable'))]"
                            )
                        except NoSuchElementException:
                            nextBtn = div.find_element_by_xpath(
                                ".//span[contains(@class,'next') and not(contains(@class,'disable'))]"
                            )

                        nextBtn.click()

                    except NoSuchElementException:
                        counter = False
                    except StaleElementReferenceException:
                        continue
                    else:
                        try:
                            WebDriverWait(url_driver, 10).until(
                                EC.presence_of_element_located((By.XPATH,
                                                                "//div[contains(@class,'prw_rup prw_meta_hsx_responsive_listing ui_section listItem')]"))
                            )
                        except TimeoutException:
                            raise TimeoutException

                print('Finish all thread!')
    except TimeoutException:
        url_driver.quit()
        print("Time out! Please try again")
        raise TimeoutException
    except selenium.common.exceptions.ElementNotInteractableException:
        url_driver.quit()
        print("selenium.common.exceptions.ElementNotInteractableException! Please try again")

    url_driver.quit()


###########################################################################################################
###########################################################################################################
# Scrapper Function for Attraction Place
###########################################################################################################
###########################################################################################################

def start_scrapper_attraction():
    # init driver
    # Choose the web driver for different OS
    # Then open the web driver for respective OS
    try:
        url_driver = getWebDriver()
        url_driver.get("https://www.tripadvisor.com.my/")
        counter = True

        try:
            elem = WebDriverWait(url_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Where to?')]"))
            )
        except TimeoutException:
            raise TimeoutException
        else:
            # print("Done find search box")
            elem.click()
            elem.send_keys(gv.text_to_search)
            # elem.send_keys("boutique hotel kampar")  # Uncomment this for testing
            elem.send_keys(Keys.RETURN)
            try:
                WebDriverWait(url_driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@data-automation,'shelf_4')]/div[3]"))
                )
            except TimeoutException:
                raise TimeoutException
            else:
                start_time = time.time()
                tmpList = []
                UI_Version = 1
                while counter:
                    # While it reached to the end of the pages.
                    # print(elem4)
                    try:
                        if UI_Version == 1:
                            time.sleep(5)

                            mainDiv = url_driver.find_element_by_xpath(
                                    "//div[contains(@data-automation,'shelf_4')]/div[2]/div[contains(@class,'_2j03JUe9')]/parent::div"
                            )

                            for i in mainDiv.find_elements_by_xpath(
                                    ".//div[contains(@class,'_2j03JUe9')]"
                            ):
                                a = i.find_element_by_xpath(".//div/a")
                                print(a.get_attribute('href'))
                                if a.get_attribute('href') not in tmpList:
                                    tmpList.append(a.get_attribute('href'))
                                    gv.urls_que.put(a.get_attribute('href'))

                            nextBtn = url_driver.find_element_by_xpath(
                                "//button/a[text()='Next']"
                            )
                            UI_Version = 2
                        else:
                            for i in url_driver.find_elements_by_xpath(
                                    "//div[contains(@class, '_25PvF8uO _2X44Y8hm')]"
                            ):
                                a = i.find_element_by_xpath(".//div/a")
                                print(a.get_attribute('href'))
                                if a.get_attribute('href') not in tmpList:
                                    tmpList.append(a.get_attribute('href'))
                                    gv.urls_que.put(a.get_attribute('href'))

                            try:
                                nextBtn = url_driver.find_element_by_xpath(
                                    "//div[contains(@class,'ui_pagination')]/a[contains(@class,'next') and not(contains(@class,'disable'))]"
                                )
                            except NoSuchElementException:
                                nextBtn = url_driver.find_element_by_xpath(
                                    "//div[contains(@class,'ui_pagination')]/span[contains(@class,'next') and not(contains(@class,'disable'))]"
                                )

                        # Press next btn
                        url_driver.execute_script("arguments[0].click();", nextBtn)

                        time.sleep(5)
                    except NoSuchElementException:
                        counter = False
                    except StaleElementReferenceException:
                        continue

                print('Finish all thread!')
    except Exception as ec:
        PrintException()
    except TimeoutException:
        url_driver.quit()
        print("Time out! Please try again")
        raise TimeoutException
    except selenium.common.exceptions.ElementNotInteractableException:
        url_driver.quit()
        print("selenium.common.exceptions.ElementNotInteractableException! Please try again")

    url_driver.quit()

# ===================================================================================== #
# ===================================================================================== #
# Scrapper Function for Restaurant  #
# ===================================================================================== #
# ===================================================================================== #

def start_scrapper_restaurant():
    # init driver
    # Choose the web driver for different OS
    # Then open the web driver for respective OS
    url_driver = getWebDriver()
    url_driver.get("https://www.tripadvisor.com.my/")
    counter = True

    try:
        try:
            elem = WebDriverWait(url_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Where to?')]"))
            )
        except TimeoutException:
            raise TimeoutException
        else:
            # print("Done find search box")
            elem.click()
            elem.send_keys(gv.text_to_search)
            # elem.send_keys("boutique hotel kampar")  # Uncomment this for testing
            elem.send_keys(Keys.RETURN)
            try:
                WebDriverWait(url_driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//div[@data-test-target='restaurants-list']"))
                )
            except TimeoutException:
                raise TimeoutException
            else:
                start_time = time.time()
                tmpList = []
                while counter:
                    # While it reached to the end of the pages.
                    # print(elem4)
                    time.sleep(5)
                    try:
                        for i in url_driver.find_elements_by_xpath(
                                "//div[@data-test-target='restaurants-list']/div[not(contains(@class, '_5rLJEtpz'))]"
                        ):
                            a = i.find_element_by_xpath(".//a[contains(@class,'_15_ydu6b')]")
                            if a.get_attribute('href') not in tmpList:
                                print(a.get_attribute('href'))
                                tmpList.append(a.get_attribute('href'))
                                gv.urls_que.put(a.get_attribute('href'))

                        div = url_driver.find_element_by_xpath(
                            "//div[contains(@class,'pagination')]")
                        # Press next btn
                        try:
                            nextBtn = div.find_element_by_xpath(
                                ".//a[contains(@class,'next') and not(contains(@class,'disable'))]"
                            )
                        except NoSuchElementException:
                            nextBtn = div.find_element_by_xpath(
                                ".//span[contains(@class,'next') and not(contains(@class,'disable'))]"
                            )

                        nextBtn.click()

                    except NoSuchElementException:
                        counter = False
                    except StaleElementReferenceException:
                        continue
                    else:
                        try:
                            WebDriverWait(url_driver, 10).until(
                                EC.presence_of_element_located((By.XPATH,
                                                                "//div[@data-test-target='restaurants-list']"))
                            )
                        except TimeoutException:
                            raise TimeoutException

                print('Finish all thread!')
    except TimeoutException:
        url_driver.quit()
        print("Time out! Please try again")
        raise TimeoutException
    except selenium.common.exceptions.ElementNotInteractableException:
        url_driver.quit()
        print("selenium.common.exceptions.ElementNotInteractableException! Please try again")

    url_driver.quit()