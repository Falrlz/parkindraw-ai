"""Root executable entrypoint for ParkinDraw AI Backend API."""

import uvicorn


def main() -> None:
    """Launch development server using uvicorn."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
