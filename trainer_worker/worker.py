import redis
import json
import os
import tempfile
import time
from datetime import datetime
from datasets import load_from_disk
from minio import Minio
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)
from logger_setup import setup_logger

r = redis.Redis(host="redis", port=6379, decode_responses=True)
minio_client = Minio(
    "minio:9000",
    access_key=os.environ["MINIO_ROOT_USER"],
    secret_key=os.environ["MINIO_ROOT_PASSWORD"],
    secure=False,
)

for bucket in ["datasets", "models"]:
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)


def download_from_minio(dataset_key: str) -> str:
    """ดึง dataset จาก MinIO bucket 'datasets' มาไว้ที่ local"""
    local_dir = tempfile.mkdtemp()
    local_path = os.path.join(local_dir, "dataset")
    objects = minio_client.list_objects("datasets", prefix=dataset_key, recursive=True)

    for obj in objects:
        relative_path = os.path.relpath(obj.object_name, dataset_key)
        target = os.path.join(local_path, relative_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        minio_client.fget_object("datasets", obj.object_name, target)

    return local_path


def train_model(dataset_path: str, config: dict):
    """โหลด base model ตาม config ก่อนเริ่มเทรน"""
    model_name = config.get("model_name", "bert-base-uncased")
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return model


def upload_to_minio(model, job_id: str) -> str:
    """เซฟโมเดลลง local แล้วอัปโหลดขึ้น MinIO bucket 'models' แบบมี versioning ตาม job_id"""
    local_dir = tempfile.mkdtemp(prefix=f"model_{job_id}_")
    model.save_pretrained(local_dir)

    model_key_prefix = f"models/{job_id}/"
    for filename in os.listdir(local_dir):
        local_file = os.path.join(local_dir, filename)
        if os.path.isfile(local_file):
            minio_client.fput_object("models", model_key_prefix + filename, local_file)

    return model_key_prefix


class EpochLoggerCallback(TrainerCallback):
    def __init__(self, logger):
        self.logger = logger

    def on_log(self, args, state, control, logs=None, **kwargs):
        if not logs or "eval_f1" not in logs:
            return

        epoch = state.epoch or 0
        self.logger.info(
            f"Epoch {epoch:.0f} | "
            f"loss: {logs.get('eval_loss', 0):.4f} | "
            f"f1: {logs['eval_f1']:.4f} | "
            f"accuracy: {logs.get('eval_accuracy', 0):.4f}"
        )


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions, average="weighted"),
    }


def run_training(job):
    logger, log_path = setup_logger(job["job_id"])

    try:
        logger.info(f"เริ่ม training job {job['job_id']}")
        logger.info(f"Dataset: {job['dataset_name']}, Model: {job['model_name']}")

        logger.info("กำลังโหลด dataset จาก MinIO...")
        dataset_path = download_from_minio(job["dataset_key"])
        dataset = load_from_disk(dataset_path)
        logger.info(f"โหลด dataset สำเร็จ: {dataset_path}")

        model_name = job["model_name"]
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        def tokenize_fn(batch):
            return tokenizer(batch["text"], padding="max_length", truncation=True)

        tokenized = dataset.map(tokenize_fn, batched=True)
        training_args = TrainingArguments(
            output_dir=f"/tmp/train_{job['job_id']}",
            num_train_epochs=int(job["epochs"]),
            per_device_train_batch_size=int(job.get("batch_size", 8)),
            evaluation_strategy="epoch",
            logging_strategy="epoch",
            save_strategy="no",
            report_to="none",
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized["train"],
            eval_dataset=tokenized["test"],
            compute_metrics=compute_metrics,
            callbacks=[EpochLoggerCallback(logger)],
        )

        logger.info("เริ่มเทรนโมเดล...")
        trainer.train()

        logger.info("เทรนเสร็จสิ้น กำลังอัปโหลดโมเดลไปที่ MinIO...")
        model_path = upload_to_minio(model, job["job_id"])
        logger.info(f"อัปโหลดโมเดลสำเร็จ: {model_path}")
    except Exception:
        logger.exception(f"training job ล้มเหลว: {job['job_id']}")
        raise

    return log_path

while True:
    job_data = r.blpop("train_queue", timeout=5)  # blocking pop รอ job ใหม่
    if job_data:
        _, job_json = job_data
        job = json.loads(job_json)
        scheduled_time = job["scheduled_time"]
        if isinstance(scheduled_time, str):
            scheduled_time = datetime.fromisoformat(
                scheduled_time.replace("Z", "+00:00")
            ).timestamp()

        if time.time() >= scheduled_time:
            run_training(job)
        else:
            r.rpush("train_queue", job_json)
            time.sleep(1)
    time.sleep(1)