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
from functools import wraps

# check token
def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.headers['Authentication']
        if not token:
            Logout()
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            Logout()
        return func(*args, **kwargs)
    return wrapped

#Đăng xuất
@app.route("/logout", methods=["GET"])
def Logout():
    session['logged_in'] = False
    return "logout"

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
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    #Step 2 : Xử lý kết quả xác thực
    if records:
        token = jwt.encode({
            'user': username,
            'exp': datetime.now() + timedelta(seconds=1440)
        }, app.config['SECRET_KEY'])
        session['logged_in'] = True
    else:
        return jsonify(
            messages=error["AuthenticationFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    #Step 3 : Kiểm tra thông tin đăng nhập
    return jsonify(
            token=token.decode('utf-8'),
            success=True
        ), status.HTTP_200_OK
#api004
@app.route("/insertBenh", methods=["POST"])
#Step 1 : Check user token
@check_for_token
def insertBenh():
    #Step 2 : Tạo bệnh mới
    try:
        insertBenh = Benh(Ten_B=request.values["Ten_B"],ThongTin_B=request.values["ThongTin_B"],CachChuaTri=request.values["CachChuaTri"],GhiChu=request.values["GhiChu"],Created=datetime.now(),Updated=datetime.now(),Created_function_id="api004",Updated_function_id="api004",Revision=0,TrangThai=True)
        db.session.add(insertBenh)
        db.session.commit()
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    #Step 3 : Trả về kết quả xử lý
    return jsonify(
            Records=1,
            success=True
        ), status.HTTP_200_OK
#api005
@app.route("/updateBenh", methods=["PATCH"])
#Step 1 : Check user token
@check_for_token
def updateBenh():
    #Step 2 : Tạo bệnh mới
    try:
        Id_B = request.values["Id_B"]
        benh = Benh.query.filter_by(Id_B=Id_B).first()
        benh.Ten_B=request.values["Ten_B"]
        benh.ThongTin_B=request.values["ThongTin_B"]
        benh.CachChuaTri=request.values["CachChuaTri"]
        benh.GhiChu=request.values["GhiChu"]
        benh.Updated=datetime.now()
        benh.Updated_function_id="api005"
        benh.Revision+=1
        benh.TrangThai=True
        benh.Id_B=Id_B
        db.session.commit()
    except:
        return jsonify(
            messages=error["handleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    #Step 3 : Trả về kết quả xử lý
    return jsonify(
            Records=1,
            success=True
        ), status.HTTP_200_OK