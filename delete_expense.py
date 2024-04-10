from load_secrets import get_env
from expenses_persistence import ExpenseRepositoryImplementation as Repository
from pymysql import MySQLError

import jwt
import os


def handler(event, context):
    secrets = get_env()

    db_name = 'expenses'
    db_host = secrets.get('db_host')
    db_port = secrets.get('db_port')
    db_user = secrets.get('username')
    db_password = secrets.get('password')
    secret_key = secrets.get('jwt_key')

    id = event['pathParameters']['id']
    token = event['Authorization'].split(' ')[1]
    token_data = jwt.decode(jwt=token, key=secret_key, algorithms=['HS256'])
    user_id = token_data.get('user_id')

    try:
        repo = Repository(
            host=db_host,
            db_port=int(db_port),
            user=db_user,
            password=db_password,
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

