# -*- coding: utf-8 -*-
from . import utils

def get_hmm():
    """Get a thought."""
    return 'hmmm...'


def hmm():
    """Contemplation..."""
    if utils.get_answer():
        print(get_hmm())

class Job:
    pass

class JobManager:
    pass

class JobServer:
    pass