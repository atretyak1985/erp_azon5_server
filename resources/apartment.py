from flask_restful import Resource, reqparse

from aidata.apartment_utis import ApartmentUtils
from models.apartment import ApartamentModel
from parser.apartment import get_category
from parser.offer import parse_offer
from parser import BASE_URL

class AiApartment(Resource):
    parser = reqparse.RequestParser()

    def get(self):
        apartments = ApartmentUtils.get_apartments();
        return {'apartments': "ok"}, 200



class Category(Resource):
    parser = reqparse.RequestParser()
    parser = reqparse.RequestParser()

    def get(self):
        search_filters = {
            "[filter_float_price:from]": 2000
        }

        count = 0

        parsed_urls = get_category("nedvizhimost", "kvartiry-komnaty", "prodazha-kvartir-komnat", "lvov", **search_filters)
        for element in (parse_offer(url) for url in parsed_urls if url and BASE_URL in url):
            count += 1
            if not(ApartamentModel.find_by_add_id(element.add_id)):
                element.save_to_db()

        # stats = StatsModel.find_by_type(type)
        # if stats:
        #     return stats.json()
        return {'message': 'found ' + str(count) + ' items'}, 200


