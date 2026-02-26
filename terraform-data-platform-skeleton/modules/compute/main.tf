resource "null_resource" "compute" {
  triggers = {
    environment = var.environment
    size        = var.instance_size
  }
}
