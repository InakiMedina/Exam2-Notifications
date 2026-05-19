terraform {
  backend "s3" {
    bucket = "iteso-terraform-state-inaki-69"
    key    = "notifications/terraform.tfstate"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
