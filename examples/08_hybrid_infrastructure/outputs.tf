output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "web_server_ip" {
  description = "Public IP of the web server"
  value       = aws_instance.web_server.public_ip
}

output "app_server_ips" {
  description = "Private IPs of app servers"
  value       = aws_instance.app_server[*].private_ip
}

output "app_server_ids" {
  description = "Instance IDs of app servers"
  value       = aws_instance.app_server[*].id
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.database.endpoint
  sensitive   = true
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.static_assets.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.static_assets.arn
}

output "monitoring_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = module.monitoring.dashboard_url
}
