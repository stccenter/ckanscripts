#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 21:44:37 2017
1. GDAL has to be installed through "brew install gdal"
2. remember to change the orgnization name and auth key
Reference: http://blog.csdn.net/theonegis/article/details/54427906
https://gis.stackexchange.com/questions/201061/python-gdal-api-transformosr-coordinatetransformation
@author: yjiang
"""
import json
import os
import math
from osgeo import osr
try:  
    from osgeo import gdal  
    from osgeo import ogr  
except:    
    import gdal  
    import ogr 
    
# 为了支持中文路径，请添加下面这句代码  
gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","NO")  
# 为了使属性表字段支持中文，请添加下面这句  
gdal.SetConfigOption("SHAPE_ENCODING","") 
# 注册所有的驱动  
ogr.RegisterAll()   

#read raster metadata (.img, .tiff)
def read_img(filename):
    
    metadata = {}
    dataset=gdal.Open(filename)       

    im_width = dataset.RasterXSize    #栅格矩阵的列数
    im_height = dataset.RasterYSize   #栅格矩阵的行数
    metadata["width"] = im_width
    metadata["height"] = im_height

    im_geotrans = dataset.GetGeoTransform()  #仿射矩阵
#==============================================================================
#     adfGeoTransform[0] /* 左上角 x */
#     adfGeoTransform[1] /* 东西方向一个像素对应的距离 */
#     adfGeoTransform[2] /* 旋转, 0表示上面为北方 */
#     adfGeoTransform[3] /* 左上角 y */
#     adfGeoTransform[4] /* 旋转, 0表示上面为北方 */
#     adfGeoTransform[5] /* 南北方向一个像素对应的距离 */
#==============================================================================
    im_proj = dataset.GetProjection() #地图投影信息
    metadata["geotransform"] = im_geotrans
    metadata["projection"] = im_proj

    
    im_metadata = dataset.GetDriver().GetMetadata()
    im_driverDes = dataset.GetDriver().GetDescription()
    
    metadata["content"] = im_metadata
    metadata["driver"] = im_driverDes
    
    cor1 = geo2lonlat(dataset, im_geotrans[0], im_geotrans[3])
    print(cor1)
    cor2 = geo2lonlat(dataset, im_geotrans[0]+im_width*im_geotrans[1], im_geotrans[3]+im_height*im_geotrans[5])
    
    metadata["im_Extent"] = [cor1[0], cor1[1], cor2[0], cor2[1]]
    del dataset 
    return metadata

# read vector metadata (.shp)
def read_shp(filename):
    dataset = ogr.Open(filename, 0) 
    metadata = {}    
    # 获取该数据源中的图层个数，一般shp数据图层只有一个，如果是mdb、dxf等图层就会有多个
    shp_layerNum = dataset.GetLayerCount()
    shp_featureNum = dataset.GetLayer(0).GetFeatureCount()
    shp_geoExtent = dataset.GetLayer(0).GetExtent()
    
    shp_metadata = dataset.GetDriver().GetMetadata()
    shp_driverDes = dataset.GetDriver().GetDescription()
    
    metadata["layerNum"] = shp_layerNum
    metadata["featureNum"] = shp_featureNum
    metadata["shp_Extent"] = shp_geoExtent
    metadata["content"] = shp_metadata
    metadata["driver"] = shp_driverDes   
  
    del dataset
    return metadata

# filePath = '/Users/yjiang/Downloads/poi/poi.shp'
# print(read_img(filePath))
# print(read_shp(filePath))

def geo2lonlat(dataset, x, y):
    '''
    将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param x: 投影坐标x
    :param y: 投影坐标y
    :return: 投影坐标(x, y)对应的经纬度坐标(lon, lat)
    '''
    # CGCS2000_GK_CM_105E. 4507
    in_pro = osr.SpatialReference()
    in_pro.ImportFromEPSG(4507)
    # WGS84 projection reference
    out_pro = osr.SpatialReference()
    out_pro.ImportFromEPSG(4326)
    ct = osr.CoordinateTransformation(in_pro, out_pro)
    coords = ct.TransformPoint(x, y)
    return coords[:2]

try:
    filePath = '/Users/yjiang/Downloads/tiffdata/2938.50-528.00.tif'
    fileName = os.path.splitext(filePath)[0]
    metadata = read_img(filePath)

    dataset_dict = {}
    dataset_dict['name'] = fileName
    dataset_dict['owner_org'] = 'nasa-cmr' #lower case
    dataset_dict['title'] = fileName
    dataset_dict['id'] = fileName    

    extra_dict = []
     
    for key in metadata:
        entry = {}
        entry['key'] = str(key)
        entry['value'] = str(metadata[key])
        extra_dict.append(entry)

        if key == 'im_Extent':

            coor_list = []  
            box_list2 = metadata['im_Extent']

            geo_dict = {}
            geo_dict['type'] = 'Polygon'
            point_list = []
            point_list.append([box_list2[1],box_list2[0]])
            point_list.append([box_list2[3],box_list2[0]])
            point_list.append([box_list2[3],box_list2[2]])
            point_list.append([box_list2[1],box_list2[2]])
            point_list.append([box_list2[1],box_list2[0]])

            coor_list.append(point_list)
            geo_dict['coordinates'] = coor_list

            new_extra = {}
            new_extra['key'] = 'spatial'
            new_extra['value'] = json.dumps(geo_dict)

            extra_dict.append(new_extra)
            
        if key == 'shp_Extent':

            coor_list = []  
            box_list2 = metadata['shp_Extent']

            geo_dict = {}
            geo_dict['type'] = 'Polygon'
            point_list = []
            point_list.append([box_list2[2],box_list2[0]])
            point_list.append([box_list2[3],box_list2[0]])
            point_list.append([box_list2[3],box_list2[1]])
            point_list.append([box_list2[2],box_list2[1]])
            point_list.append([box_list2[2],box_list2[0]])

            coor_list.append(point_list)
            geo_dict['coordinates'] = coor_list

            new_extra = {}
            new_extra['key'] = 'spatial'
            new_extra['value'] = json.dumps(geo_dict)

            extra_dict.append(new_extra)
            
    dataset_dict['extras'] = extra_dict


#==============================================================================
#     # Use the json module to dump the dictionary to a string for posting.
#     data_string = json.dumps(dataset_dict)
# 
#     # We'll use the package_create function to create a new dataset.
#     request = urllib2.Request(
#     'https://199.26.254.168/api/3/action/package_create')
# 
#     # Creating a dataset requires an authorization header.
#     request.add_header('Authorization', '309e66f0-e23b-476b-8f27-b8a44e2c144e')
#     response = urllib2.urlopen(request, data_string)
#     assert response.code == 200
#==============================================================================

except Exception as e:
    print(e)        

   
