from urllib import parse
import cv2
import numpy as np
import os
import csv
import pickle
import zipfile
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from datetime import date, datetime, timedelta
from server import app, db
from server.models import Admins, adminSchema, adminsSchema, Model, modelSchema, modelsSchema, Benh, benhSchema, benhsSchema, ModelBenh, modelSchema, modelsSchema, ModelBenh, modelBenhSchema, modelBenhsSchema, NhanDien, nhanDienSchema, nhanDiensSchema

vectors_file = [("training_set_dom_den.csv", 0), ("training_set_dom_trang.csv", 1), ("training_set_den_mang.csv", 0), 
("training_set_hoai_tu_co.csv", 1), ("training_set_hoai_tu_gan.csv", 0), ("training_set_tom_bt.csv", 2)]
kmeans = []

print(cv2.__version__)

for File, clr in vectors_file:
    data = pd.read_csv(f"./server/vector_surf_tom/{File}")
    #k-means clusters with 4    
    kmean = KMeans(n_clusters=4, random_state=0).fit(data.values)
    kmeans.append((kmean, clr))

def detect_tom_desease(img, Ten_M):
    surf = cv2.xfeatures2d.SURF_create(5000)

    with open(f"./server/models/{Ten_M}.pickle", "rb") as file:
        clf = pickle.load(file)

        image = cv2.imread(os.path.join("./server/img", img))
        image = cv2.resize(image, (256, 128))

        _, des = surf.detectAndCompute(image,None)

        ans = []

        for i in range(len(kmeans)):
            rs = kmeans[i][0].predict(des)
            data = []
            for j in range(len(des)):
                if rs[j] == kmeans[i][1]:
                    data.append(des[j])
            if len(data) > 0:
                pre = clf.predict(data)
                dect = int(np.argmax(np.bincount(pre.astype(int))))
                if(dect == i):
                    ans.append(dect)

        if len(ans) > 0:
            return ans[0]
        return -1

#Get query from DB
def get_queries(request):
    return dict(parse.parse_qsl(parse.urlsplit(request.url).query))

#Insert model bệnh
def insertMB(Id_M, Id_B, STT,TrangThai):
    insertModelBenh = ModelBenh(Id_M=Id_M, Id_B=Id_B, STT=STT, Created=datetime.now(
    ), Updated=datetime.now(), Created_function_id="api008", Updated_function_id="api008", Revision=0, TrangThai=TrangThai)
    db.session.add(insertModelBenh)
    db.session.commit()

#Delete model bệnh
def deleteMB(Id_M):
    Id_M = ModelBenh.query.filter_by(Id_M=Id_M).delete()
    db.session.commit()

#Print bệnh list
def format_benhs_list(arr):
    res = []
    for benh in arr:
        if benh["TrangThai"]:
            feature = {
                "Id_B": benh["Id_B"],
                "Ten_B": benh["Ten_B"],
                "ThongTin_B": benh["ThongTin_B"],
                "CachChuaTri": benh["CachChuaTri"],
                "GhiChu": benh["GhiChu"],
                "Created": benh["Created"],
                "Updated": benh["Updated"],
                "Created_function_id": benh["Created_function_id"],
                "Updated_function_id": benh["Updated_function_id"],
                "Revision": benh["Revision"],
                "TrangThai": benh["TrangThai"]
            }
            res.append(feature)
    return res

#Print nhận diện list
def format_nhandiens_list(arr):
    res = []
    for nhandien in arr:
        if nhandien["TrangThai"]:
            feature = {
                "Id_ND": nhandien["Id_ND"],
                "Id_B": nhandien["Id_B"],
                "Ten_B": Benh.query.filter_by(Id_B=nhandien["Id_B"]).first().Ten_B,
                "ImgName": nhandien["DiaChiAnh"],
                "ThoiGian_ND": nhandien["ThoiGian_ND"],
                "Email": nhandien["Email"],
                "YKien": nhandien["YKien"],
                "Created": nhandien["Created"],
                "Updated": nhandien["Updated"],
                "Created_function_id": nhandien["Created_function_id"],
                "Updated_function_id": nhandien["Updated_function_id"],
                "Revision": nhandien["Revision"],
                "TrangThai": nhandien["TrangThai"]
            }

            res.append(feature)   
    return res

#Print model benh list
def format_modelbenhs_list(arr):
    res = []
    print(arr)
    for ModelBenh in arr:
        if ModelBenh["TrangThai"]:
            feature = {
                "Id_B": ModelBenh["Id_B"],
                "Ten_B": Benh.query.filter_by(Id_B=ModelBenh["Id_B"]).first().Ten_B, 
                "STT": ModelBenh["STT"],  
            }
            res.append(feature)
    return res

#Print model list
def format_models_list(arr):
    res = []
    for Model in arr:
        if Model["TrangThai"]:
            feature = {
                "Id_M": Model["Id_M"],
                "Ten_M": Model["Ten_M"],
                "Created": Model["Created"],
                "Updated": Model["Updated"],
                "Created_function_id": Model["Created_function_id"],
                "Updated_function_id": Model["Updated_function_id"],
                "Revision": Model["Revision"],
                "TrangThai": Model["TrangThai"],
                "ModelBenhList": format_modelbenhs_list(modelBenhsSchema.dump(ModelBenh.query.filter_by(Id_M=Model["Id_M"])))
            }
            res.append(feature)
    return res

#get array query
def filter_arr_by_queries(arr, queries):
    spKey = ["Id_B", "Id_M", "Id_ND"]
    ingKey = ["Updated_datefrom", "Updated_dateto"]
    def filter_by_query(item):
        rs = True
        for key, value in queries.items():
            if key in spKey:
                rs = rs and (str(item[key]) == value)
            elif key in ingKey:
                continue
            else:
                rs = rs and (value in str(item[key]))
        return rs
    listFilter = list(filter(filter_by_query, arr))
    return listFilter

