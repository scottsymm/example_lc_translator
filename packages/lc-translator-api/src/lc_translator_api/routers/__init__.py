"""Router aggregation."""

from lc_translator_api.routers.generate import router as generate_router
from lc_translator_api.routers.records import router as records_router
from lc_translator_api.routers.translate import router as translate_router
from lc_translator_api.routers.validate import router as validate_router

__all__ = ["generate_router", "records_router", "translate_router", "validate_router"]
