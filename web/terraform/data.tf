# Discover the default VPC
data "aws_vpc" "main" {
  default = true
}

# Discover all subnets in VPC
data "aws_subnets" "main" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
}

# Get the security groups in that VPC (for ALB or ECS) - opting for this for later...
data "aws_security_groups" "main" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
}
