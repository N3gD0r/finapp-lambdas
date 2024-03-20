from expenses_persistence import ExpenseCategoriesRepositoryImplementation as Repository
from pymysql import MySQLError

import datetime
import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    name = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']

    id = event['pathParameters']['id']

    try:
        record = Repository(
            host=rds_host,
            user=name,
            password=password,
            db_name=db_name,
            db_port=int(db_port)
        ).get(int(id))
    except MySQLError:
        return {
            'error': 'Internal server error'
        }

    if record is None:
        raise Exception(f'Entity with id {id} not found')

    category = record.get_dict()

    for key in category.keys():
        if isinstance(category[key], datetime.datetime):
            category[key] = category[key].strftime('%Y-%m-%d %H:%M:S')

    return {
        'category': category
    }

