from load_secrets import get_secrets
from expenses_persistence import ExpenseCategoriesRepositoryImplementation as Repository
from pymysql import MySQLError

import datetime
import os


def handler(event, context):
    secret_name = os.environ['SECRETS_NAME']
    secrets = get_secrets(secret_name)
    db_name = 'expenses'
    db_host = secrets.get('db_host')
    db_port = secrets.get('db_port')
    db_user = secrets.get('username')
    db_password = secrets.get('password')

    id = event['pathParameters']['id']

    try:
        repo = Repository(
            host=db_host,
            user=db_user,
            password=db_password,
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

