resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}

module "web_server" {
  source = "./modules/web"

  instance_count = 3
  instance_type  = "t3.medium"
}

resource "aws_s3_bucket" "data" {
  bucket = "my-bucket"
}

module "database" {
  source = "./modules/db"

  engine_version = "13.0"
  instance_class = "db.t3.medium"
}

data "aws_ami" "example" {
  most_recent = true
}
