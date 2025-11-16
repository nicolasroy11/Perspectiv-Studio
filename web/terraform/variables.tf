variable "aws_region"   { default = "us-west-2" }
variable "aws_profile"  { default = "perspectiv" }
variable "project_name" { default = "perspectiv-trader" }

variable "key_name" {
  type    = string
  default = "perspectiv-main-key"
}

variable "ssh_cidr" {
  description = "CIDR allowed to SSH (your IP)"
  type        = string
  default     = "0.0.0.0/0" # tighten to your IP
}

variable "instance_type" {
  description = "EC2 instance type for ECS cluster"
  type        = string
  default     = "t3.small"
}

variable "domain_name" {
  description = "Root domain name in Route 53"
  default     = "perspectivstudio.com"
}
