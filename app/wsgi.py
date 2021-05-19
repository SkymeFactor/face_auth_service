from service_locator import ServiceLocator
from utils.app_builder import AppBuilder

builder = AppBuilder()
locator = ServiceLocator()

builder.create_services(locator)
app = builder.create_flask(locator.cfg_manager)

if __name__ == '__main__':
    app.run(
        host=locator.cfg_manager.flask_address,
        port=locator.cfg_manager.flask_port
    )
