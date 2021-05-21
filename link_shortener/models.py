from link_shortener import db, Base, session


class Main(Base):
    """Основная таблица, содержит два поля: ``id`` и ``link``"""

    __tablename__ = "main"
    __bind_key__ = "engine"

    id = db.Column(
        db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    link = db.Column(
        db.String,
        nullable=False,
        unique=True,
    )

    def __repr__(self):
        return {self.link}

    @classmethod
    def get_by_link(cls, link):
        """Получение ответа по ссылке(все ссылки уникальные)"""

        try:
            link_record = cls.query.filter(cls.link == link).first()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return link_record

    def save(self):
        """Запись ссылки в базу"""

        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def delete(self):
        """Удаление из базы"""

        try:
            session.delete(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def update(self, new_link):
        """Обновление записей - изменение ссылки при сохранении короткого имени"""

        try:
            link_exists = Main.get_by_link(new_link)
            if not link_exists:
                setattr(self, "link", new_link)
                session.commit()
        except Exception:
            session.rollback()
            raise
