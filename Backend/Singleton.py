from abc import ABC


class Singleton(ABC):
    '''
    abstract singleton class

    .. note::
        Please note there are parent-child dependencies when you inherit from this class. After creating an instance of
        the parent class instantiating his child classes will return a instance of the parent class. Already
        instantiated child classes are not affected.

    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        '''
        main implementation of the singleton logic

        This methode returns the instance of the class to be created. Then the :meth:`__init__` methode
        is called. To prevent :meth:`__init__` from running every time an already existing instance is requested
        this methode will set an pseudo init methode as :meth:`__init__`. The pseudo init method replaces itself
        with the real :meth:`__init__` afterwards.
        :param args:
        :param kwargs:
        '''
        print(args, kwargs)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        else:
            _original_init = getattr(cls, "__init__")

            def _pseudo_init(self, *_, **__):
                # set original __init__
                setattr(self.__class__, "__init__", _original_init)

            setattr(cls, "__init__", _pseudo_init)
        return cls._instance
