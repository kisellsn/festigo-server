from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def score_event_by_components(aggregated_profile, event_components, field_names):
    """
    cosine similarity calculation

    :param aggregated_profile:
    :param event_components:
    :return: avg score
    """
    scores = []
    for field in field_names:
        user_vec = np.array(aggregated_profile[field]).reshape(1, -1)
        event_vec = np.array(event_components.get(field, [])).reshape(1, -1)
        if user_vec.shape == event_vec.shape and user_vec.shape[1] > 0:
            sim = cosine_similarity(user_vec, event_vec)[0][0]
            scores.append(sim)
    return np.mean(scores) if scores else 0