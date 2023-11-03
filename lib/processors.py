from __future__ import annotations

import os
import re
import math
import json

import PyOpenColorIO as OCIO

from .base import DMBaseClass
from .operators import (
    EffectFileData,
    BurninsTextData,
    BurninsPresetData,
    RepoTransformData
)


class EffectsFileProcessor(DMBaseClass):

    def __init__(self, **kwargs) -> None:
        self.input_file: str = None
        # self.search_values: 
        self.operations: list[EffectFileData] = list()
        super().__init__(**kwargs)

    def load(self, file: str = None) -> None:
        if file:
            self.input_file = file
        if self.input_file:
            with open(self.input_file, "r") as f:
                data = json.load(f)
                print(json.dumps(data, indent=4, default=str))
                print(data)
        else:
            print("NO FILE!")


class BurninsProcessor(DMBaseClass):

    def __init__(self, **kwargs) -> None:
        self.text_data: BurninsTextData = BurninsTextData()
        self.options: BurninsPresetData = BurninsPresetData()
        super().__init__(**kwargs)

    def set_text(self, **kwargs) -> None:
        self.text_data.set_data(**kwargs)

    def set_options(self, **kwargs) -> None:
        self.options.set_data(**kwargs)

    def compute_single_burnin_cmd(self,
                                  text: str = None,
                                  text_position: str = "top_left") -> list:
        if text_position not in vars(self.text_data):
            raise ValueError(
                f"'{text_position}' is not a valid position. Please "
                "check the available positions in BurninsTextOp class."
            )
        if not text:
            text = getattr(self.text_data, text_position)
        align_y, align_x = text_position.split("_")
        pos_x = self.options.margin_x + self.options.text_padding
        pos_y = self.options.margin_y + self.options.text_padding
        box_size = "".join([
            f"{{IMG[1].x-{self.options.text_padding}}},",
            f"{{IMG[1].y-{self.options.text_padding}}},",
            f"{{IMG[1].x+IMG[1].width+{self.options.text_padding}}},",
            f"{{IMG[1].y+IMG[1].height+{self.options.text_padding}}}"
        ])
        if align_x == "center":
            pos_x = f"{{TOP.width/2}}"
        elif align_x == "right":
            pos_x = f"{{TOP.width-{self.options.margin_x + self.options.text_padding}}}"
        if align_y == "bottom":
            pos_y = f"{{TOP.height}}"
        text_cmd = "".join([
            "--text",
            f":x={pos_x}",
            f":y={pos_y}",
            f":font={self.options.font}",
            f":color={self.options.text_color}",
            f":size={self.options.text_size}",
            f":xalign={align_x}",
            f":yalign={align_y}",
        ])
        cmd = [
            "--create", self.options.resolution, "4",
            text_cmd,
            text,
            "--trim",
            "--create", self.options.resolution, "4",
            f"--box:color={self.options.bg_color}:fill=1",
            box_size,
            "--over",
            "--label", f"{align_y}_{align_x}",
            "--trim"
        ]
        return cmd

    def compute_burins_cmd(self,
                           text: BurninsTextData = None) -> list:
        if not text:
            text = self.text_data.get_data()
        cmd = []
        for i, k in enumerate(text.keys()):
            if text[k]:
                cmd.extend(self.compute_single_burnin_cmd(
                    text_position = k
                ))
                if i > 0:
                    cmd.extend(["burnin", "--over"])
                cmd.extend(["--label", "burnin"])
        return cmd


class ColorTransformProcessor(DMBaseClass):
    
    def __init__(self, **kwargs) -> None:
        self.transform_list: list = list()
        self.context: str = "dailiesman_context"
        self.working_space: str = "data"
        self.config_path: str = os.environ.get("OCIO", "")
        self.temp_config_path: str = ""
        super().__init__(**kwargs)

    def add_transform(self, *args) -> None:
        for arg in args:
            class_name = re.search(r"(?<=Color)(.*)(?=Data)", arg.__class__.__name__)
            if class_name:
                ocio_class = getattr(OCIO, class_name.group(0))
                kwargs = arg.get_data()
                if kwargs.get("index"):
                    kwargs.pop("index")
                kwargs["direction"] = OCIO.TransformDirection.TRANSFORM_DIR_FORWARD
                if kwargs["direction"] == 1:
                    kwargs["direction"] = OCIO.TransformDirection.TRANSFORM_DIR_INVERSE
                transform = ocio_class(**kwargs)
                self.transform_list.append(transform)
            else:
                raise TypeError(
                    "Wrong Object passed to internal list!\n",
                    "Allowed objects are: \n",
                    "\t- operators.ColorFileTransformData\n",
                    "\t- operators.ColorDisplayViewTransformData\n")
    
    def clear_transforms(self) -> None:
        self.transform_list = []
    
    def create_ocio_config(self,
                           source: str = None,
                           dest: str = None) -> str:
        if not source:
            source = self.config_path
        if not dest:
            dest = self.temp_config_path
        view_name = f"{self.context} (Look)"
        config = OCIO.Config.CreateFromFile(source)
        search_paths = []
        search_paths.append(
            os.path.join(
                os.path.dirname(self.config_path),
                "luts"
            ).replace("\\", "/")
        )
        for ctd in self.transform_list:
            ctd_source = ctd.getSrc()
            if ctd_source:
                search_paths.append(
                    os.path.dirname(ctd_source).replace("\\", "/")
                )
        group = OCIO.GroupTransform(self.transform_list)
        look = OCIO.Look(
            name = self.context,
            processSpace = self.working_space,
            transform = group
        )
        config.addLook(look)
        config.addDisplayView(
            "ACES",
            view_name,
            "Utility - Raw",
            looks = self.context
        )
        # config.setActiveViews(f"{config.getActiveViews()},{view_name}")
        config.setActiveViews(f"{view_name},sRGB,Rec.709,Log,Raw")
        search_paths = list(dict.fromkeys(search_paths))
        for sp in search_paths:
            config.addSearchPath(sp)
        config.validate()
        config.serialize(dest)
        return dest

    def compute_color_cmd(self,
                          colorconfig: str = None,
                          from_colorspace: str = None,
                          to_colorspace: str = None,
                          context: str = None) -> list:
        if not colorconfig:
            colorconfig = self.temp_config_path
        if not from_colorspace:
            from_colorspace = "data"
        if not to_colorspace:
            to_colorspace = "data"
        if not context:
            context = self.context
        cmd = ["--colorconfig"]
        cmd.append(colorconfig)
        cmd.append(f"--ociolook:from={from_colorspace}:to={to_colorspace}")
        cmd.append(context)
        return cmd


class RepoTransformProcessor(DMBaseClass):

    def __init__(self, **kwargs) -> None:
        self.transform_list: list[RepoTransformData] = list()
        self.source_width: int = 3840
        self.source_height: int = 2160
        self.dest_width: int = 1920
        self.dest_height: int = 1080
        self.fillmode: str = "width"
        self._raw_matrix: list[list[float]] = list()
        super().__init__(**kwargs)

    def get_raw_matrix(self) -> list[list[float]]:
        return self._raw_matrix

    def add_transform(self, *args) -> None:
        for arg in args:
            self.transform_list.append(arg)

    def clear_transforms(self) -> None:
        self.transform_list = []

    def zero_matrix(self) -> list[list[float]]:
        return [[0.0 for i in range(3)] for j in range(3)]

    def identity_matrix(self) -> list[list[float]]:
        return self.translate_matrix([0.0, 0.0])

    def translate_matrix(self, t: list[float]) -> list[list[float]]:
        return [
            [1.0, 0.0, t[0]],
            [0.0, 1.0, t[1]],
            [0.0, 0.0, 1.0]
        ]

    def rotate_matrix(self, r: float) -> list[list[float]]:
        rad = math.radians(r)
        cos = math.cos(rad)
        sin = math.sin(rad)
        return [
            [cos, -sin, 0.0],
            [sin, cos, 0.0],
            [0.0, 0.0, 1.0]
        ]

    def scale_matrix(self, s: list[float]) -> list[list[float]]:
        return [
            [s[0], 0.0, 0.0],
            [0.0, s[1], 0.0],
            [0.0, 0.0, 1.0]
        ]

    def mirror_matrix(self, x: bool = False) -> list[list[float]]:
        dir = [1.0, -1.0] if not x else [-1.0, 1.0]
        return self.scale_matrix(dir)

    def mult_matrix(self,
                    m1: list[list[float]],
                    m2: list[list[float]]) -> list[list[float]]:
        return [[sum(a * b for a, b in zip(m1_row, m2_col)) for m2_col in zip(*m2)] for m1_row in m1]

    def mult_matrix_vector(self,
                           m: list[list[float]],
                           v: list[float]) -> list[float]:
        result = [0.0, 0.0, 0.0]
        for i in range(len(m)):
            for j in range(len(v)):
                result[i] += m[i][j] * v[j]
        return result

    def flip_matrix(self, w: float) -> list[list[float]]:
        result = self.identity_matrix()
        chain = [
            self.translate_matrix([w, 0.0]),
            self.mirror_matrix(x = True)
        ]
        for m in chain:
            result = self.mult_matrix(result, m)
        return result

    def flop_matrix(self, h: float) -> list[list[float]]:
        result = self.identity_matrix()
        chain = [
            self.translate_matrix([0.0, h]),
            self.mirror_matrix()
        ]
        for m in chain:
            result = self.mult_matrix(result, m)
        return result

    def transpose_matrix(self, m: list[list[float]]) -> list[list[float]]:
        res = self.identity_matrix()
        for i in range(len(m)):
            for j in range(len(m[0])):
                res[i][j] = m[j][i]
        return res

    def matrix_to_44(self, m: list[list[float]]) -> list[list[float]]:
        result = m
        result[0].insert(2, 0.0)
        result[1].insert(2, 0.0)
        result[2].insert(2, 0.0)
        result.insert(2, [0.0, 0.0, 1.0, 0.0])
        return result

    def matrix_to_list(self, m: list[list[float]]) -> list[float]:
        result = []
        for i in m:
            for j in i:
                result.append(str(j))
        return result

    def matrix_to_csv(self,
                      m: list[list[float]]) -> str:
        l = []
        for i in m:
            for k in i:
                l.append(str(k))
        return ",".join(l)

    def matrix_to_cornerpin(self,
                            m: list[list[float]],
                            origin_upperleft: bool = True) -> list:
        w = self.source_width
        h = self.source_height
        cornerpin = []
        if origin_upperleft:
            corners = [[0, h, 1], [w, h, 1], [0, 0, 1], [w, 0, 1]]
        else:
            corners = [[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]]
        transformed_corners = [self.mult_matrix_vector(m, corner) for corner in corners]
        transformed_corners = [[corner[0] / corner[2], corner[1] / corner[2]] for corner in transformed_corners]
        for i, corner in enumerate(transformed_corners):
            x, y = corner
            cornerpin.extend([x,y])
        return cornerpin

    def get_matrix(self,
                   t: list[float],
                   r: float,
                   s: list[float],
                   c: list[float]) -> list[list[float]]:
        c_inv = [-c[0], -c[1]]
        center = self.translate_matrix(c)
        center_inv = self.translate_matrix(c_inv)
        translate = self.translate_matrix(t)
        rotate = self.rotate_matrix(r)
        scale = self.scale_matrix(s)
        result = self.mult_matrix(translate, center)
        result = self.mult_matrix(result, scale)
        result = self.mult_matrix(result, rotate)
        result = self.mult_matrix(result, center_inv)
        return result  

    def get_matrix_chained(self,
                           flip: bool = False,
                           flop: bool = True,
                           reverse_chain: bool = True) -> str:
        chain = []
        tlist = self.transform_list
        if reverse_chain:
            tlist.reverse()
        if flip:
            chain.append(self.flip_matrix(self.source_width))
        if flop:
            chain.append(self.flop_matrix(self.source_height))
        for xform in tlist:
            chain.append(
                self.get_matrix(
                    xform.translate,
                    xform.rotate,
                    xform.scale,
                    xform.center)
            )
        if flop:
            chain.append(self.flop_matrix(self.source_height))
        if flip:
            chain.append(self.flip_matrix(self.source_width))
        result = self.identity_matrix()
        for m in chain:
            result = self.mult_matrix(result, m)
        self._raw_matrix = result
        return result

    def get_cornerpin_data(self, matrix: list[list[float]]) -> list:
        cp = self.matrix_to_cornerpin(
            matrix,
            self.source_width,
            self.source_height,
            origin_upperleft=False
        )
        return cp

    def get_repotransform_cmd(self) -> list:
        matrix = self.get_matrix_chained()
        matrix_tr = self.transpose_matrix(matrix)
        warp_cmd = self.matrix_to_csv(matrix_tr)
        cmd = []
        cmd.append("--warp:filter=cubic")
        cmd.append(warp_cmd)
        cmd.append("--fit:pad=1:filter=cubic:fillmode={}".format(self.fillmode))
        cmd.append("{}x{}".format(self.dest_width, self.dest_height))
        return cmd


class SettingsProcessor(DMBaseClass):
    def __init__(self, **kwargs):
        self.settings_file: str = ""
        self.burnins_presets: dict = dict()
        self.compression_presets: dict = dict()
        self.resolution_presets: dict = dict()
        self.letterbox_presets: dict = dict()
        self.slate_presets: dict = dict()
        self.review_profiles: dict = dict()
        super().__init__(**kwargs)

    def read_settings_from_file(self, file: str) -> None:
        pass
        """
        NOT IMPLEMENTED
        """

