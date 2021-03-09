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

vectors_file = [("training_set_dom_den.csv", 0), ("training_set_dom_trang.csv", 1), ("training_set_den_mang.csv", 0), 
("training_set_hoai_tu_co.csv", 1), ("training_set_hoai_tu_gan.csv", 0), ("training_set_tom_bt.csv", 2)]
kmeans = []

for File, clr in vectors_file:
    data = pd.read_csv(f"./vector_surf_tom/{File}")
    #k-means clusters with 4    
    kmean = KMeans(n_clusters=4, random_state=0).fit(data.values)
    kmeans.append((kmean, clr))
def detect_tom_desease(img, Ten_M):
    surf = cv2.xfeatures2d.SURF_create(5000)

    with open(f"./models/{Ten_M}.pickle", "rb") as file:
        clf = pickle.load(file)

        image = cv2.imread(os.path.join("./img", img))
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

        print(ans)
        if len(ans) > 0:
            return ans[0]
        return -1
detect_tom_desease("DomTrang_01","Nhan_Dien_Benh_Tom1")