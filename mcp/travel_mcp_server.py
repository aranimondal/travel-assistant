from datetime import date

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travel-assistant")


@mcp.tool()
def get_weather_forecast(location: str = "Singapore", days: int = 3) -> dict:
    """Return a short forecast for a place using Open-Meteo."""
    days = max(1, min(days, 7))
    with httpx.Client(timeout=10) as client:
        geo = client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
        )
        geo.raise_for_status()
        places = geo.json().get("results", [])
        if not places:
            return {"error": f"Location not found: {location}"}
        place = places[0]
        forecast = client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": days,
            },
        )
        forecast.raise_for_status()
        daily = forecast.json().get("daily", {})
        return {
            "location": place.get("name", location),
            "days": [
                {
                    "date": d,
                    "temp_max_c": max_temp,
                    "temp_min_c": min_temp,
                    "precipitation_probability": rain,
                }
                for d, max_temp, min_temp, rain in zip(
                    daily.get("time", []),
                    daily.get("temperature_2m_max", []),
                    daily.get("temperature_2m_min", []),
                    daily.get("precipitation_probability_max", []),
                )
            ],
        }


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert a monetary amount using Frankfurter's latest published rate."""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    with httpx.Client(timeout=10) as client:
        response = client.get(
            "https://api.frankfurter.app/latest",
            params={"amount": amount, "from": from_currency, "to": to_currency},
        )
        response.raise_for_status()
        payload = response.json()
    return {
        "amount": amount,
        "from": from_currency,
        "to": to_currency,
        "result": payload.get("rates", {}).get(to_currency),
        "date": payload.get("date", str(date.today())),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
