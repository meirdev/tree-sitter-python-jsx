# tree-sitter-python-jsx

```python
from jsx import render
from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    return render(
        <>
            <h1>Hello World</h1>
            <div>
                <button>Enter</button>
            </div>
        </>
    )

```
