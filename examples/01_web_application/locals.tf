locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  instance_count = 3
  subnet_cidrs = {
    public  = "10.0.1.0/24"
    private = "10.0.2.0/24"
  }

  db_config = {
    engine         = "postgres"
    engine_version = "13.7"
    instance_class = "db.t3.micro"
  }
}
