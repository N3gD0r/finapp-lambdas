variable "lambdasVersion" {
  type        = string
  description = "version of the lambdas zip on S3"
}

variable "lambdaApps" {
    type = list(string)
    description = "lambda names"
    default = ["delete_expense", "get_categories", "get_category", "get_chat_history", "get_expense", "get_expenses", "login", "post_chat_history", "post_expense", "register", "update_expense"]
}

variable "lambdaLayers" {
    type = list(string)
    description = "lambda layer names"
    default = [ "pymysql_layer" ]
}

