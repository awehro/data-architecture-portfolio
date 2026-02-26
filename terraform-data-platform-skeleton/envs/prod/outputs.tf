output "prod_network"  { value = module.network.network_id }
output "prod_storage"  { value = module.storage.storage_bucket_name }
output "prod_compute"  { value = module.compute.compute_label }
