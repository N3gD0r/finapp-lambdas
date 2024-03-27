data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_lambda_function" "login" {
    for_each    = { for app in var.lambdaApps : app => app }
    filename    = "../artifacts/${var.lambdasVersion}/${each.value}.zip"
    function_name = each.value
    layers = [aws_lambda_layer_version.pymysql_layer.arn]
    role        = aws_iam_role.iam_for_lambda.arn
    handler     = "index.handler"
    runtime     = "python3.12"
    memory_size = "256"
    timeout     = "200"
  
}

