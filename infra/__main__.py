import json
import os
import pulumi
import pulumi_aws as aws


SCRIPTS = [
    "../get_expenses.py",
    "../get_expense.py",
    "../get_chat_history.py",
    "../get_categories.py",
    "../get_category.py",
    "../update_expense.py",
    "../delete_expense.py",
    "../delete_chats.py",
    "../post_expense.py",
    "../post_chat_history.py",
    "../register.py",
    "../login.py"
]
ENV = {
    "DB_USER": os.getenv("DB_USER"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD"),
    "DB_HOST": os.getenv("DB_HOST"),
    "DB_PORT": os.getenv("DB_PORT"),
    "DB_NAME": os.getenv("DB_NAME"),
    "JWT_SECRET": os.getenv("JWT_SECRET")
}
S3_BUCKET = os.getenv("BUCKET")
S3_KEY = os.getenv('S3_KEY')
S3_KEY_VERSION = os.getenv('S3_KEY_VERSION')


def main():
    secrets_policy = aws.iam.Policy(
        resource_name="lambda-policy",
        name="get-secrets-policy",
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "secretsmanager:GetSecretValue",
                "Effect": "Allow",
                "Resource": "*",
            }],
        })
    )

    role = aws.iam.Role(
        resource_name="lambda-role",
        name="lambda-role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
            }],
        }),
        managed_policy_arns=[
            aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
            secrets_policy.arn
        ]
    )

    lambda_layer = aws.lambda_.LayerVersion(
        resource_name="lambda-layer",
        layer_name="ai-budget-layer",
        description="Deps for lambda function endpoints in ai budget api",
        compatible_runtimes=["python3.12"],
        compatible_architectures=["x86_64"],
        s3_bucket=S3_BUCKET,
        s3_key=S3_KEY,
        skip_destroy=False
    )

    lambdas = {}
    for script in SCRIPTS:
        name = script[3:-3]
        lambda_code = pulumi.FileAsset(path=script)
        func = aws.lambda_.Function(
            resource_name=f"lambda-{name}",
            name=name,
            runtime="python3.12",
            handler=f"{name}.handler",
            role=role.arn,
            code=pulumi.AssetArchive(assets={script: lambda_code}),
            layers=[lambda_layer.arn],
            environment=aws.lambda_.FunctionEnvironmentArgs(
                variables=ENV
            )
        )
        lambdas[name] = func.arn

    pulumi.export("lambdas", lambdas)
    pulumi.export("layer", lambda_layer.arn)
    pulumi.export("role", role.arn)

    return lambdas, lambda_layer, role


if __name__ == '__main__':
    main()

