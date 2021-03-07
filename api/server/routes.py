from server import app
from server.models import Admins, adminSchema, adminsSchema, Model, modelSchema, modelsSchema, Benh, benhSchema, benhsSchema, ModelBenh, modelSchema, modelsSchema, NhanDien, nhanDienSchema, nhanDiensSchema

@app.route("/ping", methods=["GET"])
def ping():
    return "ping"