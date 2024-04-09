from load_secrets import get_env
from expenses_persistence import ExpenseCategoriesRepositoryImplementation as Repository
from pymysql import MySQLError

import datetime
import os


def handler(event, context):
    secrets = get_env()
    db_name = 'expenses'
    db_host = secrets.get('db_host')
    db_port = secrets.get('db_port')
    db_user = secrets.get('username')
    db_password = secrets.get('password')

    try:
        repo = Repository(
            host=db_host,
            user=db_user,
            password=db_password,
            db_name=db_name,
            db_port=int(db_port)
        )
        records = repo.get_all()
    except MySQLError:
        raise Exception('Internal server error')
    finally:
        repo.__del__()

    if records is None:
        return {
            'categories': []
        }

    categories = [category.get_dict() for category in records]

    for category in categories:
        for key in category.keys():
            if isinstance(category[key], datetime.datetime):
                category[key] = category[key].strftime('%Y-%m-%d %H:%M:S')

    return {
        'categories': categories
    }

