# Deploy to AWS ECS (Fargate)

```sh
cd infra
export TF_VAR_deepseek_api_key=sk-...
export TF_VAR_gemini_api_key=AIza...
terraform init

# 1. create the image repos first
terraform apply -target=aws_ecr_repository.app

# 2. build + push images (ARM64)
REGISTRY=$(terraform output -json ecr | jq -r .api | cut -d/ -f1)
aws ecr get-login-password | docker login --username AWS --password-stdin $REGISTRY
for app in api web; do
  docker build --platform linux/arm64 -f ../docker/$app.Dockerfile -t $REGISTRY/aistylist-$app:latest ..
  docker push $REGISTRY/aistylist-$app:latest
done

# 3. everything else
terraform apply
terraform output url
```

Redeploy after pushing new images: `aws ecs update-service --cluster aistylist --service aistylist --force-new-deployment`
