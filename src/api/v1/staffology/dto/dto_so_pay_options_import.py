from typing import List

from pydantic import BaseModel


class Line(BaseModel):
    value: float
    rate: float
    multiplier: float
    description: str
    code: str


class PayLine(BaseModel):
    payrollCode: str
    lines: List[Line]
