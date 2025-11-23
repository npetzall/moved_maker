module "web_server" {
  source = "./modules/web"

  instance_count = 3
  instance_type  = "t3.medium"
}
