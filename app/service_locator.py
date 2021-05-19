
class ServiceLocator(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ServiceLocator, cls).__new__(cls)
        return cls.instance

    # Instantiate by call
    def __call__(self,
        cfg_manager,
        token_manager,
        client_manager,
        user_manager
    ):
        self.cfg_manager = cfg_manager
        self.token_manager = token_manager
        self.client_manager = client_manager
        self.user_manager = user_manager
    
    # Protect from failing when service not found
    def __getattr__(self, attribute: str):
        return None