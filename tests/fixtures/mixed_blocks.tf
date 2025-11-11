resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}

data "aws_ami" "example" {
  most_recent = true
}

variable "test" {
  description = "Test variable"
}

locals {
  x = 1
}

