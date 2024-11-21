import uvicorn
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Tariff
from app.schemas import TariffSchema, InsuranceRequest, InsuranceResponse
from app.upload_tariffs import upload_tariffs
from app.exceptions import TariffNotFoundError, InvalidJSONError, DatabaseError
from app.crud import get_tariff_by_type_and_date
from datetime import datetime
import logging

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Kafka producer
kafka_producer = KafkaProducer(
  bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS")],
  value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


def log_to_kafka(event_type: str, details: dict):
  """Отправляет сообщение в Kafka."""
  message = {
    'timestamp': datetime.now().isoformat(),
    'event_type': event_type,
    'details': details
  }
  try:
    kafka_producer.send(os.getenv("KAFKA_TOPIC"), value=message)
    logger.info(f"Отправлено сообщение в Kafka: {message}")
  except Exception as e:
    logger.error(f"Ошибка при отправке сообщения в Kafka: {e}")


# Функция для обработки ошибок и логирования в Kafka
def handle_exception_and_log(e, event_type, details):
 log_to_kafka(event_type, details)
 raise HTTPException(status_code=500, detail=f"Ошибка: {e}")


@app.post("/tariffs/", response_model=None, status_code=status.HTTP_201_CREATED)
async def upload_tariffs_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db)):
 try:
  result = upload_tariffs(file, db)
  log_to_kafka("tariffs_uploaded", {'result': result})
  return result
 except InvalidJSONError as e:
  handle_exception_and_log(e, "tariffs_upload_error", {'error': str(e)})
 except DatabaseError as e:
  handle_exception_and_log(e, "tariffs_upload_database_error", {'error': str(e)})


@app.post("/insurance/", response_model=InsuranceResponse)
async def calculate_insurance(request: InsuranceRequest, db: Session = Depends(get_db)):
 try:
  tariff = get_tariff_by_type_and_date(db, request.cargo_type, request.date)
  if tariff is None:
   raise TariffNotFoundError
  insurance_cost = request.declared_value * tariff.rate
  log_to_kafka("insurance_calculated", {'cargo_type': request.cargo_type, 'declared_value': request.declared_value, 'date': request.date, 'insurance_cost': insurance_cost})
  return {"insurance_cost": insurance_cost}
 except TariffNotFoundError:
  handle_exception_and_log(e, "insurance_calculation_error", {'error': "Тариф не найден"})
 except Exception as e:
  handle_exception_and_log(e, "insurance_calculation_error", {'error': str(e)})


@app.on_event("shutdown")
async def shutdown_event():
  kafka_producer.flush()
  kafka_producer.close()


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)