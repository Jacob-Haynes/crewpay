from pydantic import BaseModel

from api.v1.crewplanner.dto.dto_cp_shift import CPShift


class CPShiftsByUser(BaseModel):
    user_id: int
    shifts: list[CPShift]
