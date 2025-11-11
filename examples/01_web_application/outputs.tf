output "web_server_ip" {
  description = "Public IP of the web server"
  value       = aws_instance.web_server.public_ip
}

output "app_server_ips" {
  description = "Private IPs of app servers"
  value       = aws_instance.app_server[*].private_ip
}

output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.static_assets.bucket
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

