resource "null_resource" "storage" {
  triggers = {
    environment = var.environment
    retention   = var.retention_days
  }
}
