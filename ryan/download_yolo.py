from roboflow import Roboflow
rf = Roboflow(api_key="JKeSXyTNdvUIJDdThDP3")
project = rf.workspace("ece4191-gq5mw").project("tennis-ball-detection-qtrus")
version = project.version(2)
dataset = version.download("yolov9")