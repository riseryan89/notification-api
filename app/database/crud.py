from sqlalchemy.orm import Session

from app.database.conn import Base


async def create(session: Session, obj: Base, auto_commit=False, **kwargs):
    """
    테이블 데이터 적재 전용 함수
    :param session:
    :param obj: 테이블 모델 인스턴스, ex) User()
    :param auto_commit: 자동 커밋 여부
    :param kwargs: 적재 할 데이터
    :return:
    """
    for col in obj.all_columns():
        col_name = col.name
        if col_name in kwargs:
            setattr(obj, col_name, kwargs.get(col_name))
    session.add(obj)
    session.flush()
    if auto_commit:
        session.commit()
    return obj
