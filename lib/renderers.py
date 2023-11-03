from __future__ import annotations

import os
import subprocess

from .base import DMBaseClass
from .processors import (
    BurninsProcessor,
    ColorTransformProcessor,
    RepoTransformProcessor,
    SettingsProcessor
)

class DefaultRenderer(DMBaseClass):

    def __init__(self, **kwargs):
        self.oiio_path: str = ""
        self.ffmpeg_path: str = ""
        self.burnins: BurninsProcessor = None
        self.color_transform: ColorTransformProcessor = None
        self.repo_transform: RepoTransformProcessor = None
        self.settings: SettingsProcessor = None
        super().__init__(**kwargs)

    def render_oiio(self,
                    source: str,
                    dest: str,
                    debug: bool = False) -> str:
        if self.oiio_path:
            os.environ["PATH"] = os.environ["PATH"] + os.pathsep + self.oiio_path
        if self.ffmpeg_path:
            os.environ["PATH"] = os.environ["PATH"] + os.pathsep + self.ffmpeg_path
        cmd = ["oiiotool"]
        cmd.append(source)
        if self.repo_transform:
            cmd.extend(self.repo_transform.get_repotransform_cmd())
        if self.color_transform:
            self.color_transform.create_ocio_config()
            cmd.extend(self.color_transform.compute_color_cmd())
        if self.color_transform or self.repo_transform:
            cmd.extend(["--ch", "R,G,B,A=1.0"])
            cmd.extend(["--label", "image"])
        if self.burnins:
            cmd.extend(self.burnins.compute_burins_cmd())
            if self.color_transform or self.repo_transform:
                cmd.extend(["image", "--over"])
        cmd.extend(["--ch", "R,G,B,A=1.0"])
        if debug:
            cmd.extend(["--debug", "-v"])
        cmd.extend(["-o", dest])
        subprocess.run(cmd)

    def render_repo_ffmpeg(src_path: str,
                           dest_path: str,
                           cornerpin: list,
                           in_args: list = None,
                           out_args: list = None,
                           resolution: str = None,
                           debug: str = "error") -> str:
        """
        Construct the ffmpeg commanline with arguments.
        Returns the rendered file path.
        NEEDS ffmpeg in PATH. will not work otherwise!
        """
        if not resolution:
            resolution = "1920x1080"
        width, height = resolution.split("x")
        cmd = ["ffmpeg"]
        cmd.extend(["-y", "-loglevel", debug, "-hide_banner"])
        if in_args:
            cmd.extend(in_args)
        cmd.extend(["-i", src_path])
        cmd.extend(["-vf", ",".join([
                #"pad=(in_w+2):(in_h+2):1:1:eval=init",
                "perspective={}:{}:{}:{}:{}:{}:{}:{}:{}".format(
                    cornerpin[0], cornerpin[1],
                    cornerpin[2], cornerpin[3],
                    cornerpin[4], cornerpin[5],
                    cornerpin[6], cornerpin[7],
                    "sense=destination:eval=init"
                ),
                #"crop=(in_w-2):(in_h-2)",
                f"scale={width}:-1",
                f"crop={width}:{height}"
            ])
        ])
        if out_args:
            cmd.extend(out_args)
        cmd.append(dest_path)

        # render using oiio in a subprocess
        subprocess.run(cmd)

        return dest_path