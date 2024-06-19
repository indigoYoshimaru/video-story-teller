def update_post_by_id(db_client, post_id, post):
    return db_client.story_teller.posts.update(dict(post_id = post_id), post).upserted_id