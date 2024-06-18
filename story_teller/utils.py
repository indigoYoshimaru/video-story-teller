from typing import Text


def read_env(env_file: Text):
    from dotenv import dotenv_values
    env_dict = dotenv_values(env_file)
    return env_dict
