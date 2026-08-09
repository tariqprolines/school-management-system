from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_students: int
    total_teachers: int
    total_classes: int
    active_enrollments: int
    total_fee_collected: float
    total_fee_pending: float
    fee_collection_rate: float
    class_occupancy_rate: float
