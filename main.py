from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
templates = Jinja2Templates(directory="templates")

active_drivers = [
    {"name": "driver1", "status": "On Duty", "phone": "+14238104065"}
]

maintenance_logs = [
    {"shuttle_id": "Shuttle Van #03", "service_note": "Scheduled brake check & tire rotation"}
]

ride_requests = [
    {"rider_name": "Sarah Jenkins", "facility": "Cleveland Medical Center", "pickup": "2500 North Ocoee St", "dropoff": "Downtown Transit Hub"}
]

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(request, "404.html", {"request": request}, status_code=404)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.get("/")
def read_root():
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form("")):
    uname = username.lower()
    if "admin" in uname:
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    elif "driver" in uname:
        return RedirectResponse(url="/driver/terminal", status_code=303)
    else:
        return RedirectResponse(url="/user/dashboard", status_code=303)

@app.get("/admin")
def admin_direct():
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@app.get("/admin/dashboard")
def admin_dashboard(request: Request):
    return templates.TemplateResponse(request, "admin_dashboard.html", {
        "request": request,
        "username": "admin1",
        "drivers": active_drivers,
        "maintenance_records": maintenance_logs,
        "ride_requests": ride_requests
    })

@app.get("/admin/shuttles")
def admin_shuttles(request: Request):
    return templates.TemplateResponse(request, "shuttles.html", {
        "request": request,
        "drivers": active_drivers
    })

@app.get("/admin/drivers")
def admin_drivers_view(request: Request):
    return templates.TemplateResponse(request, "drivers_list.html", {
        "request": request,
        "drivers": active_drivers
    })

@app.get("/admin/maintenance-view")
def admin_maintenance_view(request: Request):
    return templates.TemplateResponse(request, "maintenance_view.html", {
        "request": request,
        "maintenance_records": maintenance_logs
    })

@app.get("/driver/terminal")
def driver_terminal(request: Request):
    return templates.TemplateResponse(request, "driver_terminal.html", {
        "request": request, 
        "username": "driver1",
        "ride_requests": ride_requests
    })

@app.get("/driver/accept")
def driver_accept(request: Request):
    return templates.TemplateResponse(request, "driver_terminal.html", {
        "request": request, 
        "username": "driver1", 
        "ride_requests": ride_requests,
        "success": "Ride assignment accepted successfully! Proceeding to pickup location."
    })

@app.get("/driver/decline")
def driver_decline(request: Request):
    if ride_requests:
        ride_requests.pop(0)
    return templates.TemplateResponse(request, "driver_terminal.html", {
        "request": request, 
        "username": "driver1", 
        "ride_requests": ride_requests,
        "success": "Ride assignment declined and returned to dispatch queue."
    })

@app.post("/driver/break")
def driver_break(request: Request):
    for d in active_drivers:
        if d["name"] == "driver1":
            d["status"] = "On Break (15m Compliant)"
    return templates.TemplateResponse(request, "driver_terminal.html", {
        "request": request, 
        "username": "driver1", 
        "ride_requests": ride_requests,
        "break_success": "Rest break requested and approved in compliance with labor guidelines!"
    })

@app.get("/user/dashboard")
def user_dashboard(request: Request):
    return templates.TemplateResponse(request, "user_portal.html", {
        "request": request, 
        "username": "passenger1",
        "ride_requests": ride_requests
    })

@app.post("/user/request-ride")
def request_ride(request: Request, rider_name: str = Form(...), facility: str = Form(...), pickup: str = Form(...), dropoff: str = Form(...)):
    ride_requests.append({
        "rider_name": rider_name,
        "facility": facility,
        "pickup": pickup,
        "dropoff": dropoff
    })
    return templates.TemplateResponse(request, "user_portal.html", {
        "request": request, 
        "username": "passenger1", 
        "ride_requests": ride_requests,
        "success": f"Ride successfully booked for {rider_name} from {facility}!"
    })

@app.post("/admin/maintenance")
def log_maintenance(request: Request, shuttle_id: str = Form(...), service_note: str = Form(...)):
    maintenance_logs.append({"shuttle_id": shuttle_id, "service_note": service_note})
    return templates.TemplateResponse(request, "admin_dashboard.html", {
        "request": request, 
        "username": "admin1",
        "drivers": active_drivers,
        "maintenance_records": maintenance_logs,
        "ride_requests": ride_requests
    })

@app.get("/logout")
def logout():
    return RedirectResponse(url="/login", status_code=303)
