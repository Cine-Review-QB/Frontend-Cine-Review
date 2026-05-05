import reflex as rx

config = rx.Config(
    app_name="cine_review",
    # Gateway roda em 8000; backend interno do Reflex precisa de outra porta.
    backend_port=8800,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)