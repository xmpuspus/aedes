import pandas as pd                        
from pytrends.request import TrendReq
pytrend = TrendReq()

# PH-00 for Metro Manila, PH-14 for ARMM, etc. this is the reference: https://en.wikipedia.org/wiki/ISO_3166-2:PH
geo_tag = "PH-00" 

def get_search_trends(geo_tag):
    # Instantiate dengue payload with one keyword
    pytrend.build_payload(kw_list=['dengue'], geo=geo_tag)

    # Get all related queries (top and rising)
    related_queries = pytrend.related_queries()

    # Update payload with top related queries
    list_to_search = ['dengue'] + related_queries['dengue']['top'].head(4)['query'].values.flatten().tolist()

    # Add in ther dengue-related payloads
    pytrend.build_payload(kw_list=list_to_search, geo=geo_tag)

    # Get historical dengue data
    historical_search_df = pytrend.interest_over_time()
    
    return historical_search_df
