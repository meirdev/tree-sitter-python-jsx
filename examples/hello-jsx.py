from datetime import datetime


def App():
    hour = datetime.now().hour

    if 5 <= hour < 12:
        text = "Morning"
    elif 12 <= hour < 17:
        text = "Afternoon"
    elif 17 <= hour < 21:
        text = "Evening"
    else:
        text = "Night"

    return (
        <div>
            <h1 style="text-align: center">Good {text}!</h1>
        </div>
    )
