az functionapp create \
  --resource-group your-resource-group \
  --consumption-plan-location ukwest \
  --runtime python \
  --functions-version 4 \
  --name upload-image-function \
  --storage-account your-storage-account \
  --os-type Linux

  az storage account create \
  --name your-storage-account \
  --resource-group your-resource-group \
  --location ukwest \
  --sku Standard_LRS

  az storage container create \
  --name your-container-name \
  --account-name your-storage-account \
  --public-access on
