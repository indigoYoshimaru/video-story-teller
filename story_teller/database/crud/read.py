def get_post(db_client, post_id):
    return db_client.story_teller.posts.find_one(dict(post_id=post_id))


def get_raw_posts(db_client):
    from story_teller.database.enum import StatusEnum

    return db_client.story_teller.posts.find(dict(status=StatusEnum.raw.value))


def get_translated_posts(db_client):
    from story_teller.database.enum import StatusEnum

    return db_client.story_teller.posts.find(dict(status=StatusEnum.translated.value))


def get_edited_posts(db_client):
    from story_teller.database.enum import StatusEnum

    return db_client.story_teller.posts.find(dict(status=StatusEnum.edited.value))


def get_generated_posts(db_client):
    from story_teller.database.enum import StatusEnum

    return db_client.story_teller.posts.find(dict(status=StatusEnum.generated.value))


def get_done_posts(db_client):
    from story_teller.database.enum import StatusEnum

    return db_client.story_teller.posts.find(dict(status=StatusEnum.done.value))
