variable "aws_region" {
  description = "AWS region to deploy to"
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "Name of the AWS CLI profile to use"
  default     = "perspectiv"
}

variable "project_name" {
  description = "Base name for AWS resources"
  default     = "perspectiv-trader"
}
