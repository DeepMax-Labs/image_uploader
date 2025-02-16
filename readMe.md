# 📌 README.md – Deploying an Image Upload Function on Azure

## 🖼️ Azure Function: Upload Images to Blob Storage

This project contains an **Azure Function** that allows users to **upload images (JPG, JPEG, PNG) via HTTP** and store them in **Azure Blob Storage**. It is designed to work on **Linux Consumption Plan** and supports authentication via function keys.

---

## 🚀 Features

- 📂 **Uploads images to Azure Blob Storage** (supports `.jpg`, `.jpeg`, `.png`).
- 🌐 **Publicly accessible image URLs** for direct viewing in browsers.
- 🔑 **Secured API with function-level authentication**.
- 🔄 **Automatic timestamp-based file naming** to avoid overwrites.

---

## 🛠️ Prerequisites

Ensure you have the following set up **before** proceeding:

1. **Azure Subscription** ([Sign up for free](https://azure.microsoft.com/en-us/free/))
2. **Azure CLI** installed ([Guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli))
3. **Azure Functions Core Tools** ([Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local))
4. **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
5. **Git** installed ([Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))

---

## 🏗️ Setting Up Locally

### 1️⃣ **Clone the Repository**

```sh
git clone https://github.com/<YourOrganizationName>/<RepoName>.git
cd <RepoName>
```

2️⃣ Create and Activate a Virtual Environment

```sh
python -m venv .venv
source .venv/bin/activate  # For macOS/Linux

# OR

.venv\Scripts\activate     # For Windows

```

3️⃣ Install Dependencies

```sh
pip install -r requirements.txt
```

4️⃣ Configure Local Environment Variables

Create a local.settings.json file in the project root to store environment variables:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<Your_Storage_Account_Connection_String>",
    "MY_STORAGE_CONNECTION_STRING": "<Your_Storage_Account_Connection_String>",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

Replace <Your_Storage_Account_Connection_String> with your Azure Storage Account Connection String.
I have placed an examle local.settings.json file in the repo with the name local.settings.example.json.
You can rename it to local.settings.json and replace the values with your own.

    ⚠️ DO NOT commit local.settings.json to GitHub as it contains secrets.

🌍 Running Locally

Start the function locally with:

func start

Once running, you’ll see output like:

Functions:

    upload_image_function: [POST] http://localhost:7071/api/upload

Use this URL to test image uploads.
📤 Deploying to Azure
1️⃣ Log in to Azure

az login

2️⃣ Create a Resource Group

```sh
az group create --name ImageUploadGroup --location ukwest

```

3️⃣ Create an Azure Storage Account

```sh
az storage account create \
  --name imagestoragesample \
  --resource-group ImageUploadGroup \
  --location ukwest \
  --sku Standard_LRS
```

4️⃣ Create the Function App on Linux Consumption Plan

```sh
az functionapp create \
  --resource-group ImageUploadGroup \
  --consumption-plan-location ukwest \
  --runtime python \
  --functions-version 4 \
  --name upload-image-function \
  --storage-account imagestoragesample \
  --os-type Linux
```

5️⃣ Set Environment Variables in Azure

```sh
az functionapp config appsettings set \
  --name upload-image-function \
  --resource-group ImageUploadGroup \
  --settings "MY_STORAGE_CONNECTION_STRING=<Your_Storage_Account_Connection_String>"
```

6️⃣ Deploy the Function to Azure

```sh
func azure functionapp publish upload-image-function
```

🔑 Authentication (Function Key)

Since this function uses Function-level authentication, every request must include an API Key.
Find Your Function Key

Run:

```sh
az functionapp keys list --name upload-image-function --resource-group ImageUploadGroup --query "functionKeys"
```

Or, in Azure Portal:

    Go to Function App > Functions > upload_image_function > Keys.
    Copy an existing key or create a new one.

🎯 Testing the Deployed Function
Postman (Recommended)

    Method: POST

    URL:

https://upload-image-function.azurewebsites.net/api/upload?code=<YOUR-FUNCTION-KEY>

Body: Select form-data, then:

    Key: file
    Type: File
    Value: Select an image (.jpg, .jpeg, .png)

Click Send, and you should receive:

```json
{
  "imageUrl": "https://imagestoragesample.blob.core.windows.net/asm/news_images/20240118_example.jpg",
  "fileName": "example.jpg",
  "contentType": "image/jpeg",
  "message": "Uploaded successfully!"
}
```

cURL Alternative

curl -X POST -F "file=@/path/to/image.jpg" \
 "https://upload-image-function.azurewebsites.net/api/upload?code=<YOUR-FUNCTION-KEY>"

👀 Viewing Uploaded Images

Once uploaded, copy the imageUrl from the response and paste it into your browser.

If it downloads instead of displaying, ensure you set the correct Content-Type:

```python
from azure.storage.blob import ContentSettings
blob_client.upload_blob(
    file_bytes,
    overwrite=True,
    content_settings=ContentSettings(content_type=content_type)  # Ensure proper MIME type
)
```

❓ Troubleshooting
Function Crashes at Startup

    Run func start and check logs.
    Ensure Python 3.8+ is installed.
    Verify local.settings.json is correctly formatted.

Image Upload Fails

    Check if the correct key is provided in ?code=<YOUR-FUNCTION-KEY>.
    Verify the storage account exists and is accessible.
    Check container permissions (Blob (anonymous read access for blobs only) recommended for public URLs).

403 Forbidden on Uploaded Image

    Set container public access:

```sh
    az storage container set-permission \
      --name asm \
      --account-name imagestoragesample \
      --public-access blob
```

🤝 Contributing

Contributions are welcome! Feel free to fork this repository, make improvements, and submit a Pull Request.
📜 License

This project is licensed under the MIT License.
📢 Shoutout on [Youtube](https://www.youtube.com/@artificial_synapse_media)!

🎥 Watch the full tutorial on my YouTube Channel.
If you found this helpful, give a ⭐ on GitHub! 🚀
