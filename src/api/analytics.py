import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from src import models, schemas
from src.database import get_db
from src.email_alerts import send_alert_email
from src.email_template import analytics_email_html
from src.api.errors import ApiError, ApiResponse

from src.logger import logger  

router = APIRouter()

from datetime import datetime, timezone

def insert_notification(db: Session, request_id: int):
    try:
        notif = models.NotificationLog(
            request_id=request_id,
            channel="email",
            status="sent",
            sent_at=datetime.now(timezone.utc)  # timezone-aware UTC datetime
        )
        db.add(notif)
        db.commit()
        logger.info(f"Inserted notification log for request_id={request_id}")
    except Exception as err:
        logger.error(f"Failed to insert notification log: {err}")

@router.get("/summary", response_model=ApiResponse)
async def analytics_summary(user: str, db: Session = Depends(get_db)):
    try:
        # Total moderation requests by user
        total_requests = await asyncio.to_thread(
            lambda: db.query(models.ModerationRequest)
                       .filter(models.ModerationRequest.email == user)
                       .count()
        )

        # Counts by classification for text content
        text_counts = await asyncio.to_thread(
            lambda: db.query(
                        models.ModerationResult.classification,
                        func.count(models.ModerationResult.classification)
                    )
                    .join(models.ModerationRequest)
                    .filter(
                        models.ModerationRequest.email == user,
                        models.ModerationRequest.content_type == "text"
                    )
                    .group_by(models.ModerationResult.classification)
                    .all()
        )
        text_counts_by_classification = {c: cnt for c, cnt in text_counts}

        # Counts by classification for image content
        image_counts = await asyncio.to_thread(
            lambda: db.query(
                        models.ModerationResult.classification,
                        func.count(models.ModerationResult.classification)
                    )
                    .join(models.ModerationRequest)
                    .filter(
                        models.ModerationRequest.email == user,
                        models.ModerationRequest.content_type == "image"
                    )
                    .group_by(models.ModerationResult.classification)
                    .all()
        )
        image_counts_by_classification = {c: cnt for c, cnt in image_counts}

        # Get timestamp and ID of last request by user
        last_request = await asyncio.to_thread(
            lambda: db.query(models.ModerationRequest.created_at, models.ModerationRequest.id)
                       .filter(models.ModerationRequest.email == user)
                       .order_by(models.ModerationRequest.created_at.desc())
                       .first()
        )
        last_request_at = last_request[0] if last_request else None
        last_request_id = last_request[1] if last_request else None

        # Get all request IDs by user for fetching notification logs
        request_ids = await asyncio.to_thread(
            lambda: db.query(models.ModerationRequest.id)
                       .filter(models.ModerationRequest.email == user)
                       .all()
        )
        request_ids = [r[0] for r in request_ids]

        notification_logs = []
        if request_ids:
            logs = await asyncio.to_thread(
                lambda: db.query(models.NotificationLog)
                          .filter(models.NotificationLog.request_id.in_(request_ids))
                          .order_by(models.NotificationLog.sent_at.desc())
                          .all()
            )
            notification_logs = [schemas.NotificationLogResponse.model_validate(log) for log in logs]

        # Prepare HTML email content
        html_content = analytics_email_html(
            user=user,
            total_requests=total_requests,
            text_counts=text_counts_by_classification,
            image_counts=image_counts_by_classification,
            last_request_at=last_request_at
        )

        # Send alert email in a background thread
        await asyncio.to_thread(
            send_alert_email,
            subject="📊 Your Moderation Analytics Summary",
            html_content=html_content,
            to_email=user
        )

        # Insert notification log after email sent
        if last_request_id:
            await asyncio.to_thread(insert_notification, db, last_request_id)

        # Prepare and return response
        response_data = schemas.AnalyticsSummaryResponse(
            user=user,
            total_requests=total_requests,
            counts_by_classification={**text_counts_by_classification, **image_counts_by_classification},
            last_request_at=last_request_at,
            notification_logs=notification_logs
        )

        logger.info(f"Analytics summary generated successfully for user: {user}")
        return ApiResponse(status_code=200, success=True, message="Success", data=response_data)

    except Exception as e:
        logger.error(f"Analytics summary failed for user {user}: {e}")
        raise ApiError(500, f"Analytics summary failed: {str(e)}")
