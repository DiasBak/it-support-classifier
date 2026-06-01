import joblib
import numpy as np



model = joblib.load(
    'ml/model.pkl'
)



def predict_category(text):

    prediction = model.predict(
        [text]
    )[0]


    scores = model.decision_function(
        [text]
    )[0]

    confidence = round(
        abs(scores.max()) * 10
    )

    if confidence > 100:

        confidence = 100


    classes = model.classes_

    sorted_indexes = np.argsort(
        scores
    )[::-1]

    top_predictions = []

    for index in sorted_indexes[:3]:

        top_predictions.append({

            'category': classes[index],

            'score': round(
                abs(scores[index]) * 10
            )

        })

    return {

        'category': prediction,

        'confidence': confidence,

        'top_predictions': top_predictions

    }