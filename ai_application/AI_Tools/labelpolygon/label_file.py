import base64
import contextlib
import io
import json
import os
import os.path as osp
import math
import cv2
from collections import OrderedDict

import PIL.Image

from ai_application.AI_Tools.labelpolygon import __version__
from ai_application.AI_Tools.labelpolygon.logger import logger
from ai_application.AI_Tools.labelpolygon import PY2
from ai_application.AI_Tools.labelpolygon import QT4
from ai_application.AI_Tools.labelpolygon import utils


PIL.Image.MAX_IMAGE_PIXELS = None


@contextlib.contextmanager
def open(name, mode):
    assert mode in ["r", "w"]
    if PY2:
        mode += "b"
        encoding = None
    else:
        encoding = "utf-8"
    yield io.open(name, mode, encoding=encoding)
    return


class LabelFileError(Exception):
    pass


class LabelFile(object):

    suffix = ".json"

    def __init__(self, filename=None):
        self.shapes = []
        self.imagePath = None
        self.imageData = None
        if filename is not None:
            self.load(filename)
        self.filename = filename

    @staticmethod
    def load_image_file(filename):
        try:
            image_pil = PIL.Image.open(filename)
        except IOError:
            logger.error("Failed opening image file: {}".format(filename))
            return

        # apply orientation to image according to exif
        image_pil = utils.apply_exif_orientation(image_pil)

        with io.BytesIO() as f:
            ext = osp.splitext(filename)[1].lower()
            if PY2 and QT4:
                format = "PNG"
            elif ext in [".jpg", ".jpeg"]:
                format = "JPEG"
            else:
                format = "PNG"
            image_pil.save(f, format=format)
            f.seek(0)
            return f.read()

    def load(self, filename):
        keys = [
            "version",
            "imageData",
            "imagePath",
            "shapes",  # polygonal annotations
            "flags",  # image level flags
            "imageHeight",
            "imageWidth",
        ]
        shape_keys = [
            "label",
            "points",
            "group_id",
            "shape_type",
            "flags",
        ]
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            version = data.get("version")
            if version is None:
                logger.warning(
                    "Loading JSON file ({}) of unknown version".format(
                        filename
                    )
                )
            elif version.split(".")[0] != __version__.split(".")[0]:
                logger.warning(
                    "This JSON file ({}) may be incompatible with "
                    "current labelme. version in file: {}, "
                    "current version: {}".format(
                        filename, version, __version__
                    )
                )

            if data["imageData"] is not None:
                imageData = base64.b64decode(data["imageData"])
                if PY2 and QT4:
                    imageData = utils.img_data_to_png_data(imageData)
            else:
                # relative path from label file to relative path from cwd
                imagePath = osp.join(osp.dirname(filename), data["imagePath"])
                imageData = self.load_image_file(imagePath)
            flags = data.get("flags") or {}
            imagePath = data["imagePath"]
            self._check_image_height_and_width(
                base64.b64encode(imageData).decode("utf-8"),
                data.get("imageHeight"),
                data.get("imageWidth"),
            )
            shapes = [
                dict(
                    label=s["label"],
                    points=s["points"],
                    shape_type=s.get("shape_type", "polygon"),
                    flags=s.get("flags", {}),
                    group_id=s.get("group_id"),
                    other_data={
                        k: v for k, v in s.items() if k not in shape_keys
                    },
                )
                for s in data["shapes"]
            ]
        except Exception as e:
            raise LabelFileError(e)

        otherData = {}
        for key, value in data.items():
            if key not in keys:
                otherData[key] = value

        # Only replace data after everything is loaded.
        self.flags = flags
        self.shapes = shapes
        self.imagePath = imagePath
        self.imageData = imageData
        self.filename = filename
        self.otherData = otherData

    @staticmethod
    def _check_image_height_and_width(imageData, imageHeight, imageWidth):
        img_arr = utils.img_b64_to_arr(imageData)
        if imageHeight is not None and img_arr.shape[0] != imageHeight:
            logger.error(
                "imageHeight does not match with imageData or imagePath, "
                "so getting imageHeight from actual image."
            )
            imageHeight = img_arr.shape[0]
        if imageWidth is not None and img_arr.shape[1] != imageWidth:
            logger.error(
                "imageWidth does not match with imageData or imagePath, "
                "so getting imageWidth from actual image."
            )
            imageWidth = img_arr.shape[1]
        return imageHeight, imageWidth

    def save(
        self,
        filename,
        shapes,
        imagePath,
        imageHeight,
        imageWidth,
        imageData=None,
        otherData=None,
        flags=None,
    ):
        if imageData is not None:
            imageData = base64.b64encode(imageData).decode("utf-8")
            imageHeight, imageWidth = self._check_image_height_and_width(
                imageData, imageHeight, imageWidth
            )
        if otherData is None:
            otherData = {}
        if flags is None:
            flags = {}
        data = dict(
            version=__version__,
            flags=flags,
            shapes=shapes,
            imagePath=imagePath,
            imageData=imageData,
            imageHeight=imageHeight,
            imageWidth=imageWidth
        )
        for key, value in otherData.items():
            assert key not in data
            data[key] = value
        try:
            with open(filename, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.filename = filename
        except Exception as e:
            raise LabelFileError(e)

        save_location_path = ""
        save_path = str(filename).split("/")
        for i in range(len(save_path) - 1):
            save_location_path = save_location_path + save_path[i] + "/"

        Yolo_Data = ""
        list_load_labelname, Exiting_file = self.Classes(save_location_path + "classes.txt")

        Filnal_YoloDataList = []
        NewYolo_String = ""
        
        if not os.path.isfile(save_location_path + imagePath[0:-3] + "txt"):
            for j in range(len(shapes)):
                if len(list_load_labelname) > 0:
                    # is_label = False
                    # for n in range(len(list_load_labelname)):
                    #     if str(shapes[j]['label']) == list_load_labelname[n]:
                    #         Yolo_Data = Yolo_Data + str(n) + " "
                    #         is_label = True
                    #         break

                    # if is_label == False:
                    #     Yolo_Data = Yolo_Data + str(len(list_load_labelname)) + " "
                    #     list_load_labelname.append(str(shapes[j]['label']))

                    index_label_name = str(shapes[j]['label'])
                    # print("index_label_name :", index_label_name)
                    index_classes = list_load_labelname.index(index_label_name)
                    # print("index classes: ", index_classes)

                    Yolo_Data = str(index_classes) + " "
                else:
                    Yolo_Data = Yolo_Data + str(j) + " "

                for l in range(len(shapes[j]['points'])):
                    p1 = (shapes[j]['points'][l][1]/imageHeight)*imageWidth
                    imgHeight = str(float(round(p1, 6))/imageWidth)
                    Yolo_Data = Yolo_Data + str(float(round(shapes[j]['points'][l][0], 6))/imageWidth) + " " + imgHeight + " "
                p2 = (shapes[j]['points'][0][1]/imageHeight)*imageWidth
                imgHeight2 = str(float(round(p2, 6))/imageWidth)
                Yolo_Data = Yolo_Data + str(float(round(shapes[j]['points'][0][0], 6))/imageWidth) + " " + imgHeight2
                if not Exiting_file:
                    Yolo_Data = Yolo_Data + "\n"

                Filnal_YoloDataList.append(Yolo_Data)

                # print("Filnal YoloDataDict:", Filnal_YoloDataList)  

            # Re Arrange new Yolo Data before wirte to data.txt
            for i in range(len(Filnal_YoloDataList)):
                NewYolo_String = NewYolo_String + str(Filnal_YoloDataList[i]) + "\n"

            print()
            print("NewYolo_String:\n", NewYolo_String)

            with open(save_location_path + imagePath[0:-3] + "txt", 'w') as f:
                f.writelines(str(NewYolo_String[0:-1]))

        # ************************************************************
        # Save Classet.txt Here
        if os.path.isfile(save_location_path + "classes.txt"):
            with open(save_location_path + "classes.txt", 'w') as f:
                result_classes = ""
                for line in list_load_labelname:
                    result_classes = result_classes + line + "\n"
                
                f.write(result_classes[0:-1])
        else:
            label_name = ""
            for k in range(len(shapes)):
                label_name = label_name + str(shapes[k]['label']) + "\n"

            with open(save_location_path + "classes.txt", 'w') as f:
                f.writelines(str(label_name[0:-1]))

    @staticmethod
    def is_label_file(filename):
        return osp.splitext(filename)[1].lower() == LabelFile.suffix

    def Classes(self, location_path_filename=None):

        label_name = ""
        list_labelname = []
        Exiting_file = False
        if os.path.isfile(location_path_filename):
            Exiting_file = True
            with open(location_path_filename,'r') as classet_file:
                label_name = classet_file.read()
                list_labelname = label_name.split("\n")
                if '' in list_labelname:
                    list_labelname.remove('')

        return list_labelname, Exiting_file
    
