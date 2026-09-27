#!/bin/bash

# Configuration
RESOURCE_GROUP="gramvaani-rg"
LOCATION="centralindia"
CONTAINER_APP_NAME="gramvaani-backend"
CONTAINER_REGISTRY="gramvaaniregistry"
IMAGE_NAME="gramvaani-backend"
IMAGE_TAG="latest"

echo "🚀 Deploying Gram Vaani Backend to Azure Container Apps"

# 1. Create Resource Group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY \
  --sku Basic \
  --admin-enabled true

# 3. Build and Push Docker Image
echo "🔨 Building Docker image..."
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image $IMAGE_NAME:$IMAGE_TAG \
  --file Dockerfile .

# 4. Get ACR credentials
echo "🔑 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query loginServer -o tsv)

# 5. Create Container App Environment
echo "🌍 Creating Container App Environment..."
az containerapp env create \
  --name gramvaani-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# 6. Deploy Container App
echo "🚢 Deploying Container App..."
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment gramvaani-env \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    MONGO_URL=secretref:mongo-url \
    AZURE_OPENAI_ENDPOINT=secretref:azure-openai-endpoint \
    AZURE_OPENAI_API_KEY=secretref:azure-openai-key \
    AZURE_OPENAI_DEPLOYMENT=secretref:azure-openai-deployment \
    AZURE_SPEECH_KEY=secretref:azure-speech-key \
    AZURE_SPEECH_REGION=secretref:azure-speech-region \
    OPENWEATHER_API_KEY=secretref:openweather-key \
    SECRET_KEY=secretref:secret-key \
    AWS_ACCESS_KEY_ID=secretref:aws-access-key \
    AWS_SECRET_ACCESS_KEY=secretref:aws-secret-key \
    AWS_DEFAULT_REGION=ap-south-1

# 7. Get the app URL
APP_URL=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "✅ Deployment complete!"
echo "🌐 Backend URL: https://$APP_URL"
echo ""
echo "⚙️  Next steps:"
echo "1. Add secrets using: az containerapp secret set"
echo "2. Update frontend API URL to: https://$APP_URL"
