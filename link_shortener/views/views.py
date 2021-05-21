from flask import Blueprint, jsonify, redirect, request
from flask.helpers import make_response
from flask.templating import render_template
from flask_apispec import marshal_with, use_kwargs
from flask_apispec.extension import make_apispec
from marshmallow import fields
from sqlalchemy.engine.base import TwoPhaseTransaction

from link_shortener import docs, hashid
from link_shortener.models import Main


shortener_api = Blueprint("shortener_api", __name__)


def link_encoder(new_record):
    return hashid.encode(new_record.id)


@shortener_api.route("/api", methods=["POST", "DELETE", "PUT"])
@use_kwargs({"link": fields.Url(), "new_link": fields.Url()})
def send_a_link(**kwargs):
    """API функция принимает:\n
    POST - для записи в базу и возвращает сокращенную ссылку\n
    DELETE для удаления ссылки\n
    """

    if request.method == "POST":
        try:
            new_record = Main.get_by_link(**kwargs)

            if not new_record:
                new_record = Main(**kwargs)
                new_record.save()

            returned_link = f"{request.host_url}{link_encoder(new_record)}"

            return make_response({"short link": returned_link})

        except Exception as e:
            return {"error": str(e)}, 400

    if request.method == "DELETE":
        try:
            link_for_delete = Main.get_by_link(**kwargs)
            link_for_delete.delete()
            return make_response({"message": "Ссылка удалена!"})
        except Exception as e:
            return {"error": str(e)}, 400

    if request.method == "PUT":
        try:
            """Этот алгоритм переименовывает старую ссылку в новую, если новая ссылка
            еще не находится в базе.
            Если ссылка находится в базе, пользователю передается короткая ссылка от
            уже существующей, а старая удаляется.
            Если старая ссылка не найдена, то возвращается код 400"""

            old_link, new_link = kwargs["link"], kwargs["new_link"]

            old_link_exists = Main.get_by_link(old_link)
            if not old_link_exists:
                return {"message": "ссылка не найдена!"}, 400

            chenged_url = f"{request.host_url}{link_encoder(old_link_exists)}"

            new_link_exists = Main.get_by_link(new_link)
            if new_link_exists:
                old_link_exists.delete()
            else:
                old_link_exists.update(new_link)
                chenged_url = f"{request.host_url}{link_encoder(old_link_exists)}"

            return {"message": f"Ссылка: {chenged_url}"}

        except Exception as e:
            return {"error": str(e)}, 400


@shortener_api.route("/", methods=["GET"])
def index_redirect():
    """Редирект на Swagger"""

    return redirect("/index")


@shortener_api.route("/<id>", methods=["GET"])
def redirect_to_url(id):
    """Функция перенаправляет с короткой ссылки на оригинальную или переводит на страницу ошибки"""

    try:
        redirect_url_postfix = hashid.decode(id)[0]
        original_url = Main.query.filter(Main.id == redirect_url_postfix).first()

    except Exception as e:
        return render_template("error.html", error=e), 404

    return redirect(original_url.link)


docs.register(send_a_link, blueprint="shortener_api")
