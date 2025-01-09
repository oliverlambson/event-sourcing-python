import json

class AmbarResponseFactory:
    @staticmethod
    def retry_response(exception: Exception) -> str:
        message = str(exception).replace('"', '\\"')
        return json.dumps({
            "result": {
                "error": {
                    "policy": "must_retry",
                    "class": exception.__class__.__name__,
                    "description": f"message:{message}"
                }
            }
        })

    @staticmethod
    def success_response() -> str:
        return json.dumps({
            "result": {
                "success": {}
            }
        })