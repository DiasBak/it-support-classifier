import json
import os
import re
import pandas as pd

from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'complaints.json')
EXTRA_PATH = os.path.join(BASE_DIR, 'data', 'my_tickets.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'ml', 'bert_model')


def clean_text(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_category(cat):
    c = cat.lower()
    if 'credit card' in c:
        return 'Financial issue'
    if 'bank account' in c or 'checking' in c or 'savings' in c:
        return 'Bank account'
    if 'mortgage' in c:
        return 'Mortgage'
    if 'debt' in c:
        return 'Debt'
    if 'loan' in c:
        return 'Loan'
    return 'Other'


def load_data():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts, cats = [], []
    for item in data:
        src = item.get('_source', {})
        t = src.get('complaint_what_happened', '')
        c = src.get('product', '')
        if t and t.strip():
            texts.append(clean_text(t))
            cats.append(normalize_category(c))

    df = pd.DataFrame({'text': texts, 'category': cats})

    # убрать редкие
    counts = df['category'].value_counts()
    valid = counts[counts >= 100].index
    df = df[df['category'].isin(valid)]

    # добавить свои примеры (если есть)
    if os.path.exists(EXTRA_PATH):
        extra = pd.read_csv(EXTRA_PATH)
        extra.columns = ['text', 'category']
        df = pd.concat([df, extra], ignore_index=True)

    return df


def main():
    df = load_data()

    labels = sorted(df['category'].unique())
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}

    df['label'] = df['category'].map(label2id)

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

    train_ds = Dataset.from_pandas(train_df[['text', 'label']])
    test_ds = Dataset.from_pandas(test_df[['text', 'label']])

    model_name = "distilbert-base-multilingual-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize(batch):
        return tokenizer(batch['text'], truncation=True, padding='max_length', max_length=256)

    train_ds = train_ds.map(tokenize, batched=True)
    test_ds = test_ds.map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id
    )

    args = TrainingArguments(
        output_dir=os.path.join(BASE_DIR, 'ml', 'bert_out'),
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=2,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        tokenizer=tokenizer
    )

    trainer.train()

    os.makedirs(MODEL_DIR, exist_ok=True)
    trainer.save_model(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)

    print("BERT модель сохранена в:", MODEL_DIR)


if __name__ == "__main__":
    main()