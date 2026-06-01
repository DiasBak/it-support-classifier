import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import (
    TfidfVectorizer
)
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix

)


def train():

    print('Загрузка датасета...')
    df = pd.read_csv(
        'data/status_karaganda_dataset.csv'
    )

    df['category'] = df['category'].replace(
        'Системное администрирование',
        'Сетевые технологии'
    )

    df = df.dropna()
    df = df.drop_duplicates()
    df = df[
        (df['text'].str.strip() != '')
        &
        (df['category'].str.strip() != '')
    ]
    print('\n=================================')
    print('Количество записей:', len(df))
    print('=================================')
    print('\nКатегории:\n')
    print(df['category'].value_counts())


    X = df['text']
    y = df['category']

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = Pipeline([
        (
            'tfidf',
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 3),
                min_df=1,
                max_df=0.9,
                max_features=5000,
                sublinear_tf=True,
                stop_words=[

                    'и',
                    'в',
                    'на',
                    'с',
                    'по',
                    'не',
                    'после',
                    'для',
                    'при',
                    'что',
                    'как',
                    'из'
                ]
            )
        ),
        (
            'clf',
            LinearSVC(
                class_weight='balanced'
            )
        )
    ])

    print('\nОбучение модели...')
    model.fit(
        X_train,
        y_train

    )
    predictions = model.predict(
        X_test
    )
    accuracy = accuracy_score(
        y_test,
        predictions
    )
    print('\n=================================')
    print(
        'Accuracy:',
        round(
            accuracy * 100,
            2
        ),
        '%'
    )
    print('=================================')
    print('\nClassification Report:\n')
    print(
        classification_report(
            y_test,
            predictions
        )
    )
    print('\nConfusion Matrix:\n')
    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    joblib.dump(
        model,
        'ml/model.pkl'
    )

    print('\n=================================')
    print('Модель успешно сохранена!')
    print('Файл: ml/model.pkl')
    print('=================================')

if __name__ == '__main__':

    train()