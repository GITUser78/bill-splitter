"""Shared Jinja2 template environment for all routers.

Having a single place that builds the environment means filters (like
`currency` below) and settings (like disabling the template cache) only
need to be defined once and are guaranteed to be consistent across pages
and API fragment responses.
"""

import os
import jinja2
from starlette.templating import Jinja2Templates

from . import config

templates_dir = os.path.join(os.path.dirname(__file__), "templates")

# Disable caching to avoid Jinja2 cache key errors
loader = jinja2.FileSystemLoader(templates_dir)
env = jinja2.Environment(loader=loader, cache_size=0)
env.filters["currency"] = lambda value: f"{config.CURRENCY_SYMBOL}{value:.2f}"

templates = Jinja2Templates(directory=templates_dir)
templates.env = env
