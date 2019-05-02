from tenant.models import (TblAgent,
                           TblAgentAllocation,
                           TblMasterProperty,
                           TblMasterPropertyClone,
                           TblProperty,
                           TblPropertyAllocation,
                           TblRentCollection,
                           TblTenant,
                           TblVisit
                           )
from django.db.models import (Prefetch,
                              Count,
                              Sum,
                              Subquery,
                              OuterRef,
                              F,
                              Q,
                              prefetch_related_objects,
                              ExpressionWrapper,
                              CharField,
                              functions,
                              Value,
                              Sum
                              )
from django.db.models.functions import Cast, Concat, TruncMonth
from datetime import datetime, timedelta


##########################################################################
# Admin side
##########################################################################

def totalactiveAgent():
    return TblAgent.objects.filter(is_staff=True, is_superuser=False).count()

def yesterday_visit():
        return TblVisit.objects.filter(vs_date=datetime.now()-timedelta(days=1)).count()

def totalproperties():
        return TblProperty.objects.filter(pr_is_active=True).count()

def allocated_properties():
        return TblProperty.objects.filter(pr_is_active=True,pr_is_allocated=True).count()

def free_property():
        return TblProperty.objects.filter(pr_is_active=True,pr_is_allocated=False).count()
       
def total_tenants():
        return TblTenant.objects.filter(~Q(tn_status=0),tn_is_active=True).count()

def free_agents():
        return TblAgentAllocation.objects.filter(~(Q()))
