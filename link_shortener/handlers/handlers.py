from flask import Blueprint, render_template, jsonify
from flask.globals import request
from werkzeug.exceptions import HTTPException

error_handlers = Blueprint("error_handler", __name__)


@error_handlers.app_errorhandler(HTTPException)
def api_errhandler(e):
    """Функция перехвата ошибок, возвращает страницу с ошибкой для браузерных эндпоинтов
    и JSON для api-эндпоинтов"""

    if not request.path.startswith("/api"):
        return render_template("error.html", error=e), e.code
    return {"error": f"{e}"}, e.code
