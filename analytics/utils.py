import logging
from django.db.models import Count, Case, When

logger = logging.getLogger("secondary")

def aggregate_ticket_count(qs, flag: bool = None) -> int:
    if flag == None:
        qs_count = qs.aggregate(ticket_number=Count("branch_room__tenantroom__tenant_concern"))
        return qs_count["ticket_number"]

    qs_count = qs.aggregate(ticket_number=Count(
        Case(
            When(
                branch_room__tenantroom__tenant_concern__is_answered=flag, then=1      
            )
        )
    ))
    return qs_count["ticket_number"]


def annotate_ticket_count(qs, id: int, flag: bool = None):
    if flag == None:
        qs_count = qs.annotate(ticket_number=Count("branch_room__tenantroom__tenant_concern"))
        try:
            return qs_count.get(id=id).ticket_number 
        except Exception as err:
            return 0

    qs_count = qs.annotate(ticket_number=Count(
        Case(
            When(
                branch_room__tenantroom__tenant_concern__is_answered=flag, then=1
            )
        )
    ))
    try:
        return qs_count.get(id=id).ticket_number
    except Exception as err:
        return 0

