module "web_server" {
  source = "./modules/web"

  instance_count = 3
  instance_type  = "t3.medium"
}

module "database" {
  source = "./modules/db"

  engine_version = "13.0"
  instance_class = "db.t3.medium"
}

module "cache" {
  source = "./modules/redis"

  node_type = "cache.t3.micro"
}
