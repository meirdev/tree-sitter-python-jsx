# tree-sitter-python-jsx

## How to run?

```bash
git clone git@github.com:meirdev/tree-sitter-python-jsx.git
cd tree-sitter-python-jsx

python -m venv venv
source venv/bin/activate

python -m pip install tree-sitter setuptools wheel
python setup.py install

python -m jsx FILENAME.pyx
```

## Example

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

result:

```python
from jsx import Element, Fragment
from jsx import render
from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    return render(
        Element('Fragment', {'children': [Element('h1', {'children': "Hello World"}), Element('div', {'children': Element('button', {'children': "Enter"})})]})
    )
```
