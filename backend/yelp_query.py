import requests

from .api_keys import app_auth

YELP_URL = 'https://api.yelp.com/v3'

AUTOCOMPLETE_URL       = YELP_URL+'/autocomplete'
BUSINESS_DETAILS_URL   = YELP_URL+'/businesses/{}'
BUSINESS_SEARCH_URL    = YELP_URL+'/businesses/search'
BUSINESS_MATCH_URL     = YELP_URL+'/businesses/matches'
PHONE_SEARCH_URL       = YELP_URL+'/businesses/search/phone'
TRANSACTION_SEARCH_URL = YELP_URL+'/transactions/{}/search'
REVIEWS_URL            = YELP_URL+'/businesses/{}/reviews'

class YelpFusion:
    def __init__(self):
        self.client_id = app_auth['yelp']['client_id']
        self.api_key   = app_auth['yelp']['api_key']
        self.headers   = {'Authorization': f'Bearer {self.api_key}'}

    def business_search(self, params: dict):
        """ params keys:
                'term'  : Optional. Terms like "food", "restaurants", business names, etc.
                          If not provided, searches across popular categories.
                'latitude'   : Required.
                'longitude'   : Required.
                'radius': Required.
                'categories': Optional. See https://www.yelp.com/developers/documentation/v3/all_category_list
                              for a complete list.
                'limit' : Optional. Default 20, max 50.
                'offset': Optional.
                'sort_by': Optional. Default is best_match; probably choose rating.
                'price' : Optional. Filter with 1, 2, 3, 4. Can be multiple 
                          comma-delimited values.
                'open_at': Optional. Integer representing Unix time in curr timezone.

        """
        return self.__search(BUSINESS_SEARCH_URL, params)

    def __search(self, url: str, params: dict):
        return requests.get(url, headers=self.headers, params=params).json()
