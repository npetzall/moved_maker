module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr

  public_subnets = var.public_subnets
  private_subnets = var.private_subnets
}

module "compute" {
  source = "./modules/compute"

  project_name = var.project_name
  environment  = var.environment

  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids

  instance_type = var.instance_type
  ami_id        = var.ami_id
  instance_count = var.instance_count
}

module "database" {
  source = "./modules/database"

  project_name = var.project_name
  environment  = var.environment

  vpc_id            = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_id = module.compute.app_security_group_id

  engine_version = var.db_engine_version
  instance_class = var.db_instance_class
  allocated_storage = var.db_allocated_storage
}

module "storage" {
  source = "./modules/storage"

  project_name = var.project_name
  environment  = var.environment

  enable_versioning = var.enable_s3_versioning
  enable_encryption  = var.enable_s3_encryption
}
