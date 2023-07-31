from .base import DMBaseClass


class RepoTransformData(DMBaseClass):
    def __init__(self, **kwargs) -> None:
        self.translate: list[float] = [0.0, 0.0]
        self.rotate: float = 0.0
        self.scale: list[float] = [0.0, 0.0]
        self.center: list[float] = [0.0, 0.0]
        super().__init__(**kwargs)


class ColorFileTransformData(DMBaseClass):
    def __init__(self, **kwargs) -> None:
        self.src: str = ""
        self.cccId: str = "0"
        self.direction: int = 0
        super().__init__(**kwargs)


class ColorDisplayViewTransformData(DMBaseClass):
    def __init__(self, **kwargs) -> None:
        self.src: str = "data"
        self.display: str = "ACES"
        self.view: str = "Rec.709"
        self.direction: int = 0
        super().__init__(**kwargs)


class BurninsTextData(DMBaseClass):
    def __init__(self, **kwargs) -> None:
        self.top_left: str = None
        self.top_center: str = None
        self.top_right: str = None
        self.bottom_left: str = None
        self.bottom_center: str = None
        self.bottom_right: str = None
        super().__init__(**kwargs)


class BurninsPresetData(DMBaseClass):
    def __init__(self, **kwargs):
        self.name:str = "default_burnin"
        self.resolution: str = "1920x1080"
        self.font: str = "bahnschrift"
        self.text_color: str = "1,1,1"
        self.bg_color: str = "0,0,0,0"
        self.text_size: int = 50
        self.text_padding: int = 5
        self.margin_x: int = 10
        self.margin_y: int = 10
        super().__init__(**kwargs)


class CompressionPresetData(DMBaseClass):
    def __init__(self, **kwargs):
        self.name: str = "dnxhd36"
        self.extension: str = "mov"
        self.input_args: list = [
                "-apply_trc bt709"
        ]
        self.output_args: list = [
                "-c:v dnxhd",
                "-b:v 36M",
                "-pix_fmt yuv422p"
        ]
        super().__init__(**kwargs)


class ResolutionPresetData(DMBaseClass):
    def __init__(self, **kwargs):
        self.name: str = "HD"
        self.width: int = 1920
        self.height: int = 1080
        self.fillmode: str = "width"
        self.pixel_aspect: float = 1.0
        super().__init__(**kwargs)


class LetterboxPresetData(DMBaseClass):
    def __init__(self, **kwargs):
        self.name: str = "default_letterbox"
        self.bg_color: str = "0,0,0,1"
        self.aspect: float = 2.39
        self.line_width: int = 0
        self.line_color: str = "0,0,0,0"
        super().__init__(**kwargs)


class SlatePresetData(DMBaseClass):
    def __init__(self, **kwargs):
        self.name: str = "default_slate"
        self.template_path: str = "",
        self.resources_path: str = ""
        super().__init__(**kwargs)


class ReviewProfileData(DMBaseClass):
    def __init__(self, **kwargs):
        self.name: str = "dnxhd"
        self.tags: list = ["color", "repo", "slate", "burnin"]
        self.burnin_preset: str = "profile_01"
        self.compression_preset: str = "dnxhd"
        self.resolution_preset: str = "HD"
        self.letterbox_preset: str = "2.39"
        self.slate_preset: str = "base_slate"
        super().__init__(**kwargs)