from server import app, db
from server.models import Admins, adminSchema, adminsSchema, Model, modelSchema, modelsSchema, Benh, benhSchema, benhsSchema, ModelBenh, modelSchema, modelsSchema, NhanDien, nhanDienSchema, nhanDiensSchema
from flask import jsonify, request, session
from flask_api import status
import os
import hashlib
import jwt
# from server.until import *
from datetime import date, datetime, timedelta
from server.msg import error, success

@app.route("/ping", methods=["GET"])
def ping():
    return "ping"
    
#api001
@app.route("/detect", methods=["POST"])
def detect():
    # Step 1 : Select model nhận diện
    try:
        Id_M = Model.query.filter_by(TrangThai=True).first().Id_M
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 2 : Lưu file ảnh vào hệ thống
    try:
        DiaChiAnh = datetime.now().strftime("%d%m%Y_%H%M%S") + ".jpg"
        f = request.files['image']
        f.save("./server/img/"+DiaChiAnh)
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    #Step 3 : Phân loại bệnh
    # try:
    #     DiaChiAnh = datetime.now().strftime("%d%m%Y_%H%M%S") + ".jpg"
    #     f = request.files['image']
    #     f.save("./server/img/"+DiaChiAnh)
    # except:
    #     return jsonify(
    #         messages=error["handleFailure"],
    #         success=False
    #     ), status.HTTP_400_BAD_REQUEST
    #Step 4 : Lấy thông tin bệnh
    try:
        Id_B=ModelBenh.query.filter_by(Id_M=Id_M,STT=1).first().Id_B
        B=Benh.query.filter_by(Id_B=Id_B).first()
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    #Step 5 : Tạo thông tin nhận diện mới
    try:
        insertNhanDien = NhanDien(DiaChiAnh=DiaChiAnh, Email=request.values["Email"], Id_B=Id_B,YKien="",Created=datetime.now(),Updated=datetime.now(), Created_function_id= "API001", Updated_function_id="API001", Revision=0,TrangThai=True)
        db.session.add(insertNhanDien)
        db.session.commit()
        Id_ND = db.session.query(NhanDien).order_by(NhanDien.Id_ND.desc()).first().Id_ND
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
   #Step 6 : Trả kết quả nhận diện về client
    return jsonify(
            Id_ND=Id_ND,
            Id_B=Id_B,
            ImgName=DiaChiAnh,
            Ten_B=B.Ten_B,
            ThongTin_B=B.ThongTin_B,
            CachChuaTri=B.CachChuaTri,
            GhiChu=B.GhiChu,
            success=True
        ), status.HTTP_200_OK
#api002
@app.route("/insertYKien", methods=["POST"])
def insertYKien():
    #Step 1 : Cập nhật ý kiến kết quả nhận diện
    try:
        Id_ND = request.values["Id_ND"]
        Nhandien = NhanDien.query.filter_by(Id_ND=Id_ND).first()
        Nhandien.YKien = request.values["YKien"]
        Nhandien.Update=datetime.now()
        Nhandien.Updated_function_id = "api002"
        Nhandien.Id_ND = Id_ND
        db.session.commit()
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    #Step 2 : Trả kết quả nhận diện về client
    return jsonify(
            messages=success["insertSuccess"],
            success=True
        ), status.HTTP_200_OK
#api003
@app.route("/login", methods=["POST"])
def login():
    #Step 1 : Kiểm tra thông tin đăng nhập
    try:
        username = request.values["username"]
        password = hashlib.md5(request.values["password"].encode()).hexdigest()
        records = Admins.query.filter_by(username=username, password=password).first()
        if records:
            token = jwt.encode({
                'user': username,
                'exp': datetime.now() + timedelta(seconds=1440)
            }, app.config['SECRET_KEY'])
            session['logged_in'] = True
    #Step 2 : Xử lý kết quả xác thực
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    
    #Step 3 : Kiểm tra thông tin đăng nhập
    return jsonify(
            token=token.decode('utf-8'),
            success=True
        ), status.HTTP_200_OK