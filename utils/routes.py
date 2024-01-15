from app_routes import errors, file_io
from app_routes.applications import dz_stats, dz_nmf, dz_cmd, dz_mix


def register(app):
    dz_cmd.register(app)
    dz_nmf.register(app)
    dz_mix.register(app)
    dz_stats.register(app)

    errors.register(app)
    file_io.register(app)
