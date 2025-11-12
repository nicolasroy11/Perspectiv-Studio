terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}


# S3: Static Frontend Hosting

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-frontend"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  index_document { suffix = "index.html" }
  error_document { key = "index.html" }
}

resource "aws_s3_object" "frontend_files" {
  for_each = fileset("${path.module}/../client/out", "**")

  bucket       = aws_s3_bucket.frontend.id
  key          = each.value
  source       = "${path.module}/../client/out/${each.value}"
  etag         = filemd5("${path.module}/../client/out/${each.value}")
  content_type = lookup(
    {
      html = "text/html",
      js   = "application/javascript",
      css  = "text/css",
      json = "application/json",
      png  = "image/png",
      jpg  = "image/jpeg",
      jpeg = "image/jpeg",
      svg  = "image/svg+xml"
    },
    regex("\\.([^.]+)$", each.value)[0],
    "binary/octet-stream"
  )
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend_public" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Sid       = "AllowPublicRead",
      Effect    = "Allow",
      Principal = "*",
      Action    = ["s3:GetObject"],
      Resource  = "${aws_s3_bucket.frontend.arn}/*"
    }]
  })
}

# HHTPS for S3 via CloudFront - perspectivstudio.com
resource "aws_cloudfront_distribution" "frontend_cdn" {
  enabled             = true
  default_root_object = "index.html"

  aliases = ["perspectivstudio.com", "www.perspectivstudio.com"]

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3-frontend"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-frontend"

    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  viewer_certificate {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:451747690945:certificate/7aed5e77-d165-4ae0-a285-78101e72b35e"
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  price_class = "PriceClass_100"

  tags = {
    Name = "perspectivstudio-frontend"
  }
}

# Record in Route 53 for frontend
resource "aws_route53_record" "frontend_root" {
  zone_id = "Z02046181Y2WZAT0IAV45"
  name    = "perspectivstudio.com"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.frontend_cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "frontend_www" {
  zone_id = "Z02046181Y2WZAT0IAV45"
  name    = "www.perspectivstudio.com"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.frontend_cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

# Networking
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}


# Security Groups
resource "aws_security_group" "alb_sg" {
  name        = "${var.project_name}-alb-sg"
  description = "ALB ingress"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_instances_sg" {
  name        = "${var.project_name}-ecs-sg"
  description = "ECS instances"
  vpc_id      = data.aws_vpc.default.id

  # SSH for VS Code
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  # Allow ALB to reach containers
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# ECR

resource "aws_ecr_repository" "backend" {
  name = "${var.project_name}-backend"
}


# ECS Cluster (EC2)

resource "aws_ecs_cluster" "backend_cluster" {
  name = "${var.project_name}-cluster"
}


# IAM Roles

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-task-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ecs-tasks.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role" "ecs_instance_role" {
  name = "${var.project_name}-ecs-instance-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ec2.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_ecs" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "${var.project_name}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}


# ECS AMI, Launch Template, ASG

data "aws_ssm_parameter" "ecs_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}

locals {
  ecs_user_data = base64encode(<<EOF
#!/bin/bash
echo "ECS_CLUSTER=${aws_ecs_cluster.backend_cluster.name}" >> /etc/ecs/ecs.config
EOF
  )
}

resource "aws_launch_template" "ecs_lt" {
  name_prefix   = "${var.project_name}-ecs-"
  image_id      = data.aws_ssm_parameter.ecs_ami.value
  instance_type = var.instance_type
  key_name      = var.key_name

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }

  vpc_security_group_ids = [aws_security_group.ecs_instances_sg.id]
  user_data              = local.ecs_user_data
}

resource "aws_autoscaling_group" "ecs_asg" {
  name                = "${var.project_name}-ecs-asg"
  min_size            = 1
  max_size            = 2
  desired_capacity    = 1
  vpc_zone_identifier = data.aws_subnets.default.ids
  health_check_type   = "EC2"

  launch_template {
    id      = aws_launch_template.ecs_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-ecs-instance"
    propagate_at_launch = true
  }
}

resource "aws_ecs_capacity_provider" "cp" {
  name = "${var.project_name}-cp"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.ecs_asg.arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      status          = "ENABLED"
      target_capacity = 100
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "attach_cp" {
  cluster_name       = aws_ecs_cluster.backend_cluster.name
  capacity_providers = [aws_ecs_capacity_provider.cp.name]
  default_capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.cp.name
    weight            = 1
  }
}


# Logs + Task Definition

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "backend_task" {
  family                   = "${var.project_name}-task"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "backend",
      image     = "${aws_ecr_repository.backend.repository_url}:latest",
      essential = true,
      portMappings = [
        { containerPort = 8000, hostPort = 8000, protocol = "tcp" }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}


# ALB, Listener and Target Group
resource "aws_lb" "trader_alb" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = data.aws_subnets.default.ids
}

resource "aws_lb_target_group" "trader_tg" {
  name        = "${var.project_name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "instance"

  health_check {
    path              = "/"
    interval          = 30
    timeout           = 5
    healthy_threshold = 3
  }
}

resource "aws_lb_listener" "trader_listener" {
  load_balancer_arn = aws_lb.trader_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.trader_tg.arn
  }
}

# --- Route 53 alias record for trader backend API ---
resource "aws_route53_record" "trader_api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "trader-api.${var.domain_name}"   # trader-api.perspectivstudio.com
  type    = "A"

  alias {
    name                   = aws_lb.trader_alb.dns_name
    zone_id                = aws_lb.trader_alb.zone_id
    evaluate_target_health = true
  }
}

# --- Lookup existing hosted zone ---
data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

# --- ACM certificate for HTTPS ---
resource "aws_acm_certificate" "perspectiv_cert" {
  domain_name       = "trader-api.${var.domain_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# DNS validation record
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.perspectiv_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  zone_id = data.aws_route53_zone.main.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}

# Wait for validation
resource "aws_acm_certificate_validation" "perspectiv_cert_validation" {
  certificate_arn         = aws_acm_certificate.perspectiv_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# --- HTTPS listener on ALB ---
resource "aws_lb_listener" "trader_https_listener" {
  load_balancer_arn = aws_lb.trader_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate_validation.perspectiv_cert_validation.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.trader_tg.arn
  }

  depends_on = [aws_acm_certificate_validation.perspectiv_cert_validation]
}

# ECS Service
resource "aws_ecs_service" "backend_service" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.backend_cluster.id
  task_definition = aws_ecs_task_definition.backend_task.arn
  desired_count   = 1

  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.cp.name
    weight            = 1
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.trader_tg.arn
    container_name   = "backend"
    container_port   = 8000
  }

  enable_execute_command = true

  depends_on = [aws_lb_listener.trader_listener]
}


# Outputs

output "alb_dns_name" {
  value       = aws_lb.trader_alb.dns_name
  description = "Public DNS name of the ALB"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.backend_cluster.name
  description = "ECS cluster name"
}

output "ecs_service_name" {
  value       = aws_ecs_service.backend_service.name
  description = "ECS service name"
}

output "ecr_repo_url" {
  value       = aws_ecr_repository.backend.repository_url
  description = "ECR repository URL for backend image"
}
