resource "aws_instance" "web" {
  for_each = {
    "web1" = "ami-12345"
    "web2" = "ami-67890"
  }
  ami           = each.value
  instance_type = "t3.micro"
}
