import json
from sqlalchemy.orm import Session
from app.models import Tariff
from fastapi import UploadFile
from app.exceptions import InvalidJSONError, DatabaseError
from datetime import date


def upload_tariffs(file: UploadFile, db: Session):
  try:
    contents = file.file.read()
    tariffs_data = json.loads(contents)

    for day, items in tariffs_data.items():
      day_date = date.fromisoformat(day)
      for item in items:
        db_tariff = Tariff(date=day_date, cargo_type=item["cargo_type"], rate=item["rate"])
        db.add(db_tariff)
    db.commit()
    return {"message": "Тарифы успешно загружены"}

  except json.JSONDecodeError:
    raise InvalidJSONError("Неверный формат JSON")
  except Exception as e:
    db.rollback()
    raise DatabaseError(f"Ошибка загрузки тарифов: {e}")