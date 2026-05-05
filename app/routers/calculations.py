from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.crud import calculation as crud
from app.schemas.calculation import CalculationCreate, CalculationUpdate
from app.models.user import User

router = APIRouter(prefix="/calculations", tags=["calculations"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def browse(request: Request, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    calcs = crud.get_calculations(db, current_user.id)
    return templates.TemplateResponse(request, "calculations/list.html",
        {"calculations": calcs, "user": current_user})

@router.get("/new", response_class=HTMLResponse)
def add_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(request, "calculations/form.html",
        {"user": current_user, "calc": None})

@router.post("/new")
def add(request: Request, operation: str = Form(...),
        operand1: float = Form(...), operand2: float = Form(...),
        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        data = CalculationCreate(operation=operation, operand1=operand1, operand2=operand2)
        crud.create_calculation(db, data, current_user.id)
        return RedirectResponse("/calculations", status_code=302)
    except Exception as e:
        return templates.TemplateResponse(request, "calculations/form.html",
            {"user": current_user, "calc": None, "error": str(e)})

@router.get("/{calc_id}", response_class=HTMLResponse)
def read(calc_id: int, request: Request, db: Session = Depends(get_db),
         current_user: User = Depends(get_current_user)):
    calc = crud.get_calculation(db, calc_id, current_user.id)
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return templates.TemplateResponse(request, "calculations/detail.html",
        {"calc": calc, "user": current_user})

@router.get("/{calc_id}/edit", response_class=HTMLResponse)
def edit_page(calc_id: int, request: Request, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    calc = crud.get_calculation(db, calc_id, current_user.id)
    if not calc:
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse(request, "calculations/form.html",
        {"user": current_user, "calc": calc})

@router.post("/{calc_id}/edit")
def edit(calc_id: int, request: Request, operation: str = Form(...),
         operand1: float = Form(...), operand2: float = Form(...),
         db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    calc = crud.get_calculation(db, calc_id, current_user.id)
    if not calc:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        data = CalculationUpdate(operation=operation, operand1=operand1, operand2=operand2)
        crud.update_calculation(db, calc_id, data, current_user.id)
        return RedirectResponse("/calculations", status_code=302)
    except HTTPException:          # ← ADDED
        raise                      # ← ADDED
    except Exception as e:
        return templates.TemplateResponse(request, "calculations/form.html",
            {"user": current_user, "calc": calc, "error": str(e)})

@router.post("/{calc_id}/delete")
def delete(calc_id: int, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    if not crud.delete_calculation(db, calc_id, current_user.id):
        raise HTTPException(status_code=404, detail="Not found")
    return RedirectResponse("/calculations", status_code=302)

@router.get("/api/all", tags=["api"])
def api_browse(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.get_calculations(db, current_user.id)

@router.post("/api", status_code=201, tags=["api"])
def api_add(data: CalculationCreate, db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    return crud.create_calculation(db, data, current_user.id)

@router.put("/api/{calc_id}", tags=["api"])
def api_edit(calc_id: int, data: CalculationUpdate, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    result = crud.update_calculation(db, calc_id, data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result

@router.delete("/api/{calc_id}", tags=["api"])
def api_delete(calc_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    if not crud.delete_calculation(db, calc_id, current_user.id):
        raise HTTPException(status_code=404, detail="Not found")
    return {"detail": "deleted"}