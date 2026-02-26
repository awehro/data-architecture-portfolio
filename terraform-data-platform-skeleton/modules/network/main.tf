resource "null_resource" "network" {
  triggers = {
    environment = var.environment
    cidr        = var.vpc_cidr
  }
}
