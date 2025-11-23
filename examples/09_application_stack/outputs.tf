output "vpc_id" {
  description = "VPC ID"
  value       = module.infrastructure.vpc_id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "web_instance_ids" {
  description = "Instance IDs of web servers"
  value       = aws_instance.web[*].id
}

output "web_instance_ips" {
  description = "Private IPs of web servers"
  value       = aws_instance.web[*].private_ip
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.database.endpoint
  sensitive   = true
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for static content"
  value       = aws_s3_bucket.static_content.bucket
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.static_content.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.static_content.domain_name
}

output "monitoring_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = module.observability.dashboard_url
}
