from server import db, ma
from datetime import datetime

#Admins
class Admins(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(200))
    def __init__(self, username, password):
        self.username = username
        self.password = password

class AdminsSchema(ma.Schema):
    class Meta:
        fields = ("username", "password")

adminSchema = AdminsSchema()
adminsSchema = AdminsSchema(many = True)

#Model
class Model(db.Model):
    Id_M = db.Column(db.Integer, primary_key = True)
    Ten_M = db.Column(db.String(50))
    Created = db.Column(db.DateTime, default = datetime.utcnow)
    Updated = db.Column(db.DateTime, default = datetime.utcnow)
    Created_function_id = db.Column(db.String(20))
    Updated_function_id = db.Column(db.String(20))
    Revision = db.Column(db.Integer, default = 0)
    TrangThai = db.Column(db.Boolean, default = True)
    def __init__(self, Ten_M, Created, Updated, Created_function_id, Updated_function_id, Revision, TrangThai):
        self.Ten_M = Ten_M
        self.Created = Created
        self.Updated = Updated
        self.Created_function_id = Created_function_id
        self.Updated_function_id = Updated_function_id
        self.Revision = Revision
        self.TrangThai = TrangThai

class ModelSchema(ma.Schema):
    class Meta:
        fields = ("Id_M", "Ten_M", "Created", "Updated", "Created_function_id", "Updated_function_id", "Revision", "TrangThai")

modelSchema = ModelSchema()
modelsSchema = ModelSchema(many = True)

#Benh
class Benh(db.Model):
    Id_B = db.Column(db.Integer, primary_key=True)
    Ten_B = db.Column(db.String(100))
    ThongTin_B = db.Column(db.String(500))
    CachChuaTri = db.Column(db.String(500))
    GhiChu = db.Column(db.String(500))
    Created = db.Column(db.DateTime, default = datetime.utcnow)
    Updated = db.Column(db.DateTime, default = datetime.utcnow)
    Created_function_id = db.Column(db.String(20))
    Updated_function_id = db.Column(db.String(20))
    Revision = db.Column(db.Integer, default = 0)
    TrangThai = db.Column(db.Boolean, default = True)
    def __init__(self, Ten_B, ThongTin_B, CachChuaTri, GhiChu, Created, Updated, Created_function_id, Updated_function_id, Revision, TrangThai):
        self.Ten_B = Ten_B
        self.ThongTin_B = ThongTin_B
        self.CachChuaTri = CachChuaTri
        self.GhiChu = GhiChu
        self.Created = Created
        self.Updated = Updated
        self.Created_function_id = Created_function_id
        self.Updated_function_id = Updated_function_id
        self.Revision = Revision
        self.TrangThai = TrangThai

class BenhSchema(ma.Schema):
    class Meta:
        fields = ("Id_B", "Ten_B", "ThongTin_B", "CachChuaTri", "GhiChu", "Created", "Updated", "Created_function_id", "Updated_function_id", "Revision", "TrangThai")

benhSchema = BenhSchema()
benhsSchema = BenhSchema(many = True)

#Model
class ModelBenh(db.Model):
    Id_MB = db.Column(db.Integer, primary_key = True)
    Id_M = db.Column(db.Integer, db.ForeignKey("model.Id_M"))
    Id_B = db.Column(db.Integer, db.ForeignKey("benh.Id_B"))
    STT = db.Column(db.Integer)
    Created = db.Column(db.DateTime, default = datetime.utcnow)
    Updated = db.Column(db.DateTime, default = datetime.utcnow)
    Created_function_id = db.Column(db.String(20))
    Updated_function_id = db.Column(db.String(20))
    Revision = db.Column(db.Integer, default = 0)
    TrangThai = db.Column(db.Boolean, default = True)
    def __init__(self, Id_M, Id_B, STT, Created, Updated, Created_function_id, Updated_function_id, Revision, TrangThai):
        self.Id_M = Id_M
        self.Id_B = Id_B
        self.STT = STT
        self.Created = Created
        self.Updated = Updated
        self.Created_function_id = Created_function_id
        self.Updated_function_id = Updated_function_id
        self.Revision = Revision
        self.TrangThai = TrangThai

class ModelBenhSchema(ma.Schema):
    class Meta:
        fields = ("Id_MB", "Id_M", "Id_B", "STT", "Created", "Updated", "Created_function_id", "Updated_function_id", "Revision", "TrangThai")

modelBenhSchema = ModelBenhSchema()
modelBenhsSchema = ModelBenhSchema(many = True)

#Nhan dien
class NhanDien(db.Model):
    Id_ND = db.Column(db.Integer, primary_key = True)
    DiaChiAnh = db.Column(db.String(200))
    ThoiGian_ND = db.Column(db.DateTime, default = datetime.utcnow)
    Email = db.Column(db.String(100))
    Id_B = db.Column(db.Integer, db.ForeignKey("benh.Id_B"))
    YKien = db.Column(db.String(500))
    Created = db.Column(db.DateTime, default = datetime.utcnow)
    Updated = db.Column(db.DateTime, default = datetime.utcnow)
    Created_function_id = db.Column(db.String(20))
    Updated_function_id = db.Column(db.String(20))
    Revision = db.Column(db.Integer, default = 0)
    TrangThai = db.Column(db.Boolean, default = True)
    def __init__(self, DiaChiAnh, Email, Id_B, YKien, Created, Updated, Created_function_id, Updated_function_id, Revision, TrangThai):
        self.DiaChiAnh = DiaChiAnh
        self.Email = Email
        self.Id_B = Id_B
        self.YKien = YKien
        self.Created = Created
        self.Updated = Updated
        self.Created_function_id = Created_function_id
        self.Updated_function_id = Updated_function_id
        self.Revision = Revision
        self.TrangThai = TrangThai

class NhanDienSchema(ma.Schema):
    class Meta:
        fields = ("Id_ND", "DiaChiAnh", "ThoiGian_ND", "Email", "Id_B", "YKien", "Created", "Updated", "Created_function_id", "Updated_function_id", "Revision", "TrangThai")

nhanDienSchema = NhanDienSchema()
nhanDiensSchema = NhanDienSchema(many = True)