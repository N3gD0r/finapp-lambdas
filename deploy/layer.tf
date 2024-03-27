resource "aws_lambda_layer_version" "pymysql_layer" {
  filename    = "../layers/pymysql.zip"
  layer_name = "pymysql_layer"
  compatible_runtimes = ["python3.12"] 
}