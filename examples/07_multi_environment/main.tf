module "development" {
  source = "./modules/environment"

  environment = "dev"
  project_name = var.project_name

  instance_type = "t3.micro"
  instance_count = 1

  database_instance_class = "db.t3.micro"
  database_allocated_storage = 10

  enable_monitoring = false
  enable_backup = false
}

module "staging" {
  source = "./modules/environment"

  environment = "staging"
  project_name = var.project_name

  instance_type = "t3.small"
  instance_count = 2

  database_instance_class = "db.t3.small"
  database_allocated_storage = 50

  enable_monitoring = true
  enable_backup = true
}

module "production" {
  source = "./modules/environment"

  environment = "prod"
  project_name = var.project_name

  instance_type = "t3.medium"
  instance_count = 3

  database_instance_class = "db.t3.medium"
  database_allocated_storage = 100

  enable_monitoring = true
  enable_backup = true
}

module "shared_resources" {
  source = "./modules/shared"

  project_name = var.project_name

  environments = ["dev", "staging", "prod"]
}
