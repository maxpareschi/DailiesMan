class DMBaseClass:
    
    def __init__(self, **kwargs) -> None:
        self.set_data(**kwargs)
    
    def set_data(self, **kwargs) -> None:
        props = vars(self)
        for k, v in kwargs.items():
            if k in props:
                self.__setattr__(k, v)
            else:
                raise KeyError(
                    f"Cannot set '{k}' key on this object!"
                )
    
    def get_data(self) -> dict:
        return dict(vars(self))