from .workerCrawlerHotelService import *
from .managerCrawlerService import initiate_manager as him, terminate_manager as htm
from .managerAttractionCrawlerService import initiate_manager as aim, terminate_manager as atm
from .managerRestaurantCrawlerService import initiate_manager as rim, terminate_manager as rtm


class taScrappingService(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        start_time = time.time()
        try:
            try:
                if gv.text_to_search.find("Things To Do") >= 0:
                    #start_scrapper_attraction()
                    gv.urls_que.put("https://www.tripadvisor.com.my/Attraction_Review-g298303-d1798470-Reviews-Pinang_Peranakan_Mansion-George_Town_Penang_Island_Penang.html")
                    aim()
                    atm()
                elif gv.text_to_search.find("Hotels") >= 0:
                    start_scrapper()
                    #gv.urls_que.put("https://www.tripadvisor.com.my/Hotel_Review-g3522152-d12099624-Reviews-Kampar_Boutique_Hotel-Kampar_Kampar_District_Perak.html")
                    # gv.urls_que.put("https://www.tripadvisor.com.my/Hotel_Review-g3522152-d15618596-Reviews-MD_Boutique_Hotel-Kampar_Kampar_District_Perak.html")
                    # gv.urls_que.put("https://www.tripadvisor.com.my/Hotel_Review-g3522152-d9728240-Reviews-Sahom_Valley_Agro_Eco_Resort-Kampar_Kampar_District_Perak.html")
                    # gv.urls_que.put("https://www.tripadvisor.com.my/Hotel_Review-g298298-d8409933-Reviews-My_Home_Hotel_Station_18_Ipoh-Ipoh_Kinta_District_Perak.html")
                    # gv.urls_que.put("https://www.tripadvisor.com.my/Hotel_Review-g4917554-d4835313-Reviews-D_Hotel_Seri_Iskandar-Bandar_Seri_Iskandar_Perak.html")
                    him()
                    htm()
                elif gv.text_to_search.find("Restaurants") >= 0:
                    start_scrapper_restaurant()
                    # gv.urls_que.put("https://www.tripadvisor.com.my/Restaurant_Review-g3522152-d7243567-Reviews-Chan_Siew_Heng_Claypot_Chicken_Rice-Kampar_Kampar_District_Perak.html")
                    rim()
                    rtm()
            except TimeoutException:
                if gv.text_to_search.find("Things To Do") >= 0:
                    start_scrapper_attraction()
                    aim()
                    atm()
                elif gv.text_to_search.find("Hotels") >= 0:
                    start_scrapper()
                    him()
                    htm()
                elif gv.text_to_search.find("Restaurants") >= 0:
                    start_scrapper_restaurant()
                    rim()
                    rtm()

            gv.startScrappingFlag = False
            #saveResult(gv.res_info_dic, gv.usr_info_dic, start_time)
            #psg.Popup('Test Done')
        except TimeoutException:
            gv.timeoutFlag = True
