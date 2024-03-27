from db_auth import get_credentials
from expenses_persistence import ExpenseCategoriesRepositoryImplementation as Repository
from pymysql import MySQLError

import datetime
import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']
    secret_name = os.environ['SECRETS_NAME']
    creds = get_credentials(secret_name)

    id = event['pathParameters']['id']

    try:
        repo = Repository(
            host=rds_host,
            user=creds['username'],
            password=creds['password'],
            db_name=db_name,
            db_port=int(db_port)
        )
        record = repo.get(int(id))
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    if record is None:
        raise Exception(f'Entity with id {id} not found')

    category = record.get_dict()

    for key in category.keys():
        if isinstance(category[key], datetime.datetime):
            category[key] = category[key].strftime('%Y-%m-%d %H:%M:S')

    return {
        'category': category
    }

