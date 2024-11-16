import random
import string
import pandas as pd
from api.v1.models import *
import datetime
import secrets
from django.db.models import Q


def SearchCategoryRecord(category_dataframe, search):
    results = category_dataframe[
        category_dataframe['name'].str.contains(search, case=False) ]
    return results

def generate_sku_id():
    S = 11
    flag = True
    while flag:
        ran_data = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
        if not ProductMaster.objects.filter(sku_id=ran_data).exists():
            flag = False
    return ran_data


def SearchProductRecord(product_dataframe, search):
    # try:
        results = product_dataframe[
            product_dataframe['name'].str.contains(search, case=False) |
            product_dataframe['sku_id'].str.contains(search, case=False) |
            product_dataframe['product_category__name'].str.contains(search, case=False)
            ]
        return results