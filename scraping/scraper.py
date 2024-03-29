from bs4 import BeautifulSoup
import misc
import time
import datetime
import urllib.request as urllib2
import logging
import pandas as pd

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_sales_from_community(city, communitylist):
    """
    get sales data from community
    """
    logging.info("Get Sell Infomation")
    starttime = datetime.datetime.now()
    for community in communitylist:
        try:
            get_sales_by_community(city, community)
        except Exception as e:
            logging.error(e)
            logging.error(community + "Fail")
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))


def get_community_from_region(city, regionlist=[u'xicheng']):
    """
        get community data from region
    """
    logging.info("Get Community Infomation")
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        try:
            get_community_by_region(city, regionname)
            logging.info(regionname + "Done")
        except Exception as e:
            logging.error(e)
            logging.error(regionname + "Fail")
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))


def get_house_from_region(city, regionlist=[u'xicheng']):
    """
        get house data from region
    """
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        logging.info("Get Onsale House Infomation in %s" % regionname)
        try:
            get_house_by_region(city, regionname)
        except Exception as e:
            logging.error(e)
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))


def get_rent_from_region(city, regionlist=[u'xicheng']):
    """
    get rent from region
    """
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        logging.info("Get Rent House Infomation in %s" % regionname)
        try:
            get_rent_by_region(city, regionname)
        except Exception as e:
            logging.error(e)
            pass
    endtime = datetime.datetime.now()
    logging.info("Run time: " + str(endtime - starttime))


def get_sales_by_community(city, communityname):
    """
    get the sales data
    """
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"chengjiao/rs" + \
        urllib2.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    data_source = []
    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + \
                u"chengjiao/pg%drs%s/" % (page,
                                          urllib2.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        log_progress("GetSellByCommunitylist",
                     communityname, page + 1, total_pages)
        for ultag in soup.findAll("ul", {"class": "listContent"}):
            for name in ultag.find_all('li'):
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "title"})
                    info_dict.update({u'title': housetitle.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get('href')})
                    houseID = housetitle.a.get(
                        'href').split("/")[-1].split(".")[0]
                    info_dict.update({u'houseID': houseID.strip()})

                    house = housetitle.get_text().strip().split(' ')
                    info_dict.update({u'community': communityname})
                    info_dict.update(
                        {u'housetype': house[1].strip() if 1 < len(house) else ''})
                    info_dict.update(
                        {u'square': house[2].strip() if 2 < len(house) else ''})

                    houseinfo = name.find("div", {"class": "houseInfo"})
                    info = houseinfo.get_text().split('|')
                    info_dict.update({u'direction': info[0].strip()})
                    info_dict.update(
                        {u'status': info[1].strip() if 1 < len(info) else ''})

                    housefloor = name.find("div", {"class": "positionInfo"})
                    floor_all = housefloor.get_text().strip().split(' ')
                    info_dict.update({u'floor': floor_all[0].strip()})
                    info_dict.update({u'years': floor_all[-1].strip()})

                    followInfo = name.find("div", {"class": "source"})
                    info_dict.update(
                        {u'source': followInfo.get_text().strip()})

                    totalPrice = name.find("div", {"class": "totalPrice"})
                    if totalPrice.span is None:
                        info_dict.update(
                            {u'totalPrice': totalPrice.get_text().strip()})
                    else:
                        info_dict.update(
                            {u'totalPrice': totalPrice.span.get_text().strip()})

                    unitPrice = name.find("div", {"class": "unitPrice"})
                    if unitPrice.span is None:
                        info_dict.update(
                            {u'unitPrice': unitPrice.get_text().strip()})
                    else:
                        info_dict.update(
                            {u'unitPrice': unitPrice.span.get_text().strip()})

                    dealDate = name.find("div", {"class": "dealDate"})
                    info_dict.update(
                        {u'dealdate': dealDate.get_text().strip().replace('.', '-')})

                except:
                    continue
                # Sellinfo insert into mysql
                data_source.append(info_dict)

    df = pd.DataFrame(data_source)
    df.to_csv('sales_by_community.csv')


def get_community_by_region(city, regionname=u'xicheng'):
    """
    get the community data
    """
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"xiaoqu/" + regionname + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    data_source = []
    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + u"xiaoqu/" + regionname + "/pg%d/" % page
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class": "clear"})
        i = 0
        log_progress("GetCommunityByRegionlist",
                     regionname, page + 1, total_pages)
        for name in nameList:  # Per house loop
            i = i + 1
            info_dict = {}
            try:
                communitytitle = name.find("div", {"class": "title"})
                title = communitytitle.get_text().strip('\n')
                link = communitytitle.a.get('href')
                info_dict.update({u'title': title})
                info_dict.update({u'link': link})

                district = name.find("a", {"class": "district"})
                info_dict.update({u'district': district.get_text()})

                bizcircle = name.find("a", {"class": "bizcircle"})
                info_dict.update({u'bizcircle': bizcircle.get_text()})

                tagList = name.find("div", {"class": "tagList"})
                info_dict.update({u'tagList': tagList.get_text().strip('\n')})

                onsale = name.find("a", {"class": "totalSellCount"})
                info_dict.update(
                    {u'onsale': onsale.span.get_text().strip('\n')})

                onrent = name.find("a", {"title": title + u"租房"})
                info_dict.update(
                    {u'onrent': onrent.get_text().strip('\n').split(u'套')[0]})

                info_dict.update({u'id': name.get('data-housecode')})

                price = name.find("div", {"class": "totalPrice"})
                info_dict.update({u'price': price.span.get_text().strip('\n')})

                communityinfo = get_communityinfo_by_url(link)
                for key, value in communityinfo.iteritems():
                    info_dict.update({key: value})

                info_dict.update({u'city': city})
            except:
                continue
            # communityinfo insert into mysql
            data_source.append(info_dict)

        # return data_source
    df = pd.DataFrame(data_source)
    df.to_csv('community_by_region.csv')


def get_house_by_region(city, district):
    """
    get the house data
    """
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"ershoufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    data_source = []
    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + u"ershoufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetHouseByRegionlist", district, page + 1, total_pages)
        hisprice_data_source = []
        for ultag in soup.findAll("ul", {"class": "sellListContent"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "title"})
                    info_dict.update(
                        {u'title': housetitle.a.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get('href')})
                    houseID = housetitle.a.get('data-housecode')
                    info_dict.update({u'houseID': houseID})

                    houseinfo = name.find("div", {"class": "houseInfo"})
                    info = houseinfo.get_text().split('|')
                    info_dict.update({u'housetype': info[0]})
                    info_dict.update({u'square': info[1]})
                    info_dict.update({u'direction': info[2]})
                    info_dict.update({u'decoration': info[3]})
                    info_dict.update({u'floor': info[4]})
                    info_dict.update({u'years': info[5]})

                    housefloor = name.find("div", {"class": "positionInfo"})
                    communityInfo = housefloor.get_text().split('-')
                    info_dict.update({u'community': communityInfo[0]})

                    followInfo = name.find("div", {"class": "followInfo"})
                    info_dict.update(
                        {u'followInfo': followInfo.get_text().strip()})

                    taxfree = name.find("span", {"class": "taxfree"})
                    if taxfree == None:
                        info_dict.update({u"taxtype": ""})
                    else:
                        info_dict.update(
                            {u"taxtype": taxfree.get_text().strip()})

                    totalPrice = name.find("div", {"class": "totalPrice"})
                    info_dict.update(
                        {u'totalPrice': totalPrice.span.get_text()})

                    unitPrice = name.find("div", {"class": "unitPrice"})
                    info_dict.update(
                        {u'unitPrice': unitPrice.get("data-price")})
                except:
                    continue

                # Houseinfo insert into mysql
                data_source.append(info_dict)
                hisprice_data_source.append(
                    {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"]})

    df = pd.DataFrame(data_source)
    df.to_csv('house_by_region.csv'.format(city, district))


def get_rent_by_region(city, district):
    """
    get rent data
    """
    baseUrl = u"http://%s.lianjia.com/" % (city)
    url = baseUrl + u"zufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    data_source = []
    for page in range(total_pages):
        if page > 0:
            url_page = baseUrl + u"zufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByRegionlist", district, page + 1, total_pages)
        for ultag in soup.findAll("ul", {"class": "house-lst"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "info-panel"})
                    info_dict.update(
                        {u'title': housetitle.h2.a.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get("href")})
                    houseID = name.get("data-housecode")
                    info_dict.update({u'houseID': houseID})

                    region = name.find("span", {"class": "region"})
                    info_dict.update({u'region': region.get_text().strip()})

                    zone = name.find("span", {"class": "zone"})
                    info_dict.update({u'zone': zone.get_text().strip()})

                    meters = name.find("span", {"class": "meters"})
                    info_dict.update({u'meters': meters.get_text().strip()})

                    other = name.find("div", {"class": "con"})
                    info_dict.update({u'other': other.get_text().strip()})

                    subway = name.find("span", {"class": "fang-subway-ex"})
                    if subway == None:
                        info_dict.update({u'subway': ""})
                    else:
                        info_dict.update(
                            {u'subway': subway.span.get_text().strip()})

                    decoration = name.find("span", {"class": "decoration-ex"})
                    if decoration == None:
                        info_dict.update({u'decoration': ""})
                    else:
                        info_dict.update(
                            {u'decoration': decoration.span.get_text().strip()})

                    heating = name.find("span", {"class": "heating-ex"})
                    if decoration == None:
                        info_dict.update({u'heating': ""})
                    else:
                        info_dict.update(
                            {u'heating': heating.span.get_text().strip()})

                    price = name.find("div", {"class": "price"})
                    info_dict.update(
                        {u'price': int(price.span.get_text().strip())})

                    pricepre = name.find("div", {"class": "price-pre"})
                    info_dict.update(
                        {u'pricepre': pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)

    df = pd.DataFrame(data_source)
    df.to_csv('rent_by_region.csv'.format(city, district))


def get_communityinfo_by_url(url):
    """
    get community info from url
    """
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    communityinfos = soup.findAll("div", {"class": "xiaoquInfoItem"})
    res = {}
    for info in communityinfos:
        key_type = {
            u"建筑年代": u'year',
            u"建筑类型": u'housetype',
            u"物业费用": u'cost',
            u"物业公司": u'service',
            u"开发商": u'company',
            u"楼栋总数": u'building_num',
            u"房屋总数": u'house_num',
        }
        try:
            key = info.find("span", {"xiaoquInfoLabel"})
            value = info.find("span", {"xiaoquInfoContent"})
            key_info = key_type[key.get_text().strip()]
            value_info = value.get_text().strip()
            res.update({key_info: value_info})

        except:
            continue
    return res


def check_block(soup):
    """
    checks if ip is blocked
    """
    if soup.title.string == "414 Request-URI Too Large":
        logging.error(
            "Lianjia block your ip, please verify captcha manually at lianjia.com")
        return True
    return False


def log_progress(function, address, page, total):
    """
    log to indicate progress
    """
    logging.info("Progress: %s %s: current page %d total pages %d" %
                 (function, address, page, total))


if __name__ == "__main__":
    regionlist = [u'dongcheng']
    city = 'bj'
    get_house_from_region(city, regionlist)
    get_rent_from_region(city, regionlist)
    get_community_from_region(city, regionlist)
    communitylist = ['bj']
    get_sales_from_community(city, communitylist)
