from __future__ import print_function

import json
import decimal
import os

import awswrangler as wr
import pandas as pd
print(wr.__version__)
print(pd.__version__)


def handler(event, context):
    return {
        'statusCode': 200,
        'body':"hello"
    }