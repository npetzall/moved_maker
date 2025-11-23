# Using a module for networking infrastructure
module "networking" {
  source = "./modules/networking"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# Direct resources for compute instances
resource "aws_instance" "web_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = module.networking.public_subnet_ids[0]

  vpc_security_group_ids = [aws_security_group.web.id]

  tags = merge(
    local.common_tags,
    {
      Name = "Web Server"
      Type = "Web"
    }
  )
}

resource "aws_instance" "app_server" {
  count         = var.app_instance_count
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = module.networking.private_subnet_ids[0]

  vpc_security_group_ids = [aws_security_group.app.id]

  tags = merge(
    local.common_tags,
    {
      Name = "App Server ${count.index + 1}"
      Type = "Application"
    }
  )
}

# Using a module for database
module "database" {
  source = "./modules/database"

  project_name = var.project_name
  environment  = var.environment

  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.private_subnet_ids
  security_group_id = aws_security_group.db.id

  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
}

# Direct resources for security groups
resource "aws_security_group" "web" {
  name        = "${var.project_name}-web-sg"
  description = "Security group for web servers"
  vpc_id      = module.networking.vpc_id

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
      Name = "Web Security Group"
    }
  )
}

resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg"
  description = "Security group for application servers"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port       = 8080
    to_port         = 8080
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
      Name = "App Security Group"
    }
  )
}

resource "aws_security_group" "db" {
  name        = "${var.project_name}-db-sg"
  description = "Security group for database"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
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

# Direct resource for S3 bucket
resource "aws_s3_bucket" "static_assets" {
  bucket = "${var.project_name}-static-assets-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    local.common_tags,
    {
      Name = "Static Assets Bucket"
    }
  )
}

resource "aws_s3_bucket_versioning" "static_assets" {
  bucket = aws_s3_bucket.static_assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Using a module for monitoring
module "monitoring" {
  source = "./modules/monitoring"

  project_name = var.project_name
  environment  = var.environment

  instance_ids = concat(
    [aws_instance.web_server.id],
    aws_instance.app_server[*].id
  )
}
