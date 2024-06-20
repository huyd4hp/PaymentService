#! ./venv/bin/python3.12
from fastapi import FastAPI
from payment import VNPayRouter
from auth.middleware import ExceptionHandlerMiddleware
app = FastAPI()

app.include_router(VNPayRouter,prefix='/vnpay')
app.middleware(ExceptionHandlerMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        port=8567,
        reload=True,
    )