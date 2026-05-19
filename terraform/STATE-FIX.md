# Notifications state fix (CI error: sales_sg / sales_service in plan)

If Terraform plans to **destroy** `aws_security_group.sales_sg` or `aws_instance.sales_service`,
the S3 object `notifications/terraform.tfstate` was polluted (old Sales config applied with this backend key).

**Do not apply that plan** — it can break Sales.

## Fix (one-time)

1. Confirm Sales still has its own state:
   - S3 key `sales/terraform.tfstate` should manage Sales EC2/SG.

2. Remove only the **notifications** state object (not sales):

```bash
aws s3 rm s3://iteso-terraform-state-inaki-69/notifications/terraform.tfstate
# optional backup first:
# aws s3 cp s3://iteso-terraform-state-inaki-69/notifications/terraform.tfstate ./notifications-state-backup.json
```

3. Re-run **Notifications** CI (or locally):

```bash
cd terraform
terraform init
terraform apply
```

Terraform will create a fresh state with only SNS + Lambda + Function URL.
