import json
import logging
import re

from bs4 import BeautifulSoup
from scrapper_helpers.utils import flatten
from parser.utils import get_content_for_url, get_url

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

def get_category(main_category=None, sub_category=None, detail_category=None, region=None, search_query=None, url=None,
                 **filters):
    """ Parses available offer urls from given category from every page

    :param url: User defined url for OLX page with offers. It overrides category parameters and applies search filters.
    :param main_category: Main category
    :param sub_category: Sub category
    :param detail_category: Detail category
    :param region: Region of search
    :param search_query: Additional search query
    :param filters: Dictionary with additional filters. Following example dictionary contains every possible filter
    with examples of it's values.

    :Example:

    input_dict = {
        "[filter_float_price:from]": 2000, # minimal price
        "[filter_float_price:to]": 3000, # maximal price
        "[filter_enum_floor_select][0]": 3, # desired floor, enum: from -1 to 11 (10 and more) and 17 (attic)
        "[filter_enum_furniture][0]": True, # furnished or unfurnished offer
        "[filter_enum_builttype][0]": "blok", # valid build types:
        #                                             blok, kamienica, szeregowiec, apartamentowiec, wolnostojacy, loft
        "[filter_float_m:from]": 25, # minimal surface
        "[filter_float_m:to]": 50, # maximal surface
        "[filter_enum_rooms][0]": 2 # desired number of rooms, enum: from 1 to 4 (4 and more)
    }

    :type url: str, None
    :type main_category: str, None
    :type sub_category: str, None
    :type detail_category: str, None
    :type region: str, None
    :type search_query: str, None
    :type filters: dict
    :return: List of all offers for given parameters
    :rtype: list
    """
    parsed_content, page, start_url = [], 0, None
    #city = city_name(region) if region else None
    if url is None:
        url = get_url(main_category, sub_category, detail_category, region, search_query, **filters)
    else:
        start_url = url
    response = get_content_for_url(url)
    page_max = get_page_count(response.content)
    while page < page_max:
        if start_url is None:
            url = get_url(main_category, sub_category, detail_category, region, search_query, page, **filters)
        else:
            url = get_url(page=page, user_url=start_url, **filters)
        log.debug(url)
        response = get_content_for_url(url)
        log.info("Loaded page {0} of offers".format(page))

        offers = parse_available_offers(response.content)
        if offers is None:
            break
        parsed_content.append(offers)

        # parsed_content.append(offers)
        page += 1

    parsed_content = list(flatten(parsed_content))
    log.info("Loaded {0} offers".format(str(len(parsed_content))))
    return parsed_content

def get_page_count(markup):
    """ Reads total page number from OLX search page

    :param markup: OLX search page markup
    :type markup: str
    :return: Total page number extracted from js script
    :rtype: int
    """
    html_parser = BeautifulSoup(markup, "html.parser")
    #script = html_parser.head.script.next_sibling.next_sibling.next_sibling.text.split(",")
    scripts = html_parser.head.find_all('script')
    for script in scripts:
        for element in script:
            if "page_count" in element:
                pages = element.split('"page_count":')
                current = pages[1].split(',')
                out = ""
                for char in current[0]:
                    if char.isdigit():
                        out += char
                return int(out)
    log.warning("Error no page number found. Please check if it's valid olx page.")
    return 1

def parse_available_offers(markup):
    """ Collects all offer links on search page markup

        :param markup: Search page markup
        :type markup: str
        :return: Links to offer on given search page
        :rtype: list
        """
    html_parser = BeautifulSoup(markup, "html.parser")
    not_found = html_parser.find(class_="emptynew")
    if not_found is not None:
        log.warning("No offers found")
        return

    offers = html_parser.find_all(class_='offer-wrapper')
    if len(offers) == 0:
        offers = html_parser.select("li.wrap.tleft")
    parsed_offers = [parse_offer_url(str(offer)) for offer in offers if offer]
    return parsed_offers

def parse_offer_url(markup):
    """ Searches for offer links in markup

    Offer links on OLX are in class "linkWithHash".
    Only www.olx.pl domain is whitelisted.

    :param markup: Search page markup
    :type markup: str
    :return: Url with offer
    :rtype: str
    """
    html_parser = BeautifulSoup(markup, "html.parser")
    url = html_parser.find("a").attrs['href']
    return url if url else None