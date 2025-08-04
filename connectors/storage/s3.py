import os
import io
import pandas as pd

from openetl_utils.enums import AuthType
from openetl_utils.main_storage_class import Storage


class Connector(Storage):
    def __init__(self):
        self.required_libs = ["boto3"]
        self.logo = "https://cdn.dataomnisolutions.com/main/connector_logos/aws-s3.svg"
        self.engine = "Amazon S3"
        self.client = None
        self.bucket = None
        self.authentication_details = {
            AuthType.BASIC: {
                "aws_access_key_id": "",
                "aws_secret_access_key": "",
                "bucket_name": "",
                "region_name": ""
            }
        }
        super().__init__()

    def create_engine(self, **auth_params):
        return self.connect(**auth_params)

    def connect(self, **auth_params):
        import boto3
        self.authentication_details[AuthType.BASIC].update(auth_params)
        creds = self.authentication_details[AuthType.BASIC]
        self.bucket = creds["bucket_name"]
        self.client = boto3.client(
            "s3",
            aws_access_key_id=creds["aws_access_key_id"],
            aws_secret_access_key=creds["aws_secret_access_key"],
            region_name=creds["region_name"]
        )
        return self

    def test_connection(self):
        try:
            self.client.list_objects_v2(Bucket=self.bucket, MaxKeys=1)
            return True
        except Exception:
            return False

    def list_files(self, prefix=""):
        paginator = self.client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
        all_keys = []
        for page in page_iterator:
            contents = page.get("Contents", [])
            for obj in contents:
                key = obj["Key"]
                if not key.endswith("/"):
                    all_keys.append(key)
        return all_keys

    def read_file(self, file_path, **kwargs):
        ext = os.path.splitext(file_path)[1].lower()
        obj = self.client.get_object(Bucket=self.bucket, Key=file_path)
        content = obj["Body"].read()

        if ext == ".csv":
            return pd.read_csv(io.BytesIO(content))
        elif ext == ".json":
            return pd.read_json(io.BytesIO(content))
        elif ext == ".parquet":
            import pyarrow.parquet as pq
            import pyarrow as pa
            table = pq.read_table(io.BytesIO(content))
            return table.to_pandas()
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def write_file(self, file_path, data, **kwargs):
        ext = os.path.splitext(file_path)[1].lower()
        buffer = io.BytesIO()

        if isinstance(data, pd.DataFrame):
            if ext == ".csv":
                data.to_csv(buffer, index=False)
            elif ext == ".json":
                data.to_json(buffer, orient="records")
            elif ext == ".parquet":
                import pyarrow as pa
                import pyarrow.parquet as pq
                table = pa.Table.from_pandas(data)
                pq.write_table(table, buffer)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
        else:
            raise ValueError("Data must be a pandas DataFrame")

        buffer.seek(0)
        self.client.put_object(Bucket=self.bucket, Key=file_path, Body=buffer)
        return True

    def delete_file(self, file_path, **kwargs):
        self.client.delete_object(Bucket=self.bucket, Key=file_path)
        return True

    def validate_folder_structure(self, folder_path, **kwargs):
        files = self.list_files(prefix=folder_path)
        if not files:
            return False
        extensions = set(os.path.splitext(f)[1] for f in files if not f.endswith('/'))
        return len(extensions) == 1

    def get_table_schema(self, folder_path, sample_size=10, **kwargs):
        if not self.validate_folder_structure(folder_path):
            return {"error": "Invalid folder structure"}

        files = self.list_files(prefix=folder_path)[:sample_size]
        frames = []
        for f in files:
            try:
                df = self.read_file(f)
                if isinstance(df, pd.DataFrame):
                    frames.append(df)
            except Exception:
                continue

        if not frames:
            return {"error": "No readable files found"}

        df = pd.concat(frames, ignore_index=True)
        return {
            "columns": [{"name": col, "dtype": str(dtype)} for col, dtype in df.dtypes.items()]
        }

    def get_metadata(self, *args, **kwargs):
        self.connect(**kwargs)
        files = self.list_files()
        folders = {os.path.dirname(f) for f in files if "/" in f}
        valid_tables = [f for f in folders if self.validate_folder_structure(f)]
        return {
            "schema": [self.bucket],
            "tables": valid_tables
        }

    def read_table(self, table_name, schema_name="public", page_size=10000):
        return self.read_file(table_name)

    def write_data(self, data, table_name, if_exists='append', schema="public"):
        return self.write_file(table_name, data)

    def execute_query(self, query):
        raise NotImplementedError("Not applicable for storage connectors.")

    def close_session(self):
        return True

    def __exit__(self, exc_type, exc_value, traceback):
        return self.close_session()

    def get_table_file_type(self, folder_path):
        files = self.list_files(prefix=folder_path)
        extensions = [os.path.splitext(f)[1] for f in files if not f.endswith('/')]
        extensions = list(set(extensions))
        return extensions[0] if len(extensions) == 1 else None

    def get_file_url(self, key_path=""):
        key_path = key_path.lstrip("/")
        return f"s3a://{self.bucket}/{key_path}"

    def get_hadoop_config(self):
        creds = self.authentication_details[AuthType.BASIC]
        return {
            "fs.s3a.access.key": creds["aws_access_key_id"],
            "fs.s3a.secret.key": creds["aws_secret_access_key"],
            "fs.s3a.endpoint": f"s3.{creds['region_name']}.amazonaws.com",
            "fs.s3a.bucket": creds["bucket_name"],
            "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "fs.s3a.path.style.access": "true",
            'spark.hadoop.fs.s3a.aws.credentials.provider': 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider'
        }

    def get_spark_config(self):
        return self.get_hadoop_config()

    def get_spark_workflow(self, folder_path=""):
        return {
            "hadoop_config": self.get_hadoop_config(),
            "read_path": self.get_file_url(folder_path),
            "format": self.get_table_file_type(folder_path)
        }
