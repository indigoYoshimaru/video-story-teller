
def get_post(db_client, post_id):
    return db_client.storry_teller.posts.find_one(dict(post_id=post_id))
