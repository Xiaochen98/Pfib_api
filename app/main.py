from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class InterpolationRequest(BaseModel):
    x: float
    y: float
    sheet: str

@app.post("/interpolate")
def interpolate_and_return_value(req: InterpolationRequest):
    try:
        df = pd.read_excel("matrix.xlsm", sheet_name=req.sheet, index_col=0)

        x_vals = list(df.columns.astype(float))
        y_vals = list(df.index.astype(float))

        x1 = max([val for val in x_vals if val <= req.x], default=None)
        x2 = min([val for val in x_vals if val >= req.x], default=None)
        y1 = max([val for val in y_vals if val <= req.y], default=None)
        y2 = min([val for val in y_vals if val >= req.y], default=None)

        if None in (x1, x2, y1, y2) or x1 == x2 or y1 == y2:
            raise ValueError("x or y out of bounds")

        Q11 = df.loc[y1, str(x1)]
        Q21 = df.loc[y1, str(x2)]
        Q12 = df.loc[y2, str(x1)]
        Q22 = df.loc[y2, str(x2)]

        x, y = req.x, req.y
        interpolated_value = (1 / ((x2 - x1) * (y2 - y1))) * (
            Q11 * (x2 - x) * (y2 - y) +
            Q21 * (x - x1) * (y2 - y) +
            Q12 * (x2 - x) * (y - y1) +
            Q22 * (x - x1) * (y - y1)
        )

        return {"value": interpolated_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
