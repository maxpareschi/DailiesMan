import os
import json
import subprocess
from lib import processors as dmp
from lib import operators as dmo
from lib import renderers as dmr


if __name__ == "__main__":

    os.environ["OCIO"] = "D:/DEV/dailiesman/vendor/ocioconfig/OpenColorIOConfigs/aces_1.2/config.ocio"

    effect = "D:/DEV/DailiesMan/data/reviewSetupMain.json"

    ctp = dmp.ColorTransformProcessor()

    ctp.read_from_file(effect)

    # rtp = dmp.RepoTransformProcessor()
    # rtp.add_transform(
    #     dmo.RepoTransformData(**{
    #         "translate": [0.0, 0.0],
    #         "rotate": 30.0,
    #         "scale": [0.7, 0.7],
    #         "center": [1920.0, 1080.0]
    #     }),
    #     dmo.RepoTransformData(**{
    #         "translate": [20.0, 1000.0],
    #         "rotate": -45.0,
    #         "scale": [1.2, 1.2],
    #         "center": [226.0, 964.0]
    #     }),
    #     dmo.RepoTransformData(**{
    #         "translate": [200.0, -100.0],
    #         "rotate": 86.0,
    #         "scale": [0.55, 0.55],
    #         "center": [100.0, 1080.0]
    #     })
    # )
    # 
    # ctp = dmp.ColorTransformProcessor(
    #     temp_config_path = "D:/DEV/dailiesman/resources/test01/temp_config.ocio"
    # )
    # ctp.add_transform(
    #     dmo.ColorFileTransformData(**{
    #         "cccId": "",
    #         "direction": 0,
    #         "src": "D:/DEV/dailiesman/resources/test02/reviewSetup/reviewSetupMain/v000/resources/Linear_to_LogC4.spi1d"
    #     }),
    #     dmo.ColorFileTransformData(**{
    #         "cccId": "",
    #         "direction": 0,
    #         "src": "D:/DEV/dailiesman/resources/test02/reviewSetup/reviewSetupMain/v000/resources/ATH301_013_010.cc"
    #     }),
    #     dmo.ColorFileTransformData(**{
    #         "cccId": "",
    #         "direction": 0,
    #         "src": "D:/DEV/dailiesman/resources/test02/reviewSetup/reviewSetupMain/v000/resources/Athena_S3_Rec709.cube"
    #     })
    # )
    # 
    # bp = dmp.BurninsProcessor(
    #     text_data = dmo.BurninsTextData(**{
    #         "top_left": "Top Left",
    #         "top_center": "Top Center",
    #         "top_right": "Top Right",
    #         "bottom_left": "Bottom Left",
    #         "bottom_center": "Bottom Center",
    #         "bottom_right": "Bottom Right"
    #     }),
    #     options = dmo.BurninsPresetData(**{
    #         "font": "bahnschrift",
    #         "text_color": "1,1,1,1",
    #         "bg_color": "0,0,0,0.5",
    #         "text_size": 50,
    #         "text_padding": 5,
    #         "margin_x": 10,
    #         "margin_y": 10
    #     })
    # )
    # 
    # r = dmr.DefaultRenderer(
    #     oiio_path = "D:/DEV/dailiesman/vendor/oiio/windows",
    #     ffmpeg_path = "D:/DEV/dailiesman/vendor/ffmpeg/windows/bin",
    #     repo_transform = rtp,
    #     color_transform = ctp,
    #     burnins = bp
    # )

    # r.render_oiio(
    #     "D:/DEV/dailiesman/resources/test01/source.exr",
    #     "D:/DEV/dailiesman/resources/test01/result_new.png"
    # )