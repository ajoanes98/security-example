"""Minimal payments gateway stub for the security scorecard workshop track."""


def health() -> dict:
    return {"status": "ok", "service": "payments-gateway"}


if __name__ == "__main__":
    print(health())
