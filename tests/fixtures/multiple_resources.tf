resource "aws_instance" "web1" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}

resource "aws_instance" "web2" {
  ami           = "ami-12345"
  instance_type = "t3.small"
}

resource "aws_s3_bucket" "data" {
  bucket = "my-bucket"
}

