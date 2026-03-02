"""Citizen Engagement & Crowdsourcing — implements Prompt 5.5.

Incident reporting, community validation, gamification.
"""

import random
import uuid
from datetime import datetime, timezone

from app.models.schemas.problem_solving import (
    CitizenEngagementResponse,
    CitizenReport,
    IncidentCategory,
)


class CitizenService:
    """Service for Prompt 5.5 — Citizen Engagement & Crowdsourcing."""

    async def submit_report(
        self, category: str, lat: float, lng: float, road_name: str, description: str,
    ) -> CitizenEngagementResponse:
        cat = IncidentCategory(category) if category in [c.value for c in IncidentCategory] else IncidentCategory.OTHER

        # AI pre-classification (simulated)
        ai_class = f"AI classification: {cat.value.replace('_', ' ').title()} (confidence: {random.randint(85, 98)}%)"

        report = CitizenReport(
            report_id=f"CR-{uuid.uuid4().hex[:8].upper()}",
            category=cat,
            location_lat=lat,
            location_lng=lng,
            road_name=road_name,
            description=description,
            ai_classification=ai_class,
            verification_status="pending",
            verification_eta_minutes=random.randint(2, 5),
            reporter_reliability_score=random.uniform(75.0, 98.0),
        )

        return CitizenEngagementResponse(
            report=report,
            confirmation_message=f"Report #{report.report_id} submitted. Control room verification expected within {report.verification_eta_minutes} minutes. You'll be notified when confirmed.",
            community_validations=random.randint(0, 3),
            gamification={
                "badge": "Traffic Hero",
                "reports_count": random.randint(5, 25),
                "reliability_rank": "Gold",
                "points_earned": 10,
            },
            feedback_channels=[
                "Rate route recommendations after trip",
                "Report road quality issues (potholes, markings)",
                "Suggest signal timing improvements",
                "Community priority voting for infrastructure",
            ],
            timestamp=datetime.now(timezone.utc),
        )
