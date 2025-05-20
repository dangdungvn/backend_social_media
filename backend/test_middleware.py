# Script để debug whitenoise_middleware.py


class DummyApp:
    async def __call__(self, scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/plain")],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"Hello from dummy app",
            }
        )


def test_middleware():
    from whitenoise_middleware import ASGIStaticFilesHandler

    middleware = ASGIStaticFilesHandler(DummyApp())
    print("Middleware created successfully")
    print("Test complete")


if __name__ == "__main__":
    test_middleware()
