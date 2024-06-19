def update_post(db_client, post: dict):
    try:
        upserted_id = db_client.story_teller.posts.update_one(
            {"_id": post.get("_id")},
            {"$set": post},
        ).upserted_id
    except Exception as e:
        raise e
    else:
        return upserted_id
