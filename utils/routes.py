from app_routes import errors, file_io
from app_routes.pages import dz_stats, dz_nmf, dz_cmd


def register(app):
    dz_cmd.register(app)
    file_io.register(app)
    dz_nmf.register(app)
    dz_stats.register(app)
    errors.register(app)