import argparse
import os
import tempfile

from datasets import load_dataset
from minio import Minio


def upload_dataset(dataset_name: str, dataset_key: str, config: str | None = None) -> str:
    client = Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "wlul0abwlu123"),
        secure=False,
    )

    if not client.bucket_exists("datasets"):
        client.make_bucket("datasets")

    dataset = load_dataset(dataset_name, config) if config else load_dataset(dataset_name)
    with tempfile.TemporaryDirectory() as temporary_dir:
        local_path = os.path.join(temporary_dir, "dataset")
        dataset.save_to_disk(local_path)

        for root, _, files in os.walk(local_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, local_path).replace("\\", "/")
                client.fput_object("datasets", f"{dataset_key}/{relative_path}", file_path)

    return f"datasets/{dataset_key}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a Hugging Face dataset into MinIO.")
    parser.add_argument("dataset_name", help="Hugging Face dataset name, e.g. conll2003")
    parser.add_argument("--dataset-key", help="MinIO prefix", default=None)
    parser.add_argument("--config", default=None, help="Optional Hugging Face dataset config")
    arguments = parser.parse_args()
    key = arguments.dataset_key or arguments.dataset_name
    print(upload_dataset(arguments.dataset_name, key, arguments.config))