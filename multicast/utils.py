import random
import string


def create_random_file_path():
    return "".join([random.SystemRandom().choice(string.ascii_letters + string.digits) for i in range(20)])
