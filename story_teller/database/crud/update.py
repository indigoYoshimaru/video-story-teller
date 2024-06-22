def update_post(db_client, post: dict):
    try:
        upserted_id = db_client.story_teller.posts.update_one(
            {"post_id": post.get("post_id")},
            {"$set": post},
        ).upserted_id
    except Exception as e:
        raise e
    else:
        return upserted_id
