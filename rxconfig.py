import os
import reflex as rx

config = rx.Config(
    app_name="cine_review",
    backend_port=int(os.getenv("BACKEND_PORT", "8800")),
    api_url=os.getenv("API_URL", "http://localhost:8800"),
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)