output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "instance_ids" {
  description = "EC2 instance IDs"
  value       = module.compute.instance_ids
}

output "instance_ips" {
  description = "EC2 instance private IPs"
  value       = module.compute.instance_ips
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.database.endpoint
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.storage.bucket_name
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.storage.bucket_arn
}
