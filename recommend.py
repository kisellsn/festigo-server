from firestore import db

def recommend_for_user(user_id):
    user_doc = db.collection("users").document(user_id).get()
    user_prefs = user_doc.to_dict()

    all_events = [doc.to_dict() for doc in db.collection("events").stream()]

    preferred_genres = set(user_prefs.get("genres", []))
    preferred_categories = set(user_prefs.get("categories", []))

    def score(event):
        return (
            len(set(event.get("genres", [])) & preferred_genres) * 2 +
            len(set(event.get("main_categories", [])) & preferred_categories)
        )

    recommended = sorted(all_events, key=score, reverse=True)
    return recommended
