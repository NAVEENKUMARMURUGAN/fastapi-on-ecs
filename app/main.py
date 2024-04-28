from fastapi import FastAPI, UploadFile, File, HTTPException
import boto3
import uuid
from botocore.exceptions import ClientError

app = FastAPI()

# Create S3 client
s3_client = boto3.client('s3')

@app.post("/upload-file/{bucket_name}/{file_name}")
async def upload_file(bucket_name: str, file_name: str, file: UploadFile = File(...)):
    try:
        # Check file size
        max_file_size = 1_000_000_000  # 1GB in bytes
        if file.file.seek(0, 2) > max_file_size:
            raise HTTPException(status_code=413, detail="File size exceeds the limit of 1GB")

        # Get filename and create unique key
        object_key = f"{file_name}-{uuid.uuid4()}"

        file.file.seek(0)
        
        # Stream upload file to S3
        with file.file as f:
            s3_client.upload_fileobj(f, bucket_name, object_key)

        return {"message": f"File {file_name} uploaded successfully to bucket {bucket_name}!"}
    except ClientError as e:
        raise HTTPException(500, detail=f"S3 upload failed: {e}")
