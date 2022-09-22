from django.shortcuts import render
from django.http import HttpResponse
import logging

logger = logging.getLogger("main")


def index_page(request):
    logger.info("Rendered index page")
    return HttpResponse("Rendered Correctly")
