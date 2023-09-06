from contextlib import contextmanager

from db import News, session


@contextmanager
def session_scope():
    s = session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
