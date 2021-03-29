from server import app, db
from server.models import Admins, adminSchema, Benh, benhSchema, benhsSchema, NhanDien, nhanDienSchema, nhanDiensSchema, Model, modelSchema, modelsSchema, ModelBenh, modelBenhSchema, modelBenhsSchema
from flask import request, jsonify, render_template, send_file, send_from_directory, session
import hashlib
import shutil
import os
from server.until import *
from functools import wraps
import jwt
import datetime
import ast

@app.route("/admin/anh", methods=["GET"])
def loadAnh():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template("library.html")

# trang chủ
@app.route("/", methods=["GET"])
def main():
    return render_template("index.html")

# load ảnh
@app.route("/image", methods=["GET"])
def send_images():
    image_name = get_queries(request)["image"]
    return send_file(f"./templates/img/{image_name}", mimetype='image/gif')

# đăng nhập
@app.route("/login", methods=["GET"])
def LoadLogin():
    return render_template("login.html")
    

# đăng nhập
@app.route("/admin", methods=["GET"])
def Admin():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template("sick.html")

# load nhập bệnh
@app.route("/insertBenh", methods=["GET"])
def loadInsertBenh():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template("insertBenh.html")

# load cập nhật bệnh
@app.route("/updateBenh", methods=["GET"])
def loadUpdateBenh():
    if not session.get('logged_in'):
        return render_template('login.html')
    queries = get_queries(request)

    benhList = Benh.query.all()
    all_benhs = format_benhs_list(
        filter_arr_by_queries(benhsSchema.dump(benhList), queries))

    return render_template("updateBenh.html", benh=all_benhs[0])

# load danh sách bệnh đã xóa
@app.route("/deleteList", methods=["GET"])
def deletedSick():
    return render_template("deletedSick.html")

# load add model
@app.route("/addModel", methods=["GET"])
def loadAddModel():
    return render_template("addModel.html")