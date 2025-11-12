output "frontend_bucket_website_url" {
  value = aws_s3_bucket_website_configuration.frontend.website_endpoint
}