# LOCAL (Portfolio-Demo – kein Cloud-Account erforderlich)
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}

# OPTION A: AWS (S3 + DynamoDB) – für echten Einsatz
# terraform {
#   backend "s3" {
#     bucket         = "tractionwise-tfstate-dev"
#     key            = "data-platform/dev/terraform.tfstate"
#     region         = "eu-central-1"
#     encrypt        = true
#     dynamodb_table = "terraform-lock-dev"
#   }
# }

# OPTION B: Azure Storage – für echten Einsatz
# terraform {
#   backend "azurerm" {
#     resource_group_name  = "rg-terraform-state"
#     storage_account_name = "twterraformstate"
#     container_name       = "tfstate"
#     key                  = "data-platform/prod/terraform.tfstate"
#   }
# }
