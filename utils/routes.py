from app_routes import errors, file_io
from app_routes.applications import dz_stats, project_editor, dz_mix


def register(app):
    dz_stats.register(app)
    project_editor.register(app)
    dz_mix.register(app)

    errors.register(app)
    file_io.register(app)
