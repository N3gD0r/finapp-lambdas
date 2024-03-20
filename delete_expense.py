from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

import jwt
import os


def handler(event, context):
    rds_host = os.environ['RDS_HOST']
    name = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    db_name = os.environ['RDS_DB_NAME']
    db_port = os.environ['RDS_PORT']
    secret_key = os.environ['SECRET_KEY']

    id = event['pathParameters']['id']
    token = event['Authorization'].split(' ')[1]
    token_data = jwt.decode(jwt=token, key=secret_key, algorithms=['HS256'])
    user_id = token_data.get('user_id')

    try:
        repo = Repository(
            host=rds_host,
            db_port=int(db_port),
            user=name,
            password=password,
            db_name=db_name
        )
        expense_by_user = repo.get_by(user_id=user_id, expense_id=id)

        if not expense_by_user:
            return {
                'deleted': False
            }

        if len(expense_by_user) > 1:
            return {
                'deleted': False
            }
        deleted = repo.delete(int(id))

    except MySQLError:
        raise Exception('Internal server error')

    finally:
        repo.__del__()

    return {
        'deleted': deleted
    }

