from fastapi import APIRouter, Request, Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models import CarBase, CarUpdate

router = APIRouter()

@router.get("/", response_description="List all cars")
async def list_cars(request: Request):
    query = "SELECT * FROM cars"
    async with request.app.state.db_pool.acquire() as connection:
        cars = await connection.fetch(query)
    return {"data": [dict(car) for car in cars]}

@router.post("/", response_description="Add new car", status_code=status.HTTP_201_CREATED)
async def create_car(request: Request, car: CarBase = Body(...)):
    car_data = jsonable_encoder(car)
    query = """
    INSERT INTO cars (brand, make, year, price, km, cm3)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING *
    """
    async with request.app.state.db_pool.acquire() as connection:
        new_car = await connection.fetchrow(query, car_data['brand'], car_data['make'], car_data['year'], car_data['price'], car_data['km'], car_data['cm3'])
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=dict(new_car))

@router.put("/{car_id}", response_description="Update a car")
async def update_car(request: Request, car_id: str, car: CarUpdate = Body(...)):
    car_data = car.dict(exclude_unset=True)
    query = "UPDATE cars SET "
    query += ", ".join(f"{key} = ${i}" for i, key in enumerate(car_data.keys(), start=1))
    query += " WHERE id = $%d RETURNING *" % (len(car_data) + 1)
    async with request.app.state.db_pool.acquire() as connection:
        updated_car = await connection.fetchrow(query, *car_data.values(), car_id)
    if not updated_car:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Car not found"})
    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(updated_car))

@router.delete("/{car_id}", response_description="Delete a car")
async def delete_car(request: Request, car_id: str):
    query = "DELETE FROM cars WHERE id = $1 RETURNING *"
    async with request.app.state.db_pool.acquire() as connection:
        deleted_car = await connection.fetchrow(query, car_id)
    if not deleted_car:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Car not found"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Car deleted successfully"})
