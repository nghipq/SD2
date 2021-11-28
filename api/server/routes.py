from server import app, db
from server.models import Admins, adminSchema, adminsSchema, Model, modelSchema, modelsSchema, Benh, benhSchema, benhsSchema, ModelBenh, modelSchema, modelsSchema, NhanDien, nhanDienSchema, nhanDiensSchema
from flask import jsonify, request, session, send_file, send_from_directory, render_template
from flask_api import status
import os
import hashlib
import jwt
from server.until import get_queries, insertMB, deleteMB, format_benhs_list, filter_arr_by_queries, format_nhandiens_list, format_models_list, detect_tom_desease
from datetime import date, datetime, timedelta
from server.msg import error, success
from functools import wraps
import json
import shutil

# check user token
def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        print(request.headers)
        token = request.headers['Authentication']
        if not token:
            Logout()
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            Logout()
        return func(*args, **kwargs)
    return wrapped

# Đăng xuất
@app.route("/logout", methods=["GET"])
def Logout():
    session['logged_in'] = False
    return render_template("login.html")

# api001
@app.route("/detect", methods=["POST"])
def detect():
    # Step 1 : Select model nhận diện
    try:
        print("Step 1 start")
        M = Model.query.filter_by(TrangThai=True).first()
        Id_M = M.Id_M
        Ten_M = M.Ten_M
        print("Step 1 success")
    except:
        print("Step 5 faile")
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # # Step 2 : Lưu file ảnh vào hệ thống
    try:
        print("Step 2 start")
        DiaChiAnh = datetime.now().strftime("%d%m%Y_%H%M%S") + f"_{len(os.listdir('./server/img'))}.jpg"
        print(DiaChiAnh)
        f = request.files['image']
        f.save("./server/img/"+DiaChiAnh)
        print("Step 2 success")
    except:
        print("Step 2 faile")
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # # Step 3 : Phân loại bệnh
    try:
        print("Step 3 start")
        STT = int(detect_tom_desease(DiaChiAnh, Ten_M)) + 1
        if STT == 0:
            print("Step 3 - STT 0")
            return jsonify(
                messages=error["cannotDetection"],
                success=False
            ), status.HTTP_400_BAD_REQUEST
        print("Step 3 success")
    except:
        print("Step 3 faile")
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 4 : Lấy thông tin bệnh
    try:
        print("Step 4 start")
        print(f"Id model: {Id_M-1}, STT: {STT}")
        Id_B = ModelBenh.query.filter_by(Id_M=Id_M-1, STT=STT).first().Id_B
        print(Id_B)
        B = Benh.query.filter_by(Id_B=Id_B).first()
        print("Step 4 success")
    except:
        print("Step 4 faile")
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 5 : Tạo thông tin nhận diện mới
    try:
        print("Step 5 start")
        insertNhanDien = NhanDien(DiaChiAnh=DiaChiAnh, Email=request.values["Email"], Id_B=Id_B, YKien="", Created=datetime.now(), 
        Updated=datetime.now(), Created_function_id="API001", Updated_function_id="API001", Revision=0, TrangThai=True)
        db.session.add(insertNhanDien)
        db.session.commit()
        Id_ND = db.session.query(NhanDien).order_by(
            NhanDien.Id_ND.desc()).first().Id_ND
        print("Step 5 success")
    except:
        print("Step 5 faile")
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
   # Step 6 : Trả kết quả nhận diện về client
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

# api002
@app.route("/insertYKien", methods=["POST"])
def insertYKien():
    # Step 1 : Cập nhật ý kiến kết quả nhận diện
    try:
        Id_ND = request.values["Id_ND"]
        Nhandien = NhanDien.query.filter_by(Id_ND=Id_ND).first()
        Nhandien.YKien = request.values["YKien"]
        Nhandien.Update = datetime.now()
        Nhandien.Updated_function_id = "api002"
        db.session.commit()
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 2 : Trả kết quả nhận diện về client
    return jsonify(
        messages=success["insertSuccess"],
        success=True
    ), status.HTTP_200_OK

# api003
@app.route("/login", methods=["POST"])
def login():
    # Step 1 : Kiểm tra thông tin đăng nhập
    try:
        username = request.values["username"]
        password = hashlib.md5(request.values["password"].encode()).hexdigest()
        records = Admins.query.filter_by(
            username=username, password=password).first()
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 2 : Xử lý kết quả xác thực
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
    # Step 3 : Kiểm tra thông tin đăng nhập
    return jsonify(
        token=token.decode('utf-8'),
        success=True
    ), status.HTTP_200_OK

# api004
@app.route("/insertBenh", methods=["POST"])
# Step 1 : Check user token
@check_for_token
def insertBenh():
    # Step 2 : Tạo bệnh mới
    try:
        insertBenh = Benh(Ten_B=request.values["Ten_B"], ThongTin_B=request.values["ThongTin_B"], CachChuaTri=request.values["CachChuaTri"], GhiChu=request.values["GhiChu"], Created=datetime.now(
        ), Updated=datetime.now(), Created_function_id="api004", Updated_function_id="api004", Revision=0, TrangThai=True)
        db.session.add(insertBenh)
        db.session.commit()
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api005
@app.route("/updateBenh", methods=["PATCH"])
# Step 1 : Check user token
@check_for_token
def updateBenh():
    # # Step 2 : Tạo bệnh mới
    try:
        Id_B = request.values["Id_B"]
        benh = Benh.query.filter_by(Id_B=Id_B).first()
        benh.Ten_B = request.values["Ten_B"]
        benh.ThongTin_B = request.values["ThongTin_B"]
        benh.CachChuaTri = request.values["CachChuaTri"]
        benh.GhiChu = request.values["GhiChu"]
        benh.Updated = datetime.now()
        benh.Updated_function_id = "api005"
        benh.Revision = 1
        benh.TrangThai = bool(request.values["TrangThai"])
        benh.Id_B = Id_B
        db.session.commit()
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api006
@app.route("/deleteBenh", methods=["DELETE"])
# Step 1 : Check user token
@check_for_token
def deleteBenh():
    # Step 2 : Xóa bệnh
    try:
        Id_B = Benh.query.filter_by(Id_B=request.values["Id_B"]).delete()
        db.session.commit()
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api007
@app.route("/insertModel", methods=["POST"])
# Step 1 : Check user token
@check_for_token
def insertModel():
    try:
        Ten_M = request.values["Ten_M"]
        Records = Model.query.filter_by(Ten_M=Ten_M)
        # Step 2 : Check tên model đã tồn tại hay chưa
        if Records.count() > 0:
            return jsonify(
                success=False,
                message="Model name is already exist !"
            )
        # Step 3 : Lưu file model
        Models = request.files["Model"]
        Models.save(f"./server/models/{request.values['Ten_M']}.pickle")
        # Step 4 : Tạo model mới
        oldModel = Model.query.filter_by(TrangThai=True).first()
        oldModel.TrangThai = False

        try:
            db.session.commit()
        except:
            return jsonify(
                    messages=error["HandleFailure"],
                    success=False
                ), status.HTTP_400_BAD_REQUEST

        insertModel = Model(Ten_M=Ten_M, Created=datetime.now(), Updated=datetime.now(
        ), Created_function_id="api007", Updated_function_id="api007", Revision=0, TrangThai=True)
        try:
            db.session.add(insertModel)
            db.session.commit()
        except:
            return jsonify(
                    messages=error["HandleFailure"],
                    success=False
                ), status.HTTP_400_BAD_REQUEST

        Id_M = db.session.query(Model).order_by(Model.Id_M.desc()).first().Id_M
        # Step 5 : Tạo model bệnh mới
        BenhList = request.values["BenhList"]
        BenhLists = json.loads(BenhList)

        for benh in BenhLists:
            try:
                insertMB(Id_M, benh["Id_B"], benh["STT"],True)
            except:
                return jsonify(
                    messages=error["HandleFailure"],
                    success=False
                ), status.HTTP_400_BAD_REQUEST

    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 6 : Trả về kết quả xử lý
    return jsonify(
            Records=1,
            success=True
        ), status.HTTP_200_OK

# api008
@app.route("/insertModelBenh", methods=["POST"])
# Step 1 : Check user token
@check_for_token
def insertModelBenh():
    # Step 2 : Tạo model bệnh mới
    try:
        insertMB(request.values["Id_M"],
                 request.values["Id_B"], request.values["STT"] + 1,True)
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api009
@app.route("/updateModel", methods=["PATCH"])
# Step 1 : Check user token
@check_for_token
def updateModel():
    try:
        Ten_M = request.values["Ten_M"]
        Id_M = request.values["Id_M"]
        Records = Model.query.filter_by(Ten_M=Ten_M)
        GetId = Model.query.filter_by(Id_M=Id_M)
        Models = request.files["Model"]
        # Step 2 : Check tên model đã tồn tại hay chưa
        if Records.count() > 0 & GetId.Ten_M != Ten_M:
            Models.remove(f"./server/models/{request.values['Ten_M']}.pickle")
            return jsonify(
                success=False,
                message="Model name is already exist !"
            )
        # Step 3 : Lưu file model
        Models.save(f"./server/models/{request.values['Ten_M']}.pickle")
        # Step 4 : Xóa model bệnh
        deleteMB(Id_M)
        # Step 5 : Cập nhật model
        Models = Model.query.filter_by(Id_M=Id_M).first()
        Models.Ten_M = Ten_M
        Models.Updated = datetime.now()
        Models.Updated_function_id = "api009"
        Models.Revision = (Models.Revision + 1)
        Models.TrangThai = bool(request.values["TrangThai"])
        Models.Id_M = Id_M
        db.session.commit()
        # Step 6 : Tạo model bệnh mới
        BenhList = request.values["BenhList"]
        BenhLists = ast.literal_eval(BenhList)["BenhList"]
        print(BenhList)
        for benh in BenhLists:
            try:
                insertMB(Id_M, benh.Id_B, benh.STT,benh.TrangThai)
            except:
                return jsonify(
                    messages=error["HandleFailure"],
                    success=False
                ), status.HTTP_400_BAD_REQUEST

    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 7 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api011
@app.route("/deleteModel", methods=["DELETE"])
# Step 1 : Check user token
@check_for_token
def deleteModel():
    try:
        # Step 2 : Xóa model bệnh
        deleteMB(request.values["Id_M"])
        # Step 3 : Xóa model
        Id_M=Model.query.filter_by(Id_M=request.values["Id_M"]).delete()
        db.session.commit()
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api012   
@app.route("/deleteModelBenh", methods=["DELETE"])
# Step 1 : Check user token
@check_for_token
def deleteModelBenh():
    try:
        # Step 2 : Xóa model bệnh
        deleteMB(request.values["Id_M"])
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
    # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api013
@app.route("/loadImage", methods=["GET"])
def loadImage():
    try:
        # Step 1 : Lấy file ảnh
        ImageName = get_queries(request)["ImageName"]
        # Step 2 : Trả về kết quả xử lý
        return send_file(f"./img/{ImageName}", mimetype='image/gif')
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST

# api014
@app.route("/exportImage", methods=["GET"])
def exportImage():
    try:
        # Step 1 : Lấy file “.Zip” ảnh
        shutil.make_archive("./server/data_anh_benh", 'zip', "./server/img")
        return send_from_directory(directory=".", filename="data_anh_benh.zip", as_attachment=True)
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
        # Step 2 : Trả về kết quả xử lý
    return jsonify(
        Records=1,
        success=True
    ), status.HTTP_200_OK

# api015
@app.route("/benhList", methods=["GET"])
# Step 1 : Check user token
@check_for_token
def benhList():
    try:
        # Step 2 : Lấy danh sách bệnh
        queries = get_queries(request)
        try:
            Updated_datefrom = queries["Updated_datefrom"]
            Updated_dateto = queries["Updated_dateto"]
            BenhList = Benh.query.filter(Benh.Updated >= Updated_datefrom, Benh.Updated <= (Updated_dateto + " 23:59:59"))
        except:
            try:
                Updated_datefrom = queries["Updated_datefrom"]
                BenhList = Benh.query.filter(Benh.Updated >= Updated_datefrom)
            except:
                try:
                    Updated_dateto = queries["Updated_dateto"]
                    BenhList = Benh.query.filter(Benh.Updated <= (Updated_dateto + " 23:59:59"))
                except:    
                    BenhList = Benh.query.all()
        all_benhs = format_benhs_list(filter_arr_by_queries(benhsSchema.dump(BenhList), queries))
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
        # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=all_benhs,
        success=True
    ), status.HTTP_200_OK

# api016
@app.route("/ModelList", methods=["GET"])
# Step 1 : Check user token
# @check_for_token
def ModelList():
    try:
        # Step 2 : Lấy danh sách model
        queries = get_queries(request)
        try:
            Updated_datefrom = queries["Updated_datefrom"]
            Updated_dateto = queries["Updated_dateto"]
            ModelList = Model.query.filter(Model.Updated >= Updated_datefrom, Model.Updated <= (Updated_dateto + " 23:59:59"))
        except:
            try:
                Updated_datefrom = queries["Updated_datefrom"]
                ModelList = Model.query.filter(Model.Updated >= Updated_datefrom)
            except:
                try:
                    Updated_dateto = queries["Updated_dateto"]
                    ModelList = Model.query.filter(Model.Updated <= (Updated_dateto + " 23:59:59"))
                except:    
                    ModelList = Model.query.all()
        all_models = format_models_list(filter_arr_by_queries(modelsSchema.dump(ModelList), queries))
        # Step 3 : Xử lý ModelBenhList của từng Model
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
        # Step 3 : Trả về kết quả xử lý
    return jsonify(
        Records=all_models,
        success=True
    ), status.HTTP_200_OK

# api017
@app.route("/NhanDienList", methods=["GET"])
def NhanDienList():
    try:
        # Step 1 : Tạo thông tin nhận diện mới
        queries = get_queries(request)
        try:
            Updated_datefrom = queries["Updated_datefrom"]
            Updated_dateto = queries["Updated_dateto"]
            NhanDienList = NhanDien.query.filter(NhanDien.Updated >= Updated_datefrom, NhanDien.Updated <= (Updated_dateto + " 23:59:59"))
        except:
            try:
                Updated_datefrom = queries["Updated_datefrom"]
                NhanDienList = NhanDien.query.filter(NhanDien.Updated >= Updated_datefrom)
            except:
                try:
                    Updated_dateto = queries["Updated_dateto"]
                    NhanDienList = NhanDien.query.filter(NhanDien.Updated <= (Updated_dateto + " 23:59:59"))
                except:    
                    NhanDienList = NhanDien.query.all()
        all_nhandiens = format_nhandiens_list(filter_arr_by_queries(nhanDiensSchema.dump(NhanDienList), queries))
    except:
        return jsonify(
            messages=error["HandleFailure"],
            success=False
        ), status.HTTP_400_BAD_REQUEST
        # Step 3 : Trả kết quả nhận diện về client
    return jsonify(
        Records=all_nhandiens,
        success=True
    ), status.HTTP_200_OK

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
