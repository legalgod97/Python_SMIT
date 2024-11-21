from sqlalchemy.orm import Session
from app.models import Tariff
from datetime import date
from sqlalchemy.exc import SQLAlchemyError


def get_tariff_by_type_and_date(db: Session, cargo_type: str, date: date):
  return db.query(Tariff).filter(Tariff.cargo_type == cargo_type, Tariff.date == date).first()


def create_tariff(db: Session, cargo_type: str, date: date, price: float):
  """Creates a new tariff entry."""
  try:
    new_tariff = Tariff(cargo_type=cargo_type, date=date, price=price)
    db.add(new_tariff)
    db.commit()
    db.refresh(new_tariff) # Get the generated ID
    return new_tariff
  except SQLAlchemyError as e:
    db.rollback()
    print(f"Error creating tariff: {e}")
    return None


def update_tariff(db: Session, cargo_type: str, date: date, price: float):
  """Updates an existing tariff entry."""
  try:
    tariff = get_tariff_by_type_and_date(db, cargo_type, date)
    if tariff:
      tariff.price = price
      db.commit()
      return tariff
    else:
      print(f"Tariff for {cargo_type} on {date} not found.")
      return None
  except SQLAlchemyError as e:
    db.rollback()
    print(f"Error updating tariff: {e}")
    return None


def delete_tariff(db: Session, cargo_type: str, date: date):
  """Deletes a tariff entry."""
  try:
    tariff = get_tariff_by_type_and_date(db, cargo_type, date)
    if tariff:
      db.delete(tariff)
      db.commit()
      return True
    else:
      print(f"Tariff for {cargo_type} on {date} not found.")
      return False
  except SQLAlchemyError as e:
    db.rollback()
    print(f"Error deleting tariff: {e}")
    return False