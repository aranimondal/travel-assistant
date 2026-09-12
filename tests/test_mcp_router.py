from app.mcp_client import detect_tool_needs


def test_weather_detection():
    needs = detect_tool_needs("What is the weather in Singapore tomorrow?")
    assert needs == {"weather": True, "currency": False}


def test_currency_detection():
    needs = detect_tool_needs("Convert INR 60000 to SGD")
    assert needs == {"weather": False, "currency": True}


def test_combined_detection():
    needs = detect_tool_needs("Plan a trip using the weather and convert my INR budget to SGD")
    assert needs == {"weather": True, "currency": True}
