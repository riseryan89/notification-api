from typing import List
from sqlalchemy.orm import Session


class SessionControl:
    def __init__(self):
        self._session = None
        self._schema = None

    def initialize(self, sess, schema):
        if not sess or not schema:
            raise Exception("No Session")
        self._session = sess
        self._schema = schema

    @property
    def get_session(self):
        return self._session


session = SessionControl()


class SQLAlchemist:
    def __init__(self):
        self._q = None

    def _all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    @classmethod
    def create(cls, sess: Session = None, auto_commit: bool = False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param sess:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj._all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        if not sess:
            sess = next(session.get_session())
            sess.add(obj)
            sess.commit()
        else:
            sess.add(obj)
            sess.flush()
            if auto_commit:
                sess.commit()
        return obj

    @classmethod
    def cls_attr(cls, col_name=None):
        if col_name:
            col = getattr(cls, col_name)
            return col
        else:
            return cls

    @classmethod
    def create_many(cls, rows: List, sess: Session = None, auto_commit: bool = False):
        """
        테이블 데이터 적재 전용 함수
        :param rows:
        :param sess:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        sess.bulk_save_objects(rows)
        sess.flush()
        if auto_commit:
            sess.commit()
        return len(rows)

    @classmethod
    def get(cls, **kwargs):
        """
        Simply get a Row
        :param kwargs:
        :return:
        """
        sess = next(session.get_session())
        query = sess.query(cls)
        for key, val in kwargs.items():
            col = getattr(cls, key)
            query = query.filter(col == val)

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.")
        return query.first()

    @classmethod
    def filter(cls, **kwargs):
        """
        Simply get a Row
        :param by:
        :param kwargs:
        :return:
        """
        cond = []
        for key, val in kwargs.items():
            key = key.split("__")
            if len(key) > 2:
                raise Exception("No 2 more dunders")
            col = getattr(cls, key[0])
            if len(key) == 1: cond.append((col == val))
            elif len(key) == 2 and key[1] == 'gt': cond.append((col > val))
            elif len(key) == 2 and key[1] == 'gte': cond.append((col >= val))
            elif len(key) == 2 and key[1] == 'lt': cond.append((col < val))
            elif len(key) == 2 and key[1] == 'lte': cond.append((col <= val))
            elif len(key) == 2 and key[1] == 'in': cond.append((col.in_(val)))

        sess = next(session.get_session())
        query = sess.query(cls)

        query = query.filter(*cond)
        obj = cls()
        obj._q = query
        return obj

    def update(self, sess: Session = None, auto_commit: bool = False, **kwargs):
        cls = self.cls_attr()
        if sess:
            query = sess.query(cls)
        else:
            sess = next(session.get_session())
            query = sess.query(cls)
        return query.update(**kwargs)

    def first(self):
        return self._q.first()

    def order_by(self, *args: str):
        for a in args:
            if a.startswith("-"):
                col_name = a[1:]
                is_asc = False
            else:
                col_name = a
                is_asc = True
            col = self.cls_attr(col_name)
            self._q = self._q.order_by(col.asc()) if is_asc else self._q.order_by(col.desc())
        return self

    def dict(self, *args: str):
        q_dict = {}
        for c in self.__table__.columns:
            if c.name in args:
                q_dict[c.name] = getattr(self, c.name)

        return q_dict

    def all(self):
        return self._q.all()
