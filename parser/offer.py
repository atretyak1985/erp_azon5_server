#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime as dt
import json
import logging
import re

from bs4 import BeautifulSoup

from models.apartment import ApartamentModel
from parser.utils import get_content_for_url

try:
    from __builtin__ import unicode
except ImportError:
    unicode = lambda x, *args: x

log = logging.getLogger(__file__)


def get_title(offer_markup):
    """ Searches for offer title on offer page

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Title of offer
    :rtype: str, None
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    return html_parser.h1.text.strip()

def get_poster_name(offer_markup):
    """ Searches for poster name

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Poster name or None if poster name was not found (offer is outdated)
    :rtype: str, None

    :except: Poster name not found
    """
    poster_name_parser = BeautifulSoup(offer_markup, "html.parser").find(class_="offer-user__details")
    try:
        if poster_name_parser.a is not None:
            found_name = poster_name_parser.a.text.strip()
        else:
            found_name = poster_name_parser.h4.text.strip()
    except AttributeError:
        return
    return found_name

def get_gps(offer_markup):
    """ Searches for gps coordinates (latitude and longitude)

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Tuple of gps coordinates
    :rtype: tuple
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")

    if html_parser.find(class_="mapcontainer") is not None:
        gps_lat = html_parser.find(class_="mapcontainer").attrs['data-lat']
        gps_lon = html_parser.find(class_="mapcontainer").attrs['data-lon']
    else:
        gps_lat = 0
        gps_lon = 0

    return gps_lat, gps_lon

def parse_description(offer_markup):
    """ Searches for description if offer markup

    :param offer_markup: Body from offer page markup
    :type offer_markup: str
    :return: Description of offer
    :rtype: str
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    return html_parser.find(id="textContent").text.replace("  ", "").replace("\n", " ").replace("\r", "").strip()

def get_month_num_for_string(value):
    value = value.lower()[:3]
    return {
        'січ': 1,
        'лют': 2,
        'бер': 3,
        'кві': 4,
        'тра': 5,
        'чер': 6,
        'лип': 7,
        'сер': 8,
        'вер': 9,
        'жов': 10,
        'лис': 11,
        'гру': 12,
    }.get(value)

def get_img_url(offer_markup):
    """ Searches for images in offer markup

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Images of offer in list
    :rtype: list
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    images = html_parser.find_all(class_="bigImage")
    output = []
    for img in images:
        output.append(img.attrs["src"])
    return output

def get_date_added(offer_markup):
    """ Searches of date of adding offer

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Date of adding offer
    :rtype: str
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    date = html_parser.find(class_="offer-titlebox__details").em.contents
    date = date[4] if len(date) > 4 else date[0]
    date = date.replace("Dodane", "").replace("\n", "").replace("  ", "").replace("o ", "").replace(", ", " ")
    # 'в 19:04 24 серпня 2018 '  # 10:09 04 września 2017
    date_parts = date.split(' ')
    hour, minute = map(int, date_parts[1].split(':'))
    month = get_month_num_for_string(date_parts[3])
    year = int(date_parts[4])
    day = int(date_parts[2])
    date_added = dt.datetime(year=year, hour=hour, minute=minute, day=day, month=month)
    return int((date_added - dt.datetime(1970, 1, 1)).total_seconds())

def parse_tracking_data(offer_markup):
    """ Parses price and add_id from OLX tracking data script

    :param offer_markup: Head from offer page
    :type offer_markup: str
    :return: Tuple of int price and it's currency or None if this offer page got deleted
    :rtype: dict

    :except: This offer page got deleted and has no tracking script.
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    scripts = html_parser.find_all('script')

    for script in scripts:
        if script.string and "pageView" in script.string:
            data = script.string
            break

    try:
        split_data = re.split('"pageView":|;', data)
        data_dict = json.loads(split_data[3].replace('{', "{").replace("}}'", "}"))
    except json.JSONDecodeError as e:
        logging.info("JSON failed to parse pageView offer attributes. Error: {0}".format(e))
        data_dict = {}
    return data_dict

def parse_flat_data(offer_markup):
    """ Parses data from script of Google Tag Manager

    :param offer_markup: Body from offer page markup
    :type offer_markup: str
    :return: GPT dict data
    :rtype: dict
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    scripts = html_parser.find_all('script')

    for script in scripts:
        if script.string and "GPT.targeting =" in script.string:
            data = script.string
            break
    try:
        split_data = re.split('GPT.targeting = |;', data)
        data_dict = json.loads(split_data[2].replace(";", ""))
    except json.JSONDecodeError as e:
        logging.info("JSON failed to parse GPT offer attributes. Error: {0}".format(e))
        data_dict = {}
    return data_dict

def parse_region(offer_markup):
    """ Parses region information

    :param offer_markup: Class "offerbody" from offer page markup
    :type offer_markup: str
    :return: Region of offer
    :rtype: list
    """
    html_parser = BeautifulSoup(offer_markup, "html.parser")
    region = html_parser.find(class_="show-map-link").text
    return region.replace(", ", ",").split(",")

def parse_offer(url):
    """ Parses data from offer page url

    :param url: Offer page markup
    :param url: Url of current offer page
    :type url: str
    :return: Dictionary with all offer details or None if offer is not available anymore
    :rtype: dict, None
    """
    log.info(url)
    html_parser = BeautifulSoup(get_content_for_url(url).content, "html.parser")
    offer_content = str(html_parser.body)
    poster_name = get_poster_name(offer_content)
    data_track = parse_tracking_data(str(html_parser))
    data_dict = parse_flat_data(offer_content)
    region = parse_region(offer_content)
    if len(region) == 3:
        city, area, district = region
    else:
        city, area = region
        district = None


    apartment = ApartamentModel()

    apartment.add_id = data_track.get("ad_id"),
    apartment.title = get_title(offer_content),
    apartment.price = data_dict.get("ad_price"),
    apartment.currency = data_dict.get("currency"),
    apartment.city = city,
    apartment.district = district,
    apartment.region = area,
    apartment.gps = get_gps(offer_content),
    apartment.description = parse_description(offer_content),
    apartment.poster_name = poster_name,
    apartment.url = url,
    apartment.date_added = get_date_added(offer_content),
    apartment.images = get_img_url(offer_content),
    apartment.private_business = data_dict.get("private_business"),
    apartment.total_area = data_dict.get("total_area"),
    apartment.number_of_rooms = data_dict.get("number_of_rooms"),
    return apartment
