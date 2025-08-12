import asyncio
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import joinedload, Session
from pydantic import EmailStr

from src import models, schemas
from src.database import get_db, SessionLocal  
from src.utils import upload_image_to_cloudinary, hash_string
from src.llm_classifier import classify_image_gemini, classify_text_gemini
from src.email_alerts import send_alert_email
from src.email_template import moderation_email_template 
from src.api.errors import ApiError, ApiResponse
from src.logger import logger 

router = APIRouter()

async def db_add_commit_refresh(db: Session, instance):
    db.add(instance)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, instance)
    return instance

async def db_commit(db: Session):
    await asyncio.to_thread(db.commit)

@router.post("/text", response_model=ApiResponse)
async def moderate_text(payload: schemas.TextModerationRequest, db: Session = Depends(get_db)):
    if not payload.text.strip():
        logger.warning("Received empty text content for moderation")
        raise ApiError(status_code=400, message="Text content cannot be empty", errors=["Empty text is not allowed"])
    
    req = models.ModerationRequest(
        email=payload.email,
        content_hash=hash_string(payload.text),
        content_type="text",
        status="pending"
    )
    await db_add_commit_refresh(db, req)
    logger.info(f"Created moderation request with ID {req.id} for text content")

    try:
        result_data = await asyncio.to_thread(classify_text_gemini, payload.text)
        logger.info(f"Text classification successful for request ID {req.id}")
    except Exception as e:
        logger.error(f"Text classification failed for request ID {req.id}: {e}")
        raise ApiError(500, f"Text classification failed: {str(e)}")

    result = models.ModerationResult(
        request_id=req.id,
        classification=result_data.classification,
        confidence=result_data.confidence,
        reasoning=result_data.reason,
        llm_response=result_data.description
    )
    db.add(result)
    req.status = "completed"
    await db_commit(db)
    logger.info(f"Moderation result saved and request {req.id} marked as completed")

    req_with_results = await asyncio.to_thread(
        lambda: db.query(models.ModerationRequest)
                .options(joinedload(models.ModerationRequest.results))
                .filter(models.ModerationRequest.id == req.id)
                .first()
    )

    if not req_with_results.results:
        logger.error(f"No moderation results found for request ID {req.id}")
        raise ApiError(status_code=404, message="No moderation results found", errors=["No results for the given request"])

    response_data = schemas.ModerationRequestResponse.model_validate(req_with_results)
    return ApiResponse(
        status_code=200,
        success=True,
        message="Success",
        data=response_data
    )

async def process_image_moderation_background(request_id: int, file_bytes: bytes):
    try:
        cloudinary_url = await upload_image_to_cloudinary(file_bytes)
        logger.info(f"Uploaded image to Cloudinary for request ID {request_id}")

        def blocking_work():
            db = SessionLocal()
            try:
                result_data = classify_image_gemini(cloudinary_url)
                logger.info(f"Image classified successfully for request ID {request_id}")

                req = db.query(models.ModerationRequest).get(request_id)
                if req is None:
                    logger.error(f"Moderation request with ID {request_id} not found during background processing")
                    raise ApiError(404, f"Moderation request with id {request_id} not found")

                req.content_url = cloudinary_url
                req.status = "completed"

                result = models.ModerationResult(
                    request_id=request_id,
                    classification=result_data.classification,
                    confidence=result_data.confidence,
                    reasoning=result_data.reason,
                    llm_response=result_data.description,
                )
                db.add(result)
                db.commit()
                logger.info(f"Moderation result saved and request {request_id} marked as completed in background")

                # Send email notification after successful commit
                try:
                    email_html = moderation_email_template(
                        request_id=request_id,
                        classification=result_data.classification,
                        confidence=result_data.confidence,
                        reasoning=result_data.reason,
                    )
                    send_alert_email(
                        subject="Your content moderation result is ready",
                        html_content=email_html,
                        to_email=req.email
                    )
                    logger.info(f"Moderation result email sent for request ID {request_id} to {req.email}")
                except Exception as e:
                    logger.error(f"Failed to send moderation email for request ID {request_id}: {e}")

            except Exception as e:
                logger.error(f"Error during blocking image moderation work for request ID {request_id}: {e}")
                raise
            finally:
                db.close()

        await asyncio.to_thread(blocking_work)

    except Exception as e:
        logger.error(f"Error in image moderation background task for request ID {request_id}: {e}")


@router.post("/image", response_model=ApiResponse)
async def moderate_image(
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    file_bytes = await file.read()

    if not file_bytes:
        logger.warning(f"No image file provided for moderation by user {email}")
        raise ApiError(400, "No image file provided", errors=["Empty file"])

    req = models.ModerationRequest(
        email=email,
        content_type="image",
        status="pending"
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    logger.info(f"Created moderation request with ID {req.id} for image content")

    background_tasks.add_task(process_image_moderation_background, req.id, file_bytes)
    logger.info(f"Background task started for image moderation request ID {req.id}")

    return ApiResponse(
        status_code=200,
        success=True,
        message="Moderation processing started",
        data={"request_id": req.id}
    )
