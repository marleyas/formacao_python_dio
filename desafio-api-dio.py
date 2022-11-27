from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import json
import uvicorn

app = FastAPI()


@app.get('/')
async def home():
    return RedirectResponse(url='/data')


@app.get('/data')
async def show_data():
    file_json = open('estados-brasil.json')
    print(file_json)
    json_data = json.loads(file_json.read())
    return json_data['estados']

uvicorn.run(app, port=8000)
