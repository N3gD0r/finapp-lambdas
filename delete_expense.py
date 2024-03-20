from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    name = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']

    id = event['pathParameters']['id']

    try:
        deleted = Repository(
            host=rds_host,
            db_port=int(db_port),
            user=name,
            password=password,
            db_name=db_name
        ).delete(int(id))
    except MySQLError:
        return {
            'error': 'Internal server error'
        }

    return {
        'deleted': deleted
    }

