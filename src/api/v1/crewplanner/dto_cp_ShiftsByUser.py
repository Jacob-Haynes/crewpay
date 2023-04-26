from typing import List

from pydantic import BaseModel

from api.v1.crewplanner.dto_cp_shift import CPShift


class CPShiftsByUser(BaseModel):
    user_id: int
    shifts: List[CPShift]
