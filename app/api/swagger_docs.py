from flask import Blueprint, render_template, jsonify
from service_locator import ServiceLocator

bp_docs = Blueprint('docs', __name__)

@bp_docs.route('/swagger-ui', methods=['GET'])
def get_swagger():
    # Render swagger-ui page
    url_prefix = ServiceLocator().cfg_manager.flask_protocol + "://" + ServiceLocator().cfg_manager.host_address
    return render_template(
        template_name_or_list='swaggerui.html',
        css=f'{url_prefix}/static/css/swagger-ui.css',
        fav32=f'{url_prefix}/static/img/favicon-32x32.png',
        fav16=f'{url_prefix}/static/img/favicon-16x16.png',
        bundle_js=f'{url_prefix}/static/js/swagger-ui-bundle.js',
        standalone_preset_js=f'{url_prefix}/static/js/swagger-ui-standalone-preset.js',
        swagger_json=f'{url_prefix}/static/swagger.json'
    )