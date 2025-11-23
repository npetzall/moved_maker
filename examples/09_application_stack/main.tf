# Data sources
data "aws_ami" "latest_amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Module for base infrastructure
module "infrastructure" {
  source = "./modules/infrastructure"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# Direct resources for application load balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.infrastructure.public_subnet_ids

  enable_deletion_protection = var.environment == "prod"

  tags = merge(
    local.common_tags,
    {
      Name = "Application Load Balancer"
    }
  )
}

resource "aws_lb_target_group" "web" {
  name     = "${var.project_name}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.infrastructure.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  tags = local.common_tags
}

resource "aws_lb_listener" "web" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# Direct resources for EC2 instances
resource "aws_instance" "web" {
  count = var.web_instance_count

  ami           = data.aws_ami.latest_amazon_linux.id
  instance_type = var.instance_type
  subnet_id     = module.infrastructure.private_subnet_ids[count.index % length(module.infrastructure.private_subnet_ids)]

  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
  EOF

  tags = merge(
    local.common_tags,
    {
      Name = "Web Server ${count.index + 1}"
    }
  )
}

resource "aws_lb_target_group_attachment" "web" {
  count = var.web_instance_count

  target_group_arn = aws_lb_target_group.web.arn
  target_id        = aws_instance.web[count.index].id
  port             = 80
}

# Module for database cluster
module "database" {
  source = "./modules/database"

  project_name = var.project_name
  environment  = var.environment

  vpc_id            = module.infrastructure.vpc_id
  subnet_ids        = module.infrastructure.private_subnet_ids
  security_group_id = aws_security_group.db.id

  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  multi_az          = var.environment == "prod"
}

# Direct resources for security groups
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = module.infrastructure.vpc_id

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

  tags = merge(
    local.common_tags,
    {
      Name = "ALB Security Group"
    }
  )
}

resource "aws_security_group" "web" {
  name        = "${var.project_name}-web-sg"
  description = "Security group for web servers"
  vpc_id      = module.infrastructure.vpc_id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Web Security Group"
    }
  )
}

resource "aws_security_group" "db" {
  name        = "${var.project_name}-db-sg"
  description = "Security group for database"
  vpc_id      = module.infrastructure.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Database Security Group"
    }
  )
}

# Direct resources for S3 and CloudFront
resource "aws_s3_bucket" "static_content" {
  bucket = "${var.project_name}-static-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    local.common_tags,
    {
      Name = "Static Content Bucket"
    }
  )
}

resource "aws_s3_bucket_public_access_block" "static_content" {
  bucket = aws_s3_bucket.static_content.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_distribution" "static_content" {
  origin {
    domain_name = aws_s3_bucket.static_content.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.static_content.bucket}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.static_content.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.static_content.bucket}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = local.common_tags
}

resource "aws_cloudfront_origin_access_identity" "static_content" {
  comment = "OAI for ${var.project_name} static content"
}

# Module for monitoring and logging
module "observability" {
  source = "./modules/observability"

  project_name = var.project_name
  environment  = var.environment

  instance_ids = aws_instance.web[*].id
  alb_arn      = aws_lb.main.arn
}
