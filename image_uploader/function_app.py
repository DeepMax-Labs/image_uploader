import json
import logging
import mimetypes
import os

from datetime import datetime
from datetime import timezone

import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings

app = func.FunctionApp()


@app.function_name(name="upload_image_function")
@app.route(route="upload", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def upload_image_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered function that:
    1. Accepts a file via multipart/form-data (field name 'file').
    2. Only supports .jpg/.jpeg/.png types.
    3. Uploads to Azure Blob Storage (container 'asm/news_images').
    4. Returns a JSON response with a publicly accessible or SAS-based URL.
    """
    logging.info("Processing an HTTP POST request to upload an image.")

    try:
        # Check if a file was sent in the 'file' field
        uploaded_file = req.files.get("file")
        if not uploaded_file:
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "No file was uploaded. Use multipart/form-data with 'file' field."
                    }
                ),
                status_code=400,
                mimetype="application/json",
            )

        original_filename = uploaded_file.filename

        # Determine the MIME type (and thereby validate if it's jpg/jpeg/png)
        guessed_type, _ = mimetypes.guess_type(uploaded_file.filename)

        # Fallback to what Postman/file reports if guess_type is None:
        content_type = (
            guessed_type or uploaded_file.content_type or "application/octet-stream"
        )

        # Restrict to only 'image/jpeg' or 'image/png'
        valid_mimetypes = {"image/jpeg", "image/png"}
        if content_type not in valid_mimetypes:
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": (
                            f"Unsupported file type '{content_type}'. "
                            "Only .jpg/.jpeg/.png files are allowed."
                        )
                    }
                ),
                status_code=400,
                mimetype="application/json",
            )

        # Construct a blob name with a timestamp prefix
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        blob_name = f"news_images/{timestamp_str}_{original_filename}"

        # Read file bytes
        file_bytes = uploaded_file.read()

        # Connect to Azure Blob Storage using the connection string
        connection_str = os.getenv("MY_STORAGE_CONNECTION_STRING")
        if not connection_str:
            return func.HttpResponse(
                json.dumps(
                    {
                        "error": "Missing MY_STORAGE_CONNECTION_STRING in environment variables."
                    }
                ),
                status_code=500,
                mimetype="application/json",
            )

        blob_service_client = BlobServiceClient.from_connection_string(connection_str)
        container_name = "asm"  # your container
        container_client = blob_service_client.get_container_client(container_name)

        # Create container if it doesn't exist (optional)
        try:
            container_client.create_container()
        except Exception:
            pass  # container likely exists

        # Upload to Azure Blob Storage
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file_bytes, overwrite=True, content_settings=ContentSettings(content_type=content_type))

        # 6. Construct the publicly accessible blob URL
        #    Since the container is set to public access level = Blob or Container,
        #    this URL can be accessed without any token.
        public_url = blob_client.url

        # Return JSON with the public URL
        response_body = {
            "imageUrl": public_url,
            "fileName": original_filename,
            "contentType": content_type,
            "message": "Uploaded successfully!",
        }

        return func.HttpResponse(
            body=json.dumps(response_body),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as ex:
        logging.exception("Error uploading image.")
        return func.HttpResponse(
            json.dumps({"error": str(ex)}),
            status_code=500,
            mimetype="application/json",
        )
