def insert_post_one(db_client, post):
    return db_client.story_teller.posts.insert_one(post).inserted_id

def insert_post_many(db_client, posts): 
    return db_client.story_teller.posts.insert_many(posts).inserted_ids 