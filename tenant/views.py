from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib.auth.decorators import login_required
from django.core.paginator import (EmptyPage,
                                   PageNotAnInteger,
                                   Paginator)
from django.shortcuts import (HttpResponseRedirect,
                              render,
                              HttpResponse,
                              redirect,)
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import reverse
from tenant.decorators import (for_admin,
                               for_staff)
from tenant.forms import (AgentForm,
                          TenantRegistratonForm)
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
from django.db.models.functions import (Cast,
                                        Concat,
                                        TruncMonth,
                                        Coalesce,
                                        )
from datetime import (datetime,
                      timedelta,
                      )
import time
# from django.db.models.lookups import

# Create your views here.


#######################################################################################################################
# Basic views
#######################################################################################################################

# index view
def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            print('\n\nlogout\n\n')
            logout(request)
    return render(request, 'Base.html')


# Requesting agent registration
def agent_registration(request):
    form = AgentForm()
    if request.method == 'POST':
        form = AgentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                agent = form.save(commit=False)
                agent.date_joined = request.POST.get('date_joined')
                agent.set_password(agent.password)
                agent.agent_save()
                return index(request)
            except Exception as e:
                print("Error:", e)
                print(form.errors)
        else:
            print(form.errors)
    return render(request, 'AgentRegistration.html', {'form': form})


# custom login for admin/agent
def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user:
        if user.is_superuser:
            # print("\n\n\n\n Admin \n",user,"\n\n\n")
            login(request, user)
            return HttpResponseRedirect(reverse(admin_index))
        elif user.is_staff:
            # print("\n\n\n\n Agent \n",user,"\n\n\n")
            login(request, user)
            return HttpResponseRedirect(reverse(agent_index))
        else:
            # print("\n\n\n\nInavlid user\n\n\n\n")
            return render(request, 'Base.html')
    else:
        # print("\n\n\n\nInavlid user\n\n\n\n")
        return render(request, 'Base.html')


#######################################################################################################################
# Common in admin and agent
#######################################################################################################################


def notify(msg=str, code="success", url=str):
    response = "<script>\
                    console.log('notification');\
                    localStorage.setItem('Status', '"+msg+"');\
                    localStorage.setItem('code','"+code+"');\
                    location.href = '"+url +\
        "';</script>"
    return HttpResponse(response)

# adding tenant by agent
# @login_required
# def add_tenant(request):
#     form = TenantRegistratonForm()
#     if request.method == 'POST':
#         form = TenantRegistratonForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 tenant = form.save(commit=False)
#                 tenant.tn_agent = request.user
#                 tenant.tn_joining_date = request.POST.get('date_joined')

#                 tenant.save()
#                 return index(request)
#             except Exception as e:
#                 print("Error:", e)
#                 print(form.errors)
#         else:
#             print(form.errors)

#     return render(request, 'agent/add_tenant.html', {'form': form})


#######################################################################################################################
# Admin site views
#######################################################################################################################

# Admin index view
@for_admin
def admin_index(request):
    msp_list = TblMasterProperty.objects.all()\
        .annotate(
            no_of_clones=Count('tblmasterpropertyclone',
                               distinct=True))\
        .annotate(
            unallocated_clones=Count(
                'tblmasterpropertyclone', distinct=True,
                filter=Q(
                    tblmasterpropertyclone__cln_is_allocated=False)))\
        .annotate(
            allocated_clones=Count(
                'tblmasterpropertyclone', distinct=True,
                filter=Q(
                    tblmasterpropertyclone__cln_is_allocated=True)))\
        .annotate(
            no_of_property=Count(
                'tblmasterpropertyclone__tblproperty'))\
        .annotate(
            unallocated_properties=Count(
                'tblmasterpropertyclone__tblproperty',
                filter=Q(
                    tblmasterpropertyclone__tblproperty__pr_is_allocated=False)))\
        .annotate(
            allocated_properties=Count(
                'tblmasterpropertyclone__tblproperty',
                filter=Q(
                    tblmasterpropertyclone__tblproperty__pr_is_allocated=True)))

    # yearly_rent = TblMasterProperty.objects\
    #     .filter(msp_is_active=True,
    #             pk__in=TblRentCollection.objects\
    #             .select_related('rc_allocation__pa_property__pr_master__cln_master')
    #             .filter(rc_pay_off_date__lt=datetime.now()
    #                     + timedelta(days=365)).values(
    #                 'rc_allocation__pa_property__pr_master__cln_master__id'))\
    #             .annotate(month=TruncMonth('rc_pay_off_date'))\
    #             .values('month')\
    #             .annotate(sum=Sum('rc_allocation__pa_final_rent'))\
    #             .values('msp_name', 'month', 'sum')

    allinfo = dict()

    allinfo.update({'total_active_agents': TblAgent.objects.filter(
        is_staff=True,
        is_superuser=False,
        is_active=True).count()})
    allinfo.update({'yesterdays_visit': TblVisit.objects.filter(
        vs_date=datetime.now()-timedelta(days=1))
        .count()})
    allinfo.update({'totalproperties': TblProperty.objects.filter(
        pr_is_active=True).count()})
    allinfo['free_property'] = TblProperty.objects.filter(
        pr_is_active=True, pr_is_allocated=False).count()
    allinfo['total_tenants'] = TblTenant.objects.filter(
        ~Q(tn_status=0), tn_is_active=True).count()
    allinfo['free_agents'] = TblAgent.objects.exclude(
        Q(id__in=TblAgentAllocation.objects.all()
          .values_list('al_agent', flat=True))
        | Q(is_superuser=True) | Q(is_active=False)).count()
    allinfo['agent_requests'] = TblAgent.objects.filter(
        is_staff=False, is_active=False, is_superuser=False).count()
    allinfo['unmanaged_tenantlist'] = TblTenant.objects.filter(
        tn_agent=request.user).count()
    # print("\n\n\n\n",allinfo)

    # rent = TblRentCollection.objects\
    #     .select_related('rc_allocation__pa_property__pr_master__cln_master')\
    #     .filter(rc_pay_off_date__lt=datetime.now()
    #             + timedelta(days=365))\
    #     .annotate(month=TruncMonth('rc_pay_off_date'))\
    #     .values('month')\
    #     .annotate(sum=Sum('rc_allocation__pa_final_rent'))\
    #     .annotate(msp=F('rc_allocation__pa_property__pr_master__cln_master__msp_name'))\
    #     .order_by('month')\
    #     .values('msp', 'month', 'sum')

    # rent backup
    # now = time.localtime()
    # months = [time.localtime(
    #     time.mktime(
    #         (now.tm_year,
    #          now.tm_mon - n,
    #           1, 0, 0, 0, 0, 0, 0)
    #     )
    # )[:2] for n in range(12)]
    # rent = []
    # for month in months:
    #     data = TblMasterProperty.objects.all()\
    #         .annotate(sum=Sum(
    #             'tblmasterpropertyclone__tblproperty__' +
    #             'tblpropertyallocation__tblrentcollection__' +
    #             'rc_allocation__pa_final_rent',
    #             filter=Q(
    #                 Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=month[1]),
    #                 Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=month[0])
    #             )
    #         )
    #     ).values('msp_name','sum')
    #     rent.append({
    #         'month': datetime.strptime(
    #             '01-'+str(month[1])+'-'+str(month[0]),
    #             '%d-%m-%Y'
    #         ),
    #         'rent': data})

    now = time.localtime()
    months = [time.localtime(
        time.mktime(
            (now.tm_year,
             now.tm_mon - n,
              1, 0, 0, 0, 0, 0, 0)
        )
    )[:2] for n in range(12)]
    months.sort()
    # rent = []
    # for month in months:
    #     data = TblMasterProperty.objects.all()\
    #         .annotate(sum=Sum(
    #             'tblmasterpropertyclone__tblproperty__' +
    #             'tblpropertyallocation__tblrentcollection__' +
    #             'rc_allocation__pa_final_rent',
    #             filter=Q(
    #                 Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=month[1]),
    #                 Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=month[0])
    #             )
    #         )
    #     ).values('msp_name','sum')
    #     rent.append({
    #         'month': datetime.strptime(
    #             '01-'+str(month[1])+'-'+str(month[0]),
    #             '%d-%m-%Y'
    #         ),
    #         'rent': data})

    # rent = TblMasterProperty.objects.all()\
    #     .annotate(sum=Sum(
    #         'tblmasterpropertyclone__tblproperty__' +
    #         'tblpropertyallocation__tblrentcollection__' +
    #         'rc_allocation__pa_final_rent'
    #     ))

    # rent = TblRentCollection.objects.all()\
    #     .annotate(month=F('rc_month'))

    # rent = []

    masterproperties = TblMasterProperty.objects.all()\
        .annotate(
            month1=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[0][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[0][0])
                    )
                ), 0
            ),

            month2=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[1][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[1][0])
                    )
                ), 0
            ),
            month3=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[2][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[2][0])
                    )
                ), 0
            ),
            month4=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[3][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[3][0])
                    )
                ), 0
            ),
            month5=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[4][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[4][0])
                    )
                ), 0
            ),
            month6=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[5][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[5][0])
                    )
                ), 0
            ),
            month7=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[6][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[6][0])
                    )
                ), 0
            ),
            month8=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[7][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[7][0])
                    )
                ), 0
            ),
            month9=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[8][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[8][0])
                    )
                ), 0
            ),
            month10=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[9][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[9][0])
                    )
                ), 0
            ),
            month11=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[10][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[10][0])
                    )
                ), 0
            ),
            month12=Coalesce(
                Sum(
                    'tblmasterpropertyclone__tblproperty__' +
                    'tblpropertyallocation__tblrentcollection__' +
                    'rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__month=months[11][1]),
                        Q(tblmasterpropertyclone__tblproperty__tblpropertyallocation__tblrentcollection__rc_month__year=months[11][0])
                    )
                ), 0
            )
    )

    # print(masterproperties.values())
    # for masterproperty in masterproperties.values():
    #     print(masterproperty)

    Agentvise_rent_data = TblAgent.objects.filter(
        is_superuser=False,
        is_active=True,
        is_staff=True)\
        .annotate(
            month1=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[0][1]),
                        Q(tblrentcollection__rc_month__year=months[0][0])
                    )
                    ), 0
            ),
            month2=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[1][1]),
                        Q(tblrentcollection__rc_month__year=months[1][0])
                    )
                    ), 0
            ),
            month3=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[2][1]),
                        Q(tblrentcollection__rc_month__year=months[2][0])
                    )
                    ), 0
            ),
            month4=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[3][1]),
                        Q(tblrentcollection__rc_month__year=months[3][0])
                    )
                    ), 0
            ),
            month5=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[4][1]),
                        Q(tblrentcollection__rc_month__year=months[4][0])
                    )
                    ), 0
            ),
            month6=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[5][1]),
                        Q(tblrentcollection__rc_month__year=months[5][0])
                    )
                    ), 0
            ),
            month7=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[6][1]),
                        Q(tblrentcollection__rc_month__year=months[6][0])
                    )
                    ), 0
            ),
            month8=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[7][1]),
                        Q(tblrentcollection__rc_month__year=months[7][0])
                    )
                    ), 0
            ),
            month9=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[8][1]),
                        Q(tblrentcollection__rc_month__year=months[8][0])
                    )
                    ), 0
            ),
            month10=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[9][1]),
                        Q(tblrentcollection__rc_month__year=months[9][0])
                    )
                    ), 0
            ),
            month11=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[10][1]),
                        Q(tblrentcollection__rc_month__year=months[10][0])
                    )
                    ), 0
            ),
            month12=Coalesce(
                Sum('tblrentcollection__rc_allocation__pa_final_rent',
                    filter=Q(
                        Q(tblrentcollection__rc_month__month=months[11][1]),
                        Q(tblrentcollection__rc_month__year=months[11][0])
                    )
                    ), 0
            ),
    )

    # agentwise_tenant_visit=TblAgent.objects.filter(
    #     is_superuser=False,is_active=True,
    #     is_staff=True)\
    #         .annotate(
    #             visits=\
    #                 Count('tbltenant__tblvisit__vs_tenant',
    #                 filter=Q(tbltenant__tblvisit__vs_date__gte=datetime.now()-timedelta(days=30)) 
    #             )
    #         )
    
    agentwise_tenant_intrest=TblAgent.objects.filter(
        is_superuser=False,is_active=True,
        is_staff=True)\
            .annotate(
                allvisits=\
                    Count('tbltenant__tblvisit__vs_tenant',
                    filter=Q(tbltenant__tblvisit__vs_date__gte=datetime.now()-timedelta(days=30)) 
                ),
                status1=\
                    Count('tbltenant__tblvisit__vs_tenant',
                    filter=Q(Q(tbltenant__tblvisit__vs_date__gte=datetime.now()-timedelta(days=30)) &
                    Q(tbltenant__tblvisit__vs_intrest_status=1))
                ),
                status2=\
                    Count('tbltenant__tblvisit__vs_tenant',
                    filter=Q(Q(tbltenant__tblvisit__vs_date__gte=datetime.now()-timedelta(days=30)) &
                    Q(tbltenant__tblvisit__vs_intrest_status=2))
                ),
                status3=\
                    Count('tbltenant__tblvisit__vs_tenant',
                    filter=Q(Q(tbltenant__tblvisit__vs_date__gte=datetime.now()-timedelta(days=30)) &
                    Q(tbltenant__tblvisit__vs_intrest_status=3))
                )
            )


    # print(agentwise_tenant_intrest.values('first_name','allvisits','status1','status2','status3'))

    # for masterproperty in masterproperties:
    #     data = TblRentCollection.objects\
    #         .filter(rc_pay_off_date__lt=datetime.now()
    #                 + timedelta(days=365),
    #                 rc_allocation__pa_property__pr_master__cln_master=masterproperty)\
    #         .annotate(month=TruncMonth('rc_pay_off_date'))\
    #         .values('month')\
    #         .annotate(rent=Sum('rc_allocation__pa_final_rent'))\
    #         .order_by('month')
    #         # print
    #     rent.append(
    #         {
    #             'msp':masterproperty.msp_name,
    #             # 'month':data.month,
    #             'rent':[data.values('rent')]
    #         }
    #     )

    # for r in rent:
    #     print(r)
    months_in_str = []
    for month in months:
        months_in_str.append(datetime.strptime(
            str(month[1])+','+str(month[0]), '%m,%Y').strftime('%b,%Y'))
    # print(months_in_str)
    return render(request, 'admin/index.html',
                  {'msp_list': msp_list,
                   'months': months_in_str,
                   'rent': masterproperties,
                   'agent_wise_rent': Agentvise_rent_data,
                   'agentwise_tenant_intrest':agentwise_tenant_intrest,
                   'allinfo': allinfo, })

# Page Agent Requests..................................................................................................
# view all agent requests on admin site

# @for_admin
# def makecharts(request):
#     NewTenantJoinThisMonth=DataPool(
#         series=[
#             {
#                 'options':{
#                     'source': TblTenant.objects.select_related('tn_agent').filter(tn_joining_date=datetime.now()-timedelta(days=30)).order_by('tn_agent_id')
#                 },
#                 'terms':[
#                     'tn_agent',
#                     'tn_name',
#                 ]
#             }
#             ])
#     cht=Chart(
#         datasource=NewTenantJoinThisMonth,
#         series_options=[{
#             'options':{
#                 'type':'line',
#                 'stacking':False
#             },'terms':{
#                 'tn_agent':['tn_name']
#             }
#         }],
#         chart_options={
#             'title':{'text':'New Tenant Registrations this month'},
#             'xAxis':{
#                 'title':'Number Of tenant'
#             }
#         }
#     )
#     return cht


@for_admin
def view_agent_request(request):
    # print('agents')
    try:
        # print('agents')
        agents = TblAgent.objects.filter(
            is_active=False, is_staff=False)\
            .order_by('first_name', 'last_name')

        print(agents)
    except Exception as e:
        print('Error at Agent Request', e)
        agents = None
    return render(request, 'admin/agent_requests.html',
                  {'agents': agents})

# accepting the agent request
@for_admin
def agent_request_accept(request):
    try:
        id = request.GET['id']
        agent = TblAgent.objects.get(id=id)
        agent.verified_save()
        return HttpResponse(1)
    except Exception as e:
        print('Error in agent request accept:', e)
        return HttpResponse(0)

# deleting the agent request@for_admin
@for_admin
def agent_request_reject(request):
    try:
        id = request.GET['id']
        TblAgent.objects.filter(id=id).delete()
        return HttpResponse(1)
    except Exception as e:
        print('Error in agent request reject', e)
        return HttpResponse(0)


# returning search result of agent requests.
def get_agents(starts_with=''):
    agents = []
    first_name = starts_with
    last_name = None
    if ' ' in starts_with:
        lst = starts_with.split(' ')
        first_name = lst[0]
        last_name = lst[1]

    if first_name:
        if last_name:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        last_name__istartswith=last_name,
                        is_active=False,
                        is_staff=False,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        else:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        is_active=False,
                        is_staff=False,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        print(agents)
    else:
        agents = TblAgent.objects\
            .filter(is_active=False,
                    is_staff=False,
                    is_superuser=False).order_by('first_name',
                                                 'last_name')
    return agents


# View the search result from agent requests
@for_admin
def agent_requests_search(request):
    agents = []
    starts_with = ''
    if request.method == 'GET':
        if 'suggestion' in request.GET.keys():
            starts_with = request.GET['suggestion']
        agents = get_agents(starts_with)

    return render(request, 'admin/agents.html', {'agents': agents, })


# End-Page Agent Requests...........................................................................................


# Page Agent View..................................................................................................
# view all agent requests on admin site
@for_admin
def view_agent_all(request):
    try:
        agents = TblAgent.objects.filter(
            is_staff=True, is_superuser=False).order_by('first_name',
                                                        'last_name')

    except Exception as e:
        agents = None
        print('Error at Agent Profile', e)
    return render(request, 'admin/agent_active.html',
                  {'agents': agents})


def update_tenant(tenant_list, to_agent):
    """ Updating Tenant from one agent to another agent"""
    try:
        for tenant in tenant_list:
            try:
                tenant.tn_agent = to_agent
                tenant.save()
            except Exception as e:
                temp_tenat = TblTenant.objects.get(
                    tn_agent=to_agent,
                    tn_contact=tenant.tn_contact)
                TblVisit.objects.filter(vs_tenant=tenant)\
                    .update(vs_tenant=temp_tenat)
                TblPropertyAllocation.objects\
                    .filter(pa_tenant=tenant)\
                    .update(pa_tenant=temp_tenat)
                tenant.delete()
        return True
    except Exception as e:
        print('Error at deallocation on tenant update :', e)
        return False

# activating deactivating agents status


@for_admin
def agent_action(request):
    agent = TblAgent.objects.get(id=request.GET['id'])
    act = request.GET['is_active']
    msg = 'Agent Activated Successfully.'
    code = 'success'
    if act == '0':
        msg = 'Agent Retired Successfully.'
        print('dealloacting all properties')
        try:
            allocation = TblAgentAllocation.objects\
                .select_related('al_master')\
                .filter(al_agent=request.GET['id'])
            print(allocation)
            for al in allocation:
                print(al.al_master.cln_alias)
                al.al_master.cln_is_allocated = False
                al.al_master.save()

            allocation.delete()
            tenants = TblTenant.objects.filter(tn_agent=agent)
            update_tenant(tenants, request.user)

        except Exception as e:
            print('Error at deallocation', e)
            msg = 'Something went wrong while retiring Agent.'
            code = 'error'

    agent.is_active = act
    agent.save()
    return notify(msg=msg, code=code, url=reverse(view_agent_all))


# returning search result of Active Agents.
def get_active_agents(starts_with=''):
    agents = []
    first_name = starts_with
    last_name = None
    if ' ' in starts_with:
        lst = starts_with.split(' ')
        first_name = lst[0]
        last_name = lst[1]

    if first_name:
        if last_name:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        last_name__istartswith=last_name,
                        is_staff=True,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        else:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        is_staff=True,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        print(agents)
    else:
        agents = TblAgent.objects\
            .filter(is_staff=True,
                    is_superuser=False).order_by('first_name',
                                                 'last_name')
    return agents


# View the search result from agent requests
@for_admin
def agent_active_search(request):
    agents = []
    starts_with = ''
    if request.method == 'GET':
        if 'suggestion' in request.GET.keys():
            starts_with = request.GET['suggestion']

        print("start", starts_with)
        agents = get_active_agents(starts_with)

    return render(request, 'admin/active_agents.html',
                  {'agents': agents, })

# End-Page Agent View..................................................................................................


# Page Agent profile View.......................................................................................
# Viewing the agent request in more detailed View
@for_admin
def agent_profile(request, tid):
    print("\n\n\n\n\n\n")

    agent = TblAgent.objects.get(id=tid)

    details = TblAgentAllocation.objects\
        .select_related('al_master')\
        .select_related('al_master__cln_master')\
        .filter(al_agent=agent)\
        .annotate(
            properties=Count('al_master__tblproperty')
        )\
        .annotate(
            unallocated=Count(
                'al_master__tblproperty',
                filter=Q(al_master__tblproperty__pr_is_allocated=False))
        )\
        .annotate(
            allocated=Count(
                'al_master__tblproperty',
                filter=Q(al_master__tblproperty__pr_is_allocated=True))
        )\
        .order_by(
            'al_master__cln_master__msp_name',
            'al_master__cln_alias',
            '-al_master__cln_is_master_clone'
        )
    # for detail in details:
    #     print("Master =", detail.al_master.cln_master.msp_name, end="\t")
    #     print("Clone =", detail.al_master.cln_alias, end="\t")
    #     print("Properties =", detail.properties, end="\t")
    #     print("Unallocated =", detail.unallocated, end="\t")
    #     print("Allocated =", detail.allocated, end="\n")

    return render(request, 'admin/agent_profile.html',
                  {'agent': agent, 'allocations': details})

# showing Allocation data of Agent


@for_admin
def show_data_agent(request):

    try:
        act = request.GET.get('act')
        id = request.GET.get('id')
        print(act)
        data = None
        if act == 'all_properties':
            data = TblProperty.objects\
                .filter(pr_master=id)\
                .order_by('pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)
        elif act == 'allocated_properties':

            data = TblPropertyAllocation.objects\
                .select_related('pa_tenant')\
                .select_related('pa_property')\
                .filter(pa_property__pr_master=id,
                        pa_property__pr_is_allocated=True,
                        pa_is_allocated=True)\
                .order_by('pa_property__pr_address')
            for d in data:
                print(d.pa_property.pr_master.cln_alias,
                      d.pa_property.pr_address, d.pa_tenant.tn_name)

        elif act == 'unallocated_properties':
            data = TblProperty.objects\
                .select_related('pr_master')\
                .filter(pr_master=id, pr_is_allocated=False)\
                .order_by('pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)

        print(data)

        return render(request, 'admin/show_data.html',
                      {'rows': data, 'act': act, 'msp': id})
    except Exception as e:
        print("error ", e)
        return HttpResponse('''<div  style="color: red;
                                align: right; width: max-content; " >
                                <right>Something Went Wrong While
                                Fetching Requested data</right></div>''')


# End-Page Agent View..................................................................................................


# Page Add Master Property View.......................................................................................
# Creating Clone Input boxes according to user input
def create_clone_list(request):
    no = request.GET['clone_no']
    if no == '':
        no = 0
    return render(request, 'admin/clone_input_list.html',
                  {'no': range(1, int(no)+1)})

# Adding Master Property with or without clone..


@for_admin
def add_master_property(request):
    if request.method == "POST":
        try:
            # Creating new or taking Existing
            #  object for master property.
            msp = TblMasterProperty.objects.\
                get_or_create(msp_name=request.POST['msp_name'],
                              msp_address=request.POST['msp_address'],
                              msp_description=request.
                              POST['msp_description'],
                              msp_is_active=True)
            # Condition to check if new row is created or not.
            if msp[1]:
                # Saving the object and creating
                # master clone if new row created.
                msp[0].new_save()
                if 'msp_have_clones' in request.POST.keys():
                    try:
                        no = int(request.POST['msp_clone_no'])
                    except:
                        no = 0
                    if request.POST['msp_have_clones']\
                            and no > 0 and no <= 50:
                        for n in range(1, no+1):
                            cln = TblMasterPropertyClone.objects\
                                .create(cln_alias=request.
                                        POST['msp_clone'+str(n)],
                                        cln_master=msp[0])
                            cln.save()
                return notify(msg='Master Property Added Successfully',
                              url=reverse(view_master_property))
            else:
                return notify(msg='Master Property Already exists.',
                              code='error',
                              url=reverse(add_master_property))

        except Exception as e:
            print("Error :", e)
    else:
        return render(request, 'admin/add_master_property.html')
# End-Page Add master property View.................................................................................

# Page Add Poperty View............................................................................................
# Showing clone list of selected property


@for_admin
def clone_list(request):
    if request.GET.get('unallocated'):
        clones = TblMasterPropertyClone.objects.filter(
            cln_master=request.GET['msp'],
            cln_is_allocated=False).order_by('id')
    else:
        clones = TblMasterPropertyClone.objects.filter(
            cln_master=request.GET['msp']).order_by('id')
    return render(request, 'admin/clone_list.html', {'clones': clones})


# Viewing master property at admin side
@for_admin
def view_master_property(request):
    msp_list = TblMasterProperty.objects.all()\
        .annotate(
            no_of_clones=Count('tblmasterpropertyclone',
                               distinct=True))\
        .annotate(
            unallocated_clones=Count(
                'tblmasterpropertyclone', distinct=True,
                filter=Q(
                    tblmasterpropertyclone__cln_is_allocated=False)))\
        .annotate(
            allocated_clones=Count(
                'tblmasterpropertyclone', distinct=True,
                filter=Q(
                    tblmasterpropertyclone__cln_is_allocated=True)))\
        .annotate(
            no_of_property=Count(
                'tblmasterpropertyclone__tblproperty'))\
        .annotate(
            unallocated_properties=Count(
                'tblmasterpropertyclone__tblproperty',
                filter=Q(
                    tblmasterpropertyclone__tblproperty__pr_is_allocated=False)))\
        .annotate(
            allocated_properties=Count(
                'tblmasterpropertyclone__tblproperty',
                filter=Q(
                    tblmasterpropertyclone__tblproperty__pr_is_allocated=True)))

    # msp_list = ViewMasterProperties.objects.all()
    return render(request, 'admin/master_property_view.html',
                  {'master_property_list': msp_list})


# Adding new property in the database
@for_admin
def add_property(request):
    address_list = TblMasterProperty.objects.all()
    existing_addresses = []
    addeed_addresses = []
    if request.method == "POST":
        # A function to check if property alredy exists
        def is_property_exists(msp=None, add=None):
            is_exists = False
            clones = TblMasterPropertyClone.objects\
                .filter(cln_master=msp)
            for clone in clones:
                if TblProperty.objects\
                    .filter(pr_master=clone,
                            pr_address=add).exists():
                    is_exists = True
                    break
            return is_exists

        msp_id = request.POST['pr_msp']
        msp_clone_id = request.POST['pr_msp_clone']
        num = request.POST['pr_num']
        pr_rent = request.POST['pr_rent']
        pr_deposite = request.POST['pr_deposite']
        pr_description = request.POST['pr_description']
        msp = TblMasterProperty.objects.get(id=msp_id)
        msp_clone = TblMasterPropertyClone.objects.get(id=msp_clone_id)
        for n in range(int(num)):
            if 'pr_address'+str(n) in request.POST.keys():
                pr_address = request.POST['pr_address'+str(n)]
                if not is_property_exists(msp=msp, add=pr_address):
                    try:
                        obj = TblProperty.objects.\
                            create(pr_master=msp_clone,
                                   pr_address=pr_address,
                                   pr_rent=float(
                                       pr_rent),
                                   pr_deposite=float(
                                       pr_deposite),
                                   pr_description=pr_description,
                                   pr_is_active=True,
                                   pr_is_allocated=False)
                        obj.save()
                        addeed_addresses.append(pr_address)
                    except Exception as e:
                        print("\n\n\n\nError:", e)
                else:
                    existing_addresses.append(pr_address)
        if existing_addresses:
            context = ",".join(existing_addresses) +\
                " are alredy existing in <b><u>" + \
                msp.msp_name+"</u></b> Master Property."
        else:
            context = ''
        if addeed_addresses:
            success = ",".join(addeed_addresses) +\
                " are added in <b><u>"+msp_clone.cln_alias + \
                "</b></u> clone of <b><u>"+msp.msp_name +\
                "<b></u> Master Property."
        else:
            success = "No Property added to <b><u>" +\
                msp_clone.cln_alias + \
                "</u></b> clone of <b><u>"+msp.msp_name +\
                "</u></b> Master Property."
        return render(request, 'admin/add_property.html',
                      {'address_list': address_list,
                       'context': context,
                       'success': success})

    return render(request, 'admin/add_property.html',
                  {'address_list': address_list})
# End-Page Add property View.................................................................................

# Page View MAster Property.................................................................................
# showing data on admin page


@for_admin
def show_data(request):

    try:
        act = request.GET.get('act')
        id = request.GET.get('id')
        print(act)
        data = None
        if act == 'all_clones':
            data = TblMasterPropertyClone.objects.filter(cln_master=id)\
                .annotate(
                    properties=Count('tblproperty',
                                     Subquery(
                                         TblProperty.objects.filter(
                                             pr_master=OuterRef('pk')
                                         ).values('pr_master')
                                     )
                                     )
            ).order_by('-cln_is_master_clone', 'cln_alias')
            for d in data:
                print(d.properties)
        elif act == 'allocated_clones':
            data = TblAgentAllocation.objects\
                .select_related('al_agent')\
                .select_related('al_master')\
                .filter(al_master__cln_master=id,
                        al_master__cln_is_allocated=True
                        ).order_by(
                    '-al_master__cln_is_master_clone',
                    'al_master__cln_alias')

            for d in data:
                print(d.al_agent.username, d.al_master.cln_alias)
        elif act == 'unallocated_clones':
            data = TblMasterPropertyClone.objects\
                .filter(cln_master=id,
                        cln_is_allocated=False)\
                .order_by('-cln_is_master_clone', 'cln_alias')

            for d in data:
                print(d.cln_alias)
        elif act == 'all_properties':
            data = TblProperty.objects\
                .select_related('pr_master')\
                .filter(pr_master__cln_master=id)\
                .order_by('-pr_master__cln_is_master_clone',
                          'pr_master__cln_alias',
                          'pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)
        elif act == 'allocated_properties':

            data = TblPropertyAllocation.objects.select_related(
                'pa_tenant').select_related(
                    'pa_property').filter(
                        pa_property__pr_master__cln_master=id,
                        pa_is_allocated=True,
            ).order_by(
                '-pa_property__pr_master__cln_is_master_clone',
                'pa_property__pr_master__cln_alias',
                'pa_property__pr_address')
            for d in data:
                print(d.pa_property.pr_master.cln_alias,
                      d.pa_property.pr_address, d.pa_tenant.tn_name)
            # data = TblAgentAllocation.objects.select_related(
            #     'al_agent').select_related('al_master'
            #       ).filter(al_master__cln_master=id)
        elif act == 'unallocated_properties':
            data = TblProperty.objects\
                .select_related('pr_master')\
                .filter(pr_master__cln_master=id,
                        pr_is_allocated=False
                        ).order_by(
                    '-pr_master__cln_is_master_clone',
                    'pr_master__cln_alias',
                    'pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)
        # data= TblMasterPropertyClone.objects\
        # .prefetch_related(Prefetch(

        # ))
        # data = TblAgentAllocation.objects\
        # .select_related('al_agent')\
        # .prefetch_related(Prefetch('al_master',
        #       queryset=TblMasterPropertyClone\
        # .objects.filter(cln_master=id,cln_is_allocated=True),
        #       to_attr='master'))
        # data = TblAgentAllocation.objects.select_related(
        #     'al_agent').select_related('al_master')\
        # .filter(al_master__cln_master=id)

        # .prefetch_related(Prefetch('al_master',
        #   queryset=TblMasterPropertyClone.objects\
        # .filter(cln_master=id
        #   ))).all()
        print(data)

        return render(request, 'admin/show_data.html',
                      {'rows': data, 'act': act, 'msp': id})
    except Exception as e:
        print("error ", e)
        return HttpResponse('''<div  style="color: red;
                                align: right; width: max-content; " >
                                <right>Something Went Wrong While
                                Fetching Requested data</right></div>''')

# Editing Property details


@for_admin
def edit_property(request):
    try:
        pr = TblProperty.objects.get(id=request.GET.get('id'))
        pr.pr_rent = request.GET.get('rent')
        pr.pr_deposite = request.GET.get('deposite')
        pr.pr_description = request.GET.get('description')
        pr.save()
        return HttpResponse("1")
    except Exception as e:
        print("error ", e)
        return HttpResponse("0")


# Deallocating property
@for_admin
def deallocate_clone(request):
    try:
        al = TblAgentAllocation.objects.get(id=request.GET.get('id'))
        tenants = TblTenant.objects\
            .filter(
                pk__in=TblPropertyAllocation.objects
                .filter(pa_property__pr_master=al.al_master,
                        pa_is_allocated=True)
                .values('pa_tenant')
            )
        update_tenant(tenants, request.user)
        al.al_master.cln_is_allocated = False
        al.al_master.save()
        al.delete()
        return HttpResponse("1")
    except Exception as e:
        print("error ", e)
        return HttpResponse("0")


# Deleting clone property
@for_admin
def delete_clone(request):
    try:
        master_clone = TblMasterPropertyClone.objects\
            .get(cln_master=request.GET.get('msp'),
                 cln_is_master_clone=True)
        clone = TblMasterPropertyClone.objects\
            .get(id=request.GET.get('id'))
        tenants = TblTenant.objects\
            .filter(
                pk__in=TblPropertyAllocation.objects
                .filter(pa_property__pr_master=clone,
                        pa_is_allocated=True)
                .values('pa_tenant')
            )
        if master_clone.cln_is_allocated:
            update_tenant(tenants, TblAgentAllocation.objects.get(
                al_master=master_clone).al_agent)
        else:
            update_tenant(tenants, request.user)
        TblProperty.objects.filter(pr_master=clone)\
            .update(pr_master=master_clone)
        clone.delete()
        return HttpResponse("1")
    except Exception as e:
        print("error ", e)
        return HttpResponse("0")

# Allocating Agent


@for_admin
def allocate_clone(request):

    if request.method == 'GET':
        obj_msp = TblMasterProperty.objects.all()
        obj_agent = TblAgent.objects.filter(
            is_active=True, is_staff=True, is_superuser=False)
        if 'msp' in request.GET.keys() and 'cln' in request.GET.keys():
            msp = TblMasterProperty.objects.\
                get(id=request.GET['msp'])
            cln = TblMasterPropertyClone.objects\
                .get(id=request.GET['cln'])
            return render(request, 'admin/agent_allocation.html',
                          {'obj_msp': obj_msp,
                           'obj_agent': obj_agent,
                           'msp': msp,
                           'cln': cln,
                           'agent': None})
        elif 'agent' in request.GET.keys():
            agent = TblAgent.objects.get(id=request.GET.get('agent'))
            return render(request, 'admin/agent_allocation.html',
                          {'obj_msp': obj_msp,
                           'obj_agent': obj_agent,
                           'msp': None,
                           'cln': None,
                           'agent': agent})
        else:
            return render(request, 'admin/agent_allocation.html',
                          {'obj_msp': obj_msp,
                           'obj_agent': obj_agent,
                           'msp': None,
                           'cln': None,
                           'agent': None})

    elif request.method == 'POST':
        try:
            # al_master=TblMasterProperty.objects\
            # .get(id=request.POST['pr_msp'])
            al_master = TblMasterPropertyClone.objects.get(
                id=request.POST['pr_msp_clone'])
            al_master.cln_is_allocated = True
            al_master.save()
            al_agent = TblAgent.objects.get(id=request.POST['agentx'])
            obj = TblAgentAllocation.objects.get_or_create(
                al_agent=al_agent, al_master=al_master)
            print(obj[1])
            obj[0].save()
            tenant_list = TblTenant.objects.filter(
                pk__in=TblPropertyAllocation.objects.filter(
                    pa_property__pr_master=obj[0].al_master
                ).values('pa_tenant')
            )
            update_tenant(tenant_list, al_agent)
            # return render(request,'notify.html',{'msg':'notification testing','code':'success','url':reverse(view_master_property)})
            return notify(msg='Property Allocated Successfully',
                          url=reverse(view_master_property))
            # return HttpResponseRedirect(reverse(view_master_property))
        except Exception as e:
            print('Error ', e)
            return notify(msg='Something went wrong while allocating agent.',
                          code='error',
                          url=reverse(view_master_property))


# Deleting Master property
@for_admin
def delete_master_property(request):
    try:
        msp = TblMasterProperty.objects.get(id=request.GET.get('id'))
        tenants = TblPropertyAllocation.objects.select_related(
            'pa_tenant').select_related('pa_property')\
            .select_related('pa_property__pr_master').\
            filter(pa_property__pr_master__cln_master=msp)
        for tenant in tenants:
            tenant.pa_tenant.tn_status = 0
            tenant.pa_tenant.save()
            # print(tenant.pa_tenant)
        # agents = TblAgent.objects.filter(
        #     pk__in=TblAgentAllocation.objects.filter(
        #         al_master__cln_master=msp
        #     ).values('al_master'))
        # for agent in agents:
        #     update_tenant(agent, request.user)
        msp.delete()
        return HttpResponse("1")
    except Exception as e:
        print('Error at Master property delete', e)
        return HttpResponse("0")


# Removing property from system
@for_admin
def property_soldout(request):
    obj_pr = TblProperty.objects.get(id=request.GET['pr_id'])
    try:
        obj_pr.pr_is_active = False
        obj_pr.pr_is_allocated = False
        obj_pr.save()
        pAllocation = TblPropertyAllocation.objects.get(
            pa_property=obj_pr, pa_is_allocated=True)
        # print(type(pAllocation))
        pAllocation.pa_tenant.tn_status = 0
        pAllocation.pa_tenant.save()
        pAllocation.pa_is_allocated = False
        pAllocation.save()

    except Exception as e:
        print("Error: ", e)
    return HttpResponse("1")


# End-Page View master property .................................................................................

# Page Add Create Clone View....................................................................................
# creating new clone
@for_admin
def create_clone(request):
    msp_list = []
    if request.method == 'POST':
        obj_msp = TblMasterProperty.objects\
            .get(id=request.POST['pr_msp'])
        no = int(request.POST['msp_clone_no'])
        if no > 0 and no <= 50:
            for n in range(1, no+1):
                cln = TblMasterPropertyClone.objects.create(
                    cln_alias=request.POST.get('msp_clone'+str(n)),
                    cln_master=obj_msp,
                    cln_is_allocated=False,
                    cln_is_active=True)
                cln.save()

    else:
        msp_list = TblMasterProperty.objects.all()

    return render(request, 'admin/create_clone.html',
                  {'obj_msp': msp_list})


# End-Page Add Create Clone View..................................................................................

# Page manage Clone View.........................................................................................
# Moving property from one clone to another
@for_admin
def manage_clones(request):
    msp_list = []
    if request.method == 'POST':
        clone = request.POST['to_clone']
        # print(clone)
        objclone = TblMasterPropertyClone.objects.get(pk=clone)
        to_agent = TblAgentAllocation.objects\
            .get(al_master__pk=clone).al_agent
        properties = request.POST.getlist('move_to[]')
        for pr in properties:
            pr = TblProperty.objects.get(id=pr)
            pr.pr_master = objclone
            pr.save()
            if pr.pr_is_allocated:
                try:
                    # code for from agent
                        # from_agent = TblAgentAllocation.objects\
                        #     .get(al_master=TblProperty.objects
                        #         .get(pk=pr).pr_master)\
                        #     .al_master
                        # update_tenant(from_agent, to_agent)
                    try:
                        to_agent = TblAgentAllocation.objects\
                            .get(al_master=pr.pr_master).al_agent
                    except:
                        to_agent = request.user

                    if to_agent is None:
                        to_agent = request.user
                    tenant = TblTenant.objects.filter(
                        pk=TblPropertyAllocation.objects.get(
                            pa_property=pr,
                            pa_is_allocated=True
                        ).pa_tenant
                    )
                    update_tenant(tenant, to_agent)
                except Exception as e:
                    print('Error at manage clone:-', e)

    # else:
    lst = request.POST.getlist('move_to[]')
    print(lst)
    lst = request.POST
    for l in lst.keys():
        print(l, "   ", lst[l])
    msp_list = TblMasterProperty.objects.all()

    return render(request, 'admin/manage_clones.html',
                  {'obj_msp': msp_list})


# showing properties of selected clone or master property
def show_properties(request):
    master = request.GET.get('id')
    is_master_property = request.GET.get('is_master')
    if is_master_property == "true":
        to_clone = request.GET['cln']
        data = TblProperty.objects.\
            select_related('pr_master')\
            .filter(pr_master__cln_master=master)\
            .exclude(pr_master=to_clone)\
            .order_by('-pr_master__cln_is_master_clone',
                      'pr_master__cln_alias',
                      'pr_address')
    else:
        data = TblProperty.objects.\
            select_related('pr_master')\
            .filter(pr_master=master)\
            .order_by('-pr_master__cln_is_master_clone',
                      'pr_master__cln_alias',
                      'pr_address')
    return render(request, 'admin/show_properties.html',
                  {'rows': data, })


# showing list of clones
def move_to_clone_list(request):
    clones = TblMasterPropertyClone.objects.filter(
        cln_master=request.GET['msp']).order_by('id')
    response = """move in clone:
                <select style="width:50%;" name="to_clone"
                 class="form-data"
                 id="to_clone" placeholder="new hint">
                 <option value="" selected="selected">
                 Select Clone</option>
                """
    for clone in clones:
        response += "<option  value="+str(clone.id)+"> "\
            + clone.cln_alias+" </option>"
    response += "</select><br />"
    return HttpResponse(response)


# showing list of clones of selected master property
# excluding selected clone in move_to clone.
def move_from_clone_list(request):
    clones = TblMasterPropertyClone.objects\
        .filter(cln_master=request.GET['msp'])\
        .exclude(id=request.GET['cln']).order_by('id')
    response = """move from clone:
                <select style="width:50%;" name="from_clone"
                 class="form-data"
                 id="from_clone" placeholder="new hint">
                 <option value="" selected="selected">
                 Select Clone</option>
                """
    for clone in clones:
        response += "<option  value="+str(clone.id)+"> "\
            + clone.cln_alias+" </option>"
    response += "</select><br />"
    return HttpResponse(response)


# View to all unmanaged tenants
def view_unmanaged_tenants(request):
    tenantlist = TblTenant.objects.filter(tn_agent=request.user)\
        .annotate(
            tn_clone=Subquery(
                TblPropertyAllocation.objects.filter(
                    pa_tenant=OuterRef('pk'),
                    pa_is_allocated=True
                ).values('pa_property__pr_master__cln_alias')[:1]))\
        .annotate(
            tn_clone_id=Subquery(
                TblPropertyAllocation.objects.filter(
                    pa_tenant=OuterRef('pk'),
                    pa_is_allocated=True
                ).values('pa_property__pr_master')[:1]))\
        .annotate(
            tn_master_property=Subquery(
                TblPropertyAllocation.objects.filter(
                    pa_tenant=OuterRef('pk'),
                    pa_is_allocated=True
                ).values('pa_property__pr_master__cln_master__msp_name')[:1]))\
        .annotate(
            tn_master_property_id=Subquery(
                TblPropertyAllocation.objects.filter(
                    pa_tenant=OuterRef('pk'),
                    pa_is_allocated=True
                ).values('pa_property__pr_master__cln_master')[:1]))
    agents = TblAgent.objects.filter(
        is_active=True, is_staff=True, is_superuser=False)
    for p in tenantlist.values('id', 'tn_status', 'tn_is_active'):
        print(p)
    return render(request, 'admin/view_tenant.html',
                  {'tenantlist': tenantlist, 'agents': agents})


def allocate_unmanaged_tenant(request):
    try:
        tenants = list(map(int, request.GET.get('tenants').split(',')))
        agent = request.GET['agent']
        TblTenant.objects.filter(pk__in=tenants).update(tn_agent=agent)
        return HttpResponse(1)
    except Exception as e:
        print('Error while allocating unmanaged tenants:-', e)
        return HttpResponse(0)

#######################################################################################################################
# Agent site views
#######################################################################################################################

# agent index view


@for_staff
def agent_index(request):
    neartoend_agreement = TblPropertyAllocation.objects\
        .select_related('pa_tenant')\
        .select_related('pa_property__pr_master__cln_master')\
        .filter(pa_is_allocated=True,
                pa_agreement_end_date__lte=datetime.now()
                + timedelta(days=30),
                pa_tenant__tn_agent=request.user)\
        .order_by('pa_agreement_end_date')

    # Monthwise_rentcollection=TblRentCollection.objects\
    #     .filter(rc_allocation__pa_tenant__tn_agent=request.user,rc_pay_off_date__year=datetime.now().year)\
    #     .values('rc_pay_off_date__month')\
    #     .annotate(total=Sum('rc_allocation__pa_final_rent'))\

    # for m in Monthwise_rentcollection.values('rc_pay_off_date','total'):
    #     print(m)

    monthly_rent_collection = TblRentCollection.objects\
        .filter(rc_pay_off_date__lt=datetime.now()
                + timedelta(days=365),
                rc_agent=request.user)\
        .annotate(month=TruncMonth('rc_pay_off_date'))\
        .values('month')\
        .annotate(sum=Sum('rc_allocation__pa_final_rent'))\
        .values('month', 'sum')
    # print(rent_collection.values('month','sum'))

    rent_collection = TblTenant.objects\
        .filter(tn_agent=request.user)\
        .annotate(total=Sum('tblpropertyallocation__tblrentcollection__rc_allocation__pa_final_rent'
                            ))
    # tenantname=[]
    # totalammount=[]
    # for t in rent_collection:
    #     tenantname.append(t.tn_name)
    #     totalammount.append(t.total)
    # print(tenantname,totalammount)

    # print(rentcollection.values("total"))
    # for tenant in rentcollection:
    #     print(tenant.pa_tenant,tenant.total )
    # # * tenant.rc_allocation.pa_final_rent)

    return render(request, 'agent/index.html', {'neartoend_agreement': neartoend_agreement, 'tenantname': rent_collection, 'monthly_rent': monthly_rent_collection})

# view all  tenants of agent


@for_staff
def view_tenants(request):
    # data = TblPropertyAllocation.objects.all()\
    #     .select_related('pa_tenant')\
    #     .prefetch_related(
    #         Prefetch(
    #             'pa_property',
    #             queryset=TblProperty.objects.filter(pr_is_allocated=True),
    #             to_attr='property'
    #         )
    # )

    # tenantlist = TblTenant.objects.all()\
    #     .annotate(
    #         pr_address=Subquery(
    #             TblPropertyAllocation.objects.filter(
    #                 pa_tenant=OuterRef('pk'),
    #                 pa_is_allocated=True
    #             )
    #             .select_related('pa_property')
    #             .values('pa_property__pr_address')
    #         )
    # )
    tenantlist = TblTenant.objects.filter(tn_agent=request.user)\
        .annotate(
            pr_address=Subquery(
                TblPropertyAllocation.objects.filter(
                    pa_tenant=OuterRef('pk'),
                    pa_is_allocated=True
                )
                .select_related('pa_property')
                .select_related('pa_property__pr_master__cln_master')
                .values('pa_property__pr_address',
                        'pa_property__pr_master__cln_master__msp_name',
                        'pa_property__pr_master__cln_master__msp_address')
                .annotate(
                    address=Concat(
                        'pa_property__pr_address',
                        Value(', '),
                        'pa_property__pr_master__cln_master__msp_name',
                        Value(', '),
                        'pa_property__pr_master__cln_master__msp_address'
                    )
                )
                .values('address'),
                output_field=CharField()
            )
    )
    # data = TblTenant.objects.all().tblproperty__set.all()
    # data = TblPropertyAllocation.objects.filter(
    #                 pa_is_allocated=True
    #             )\
    #             .select_related('pa_property')\
    #             .select_related('pa_property__pr_master__cln_master')\
    #             .values('pa_property__pr_address','pa_property__pr_master__cln_master__msp_name','pa_property__pr_master__cln_master__msp_address')\
    #             .annotate(
    #                 address=Concat(Cast('pa_property__pr_address',output_field=CharField()),
    #                 , Cast('pa_property__pr_master__cln_master__msp_name',output_field=CharField())
    #                 , Cast('pa_property__pr_master__cln_master__msp_address',output_field=CharField())

    #             ))

    # data = TblPropertyAllocation.objects.filter(
    #                 pa_is_allocated=True
    #             )\
    # .select_related('pa_property')\
    # .select_related('pa_property__pr_master__cln_master')\
    # .values('pa_property__pr_address','pa_property__pr_master__cln_master__msp_name','pa_property__pr_master__cln_master__msp_address')\
    # .annotate(
    #     address=Concat('pa_property__pr_address',Value(', ')
    #     ,'pa_property__pr_master__cln_master__msp_name',Value(', ')
    #     , 'pa_property__pr_master__cln_master__msp_address'

    # ))
    # print(data.values())
    # for d in tenantlist:
    #     print(d.tn_name, end='    ')
    #     if d.tn_status == 2 or d.tn_status == 3:
    #         print(d.pr_address)
    #     else:
    #         print('Property not allocated')
    # print(tenantlist.values())
    for d in tenantlist.values('tn_name', 'tn_contact', 'tn_status', 'pr_address'):
        print(d)
    # tenantlist = TblTenant.objects.filter(tn_agent=request.user)
    return render(request, 'agent/view_tenant.html',
                  {'tenantlist': tenantlist})

# Adding new tenant to system


@for_staff
def addTenant(request):
    form = TenantRegistratonForm()
    if request.method == 'POST':
        for k in request.POST.keys():
            print(k, "\t", request.POST[k])
        if 'update' in request.POST.keys():
            tenant = TblTenant.objects.get(id=request
                                           .POST['tn_id'])
            tenant.tn_contact = request\
                .POST['tn_contact']
            tenant.tn_permanent_address = request\
                .POST['tn_permanent_address']
            tenant.tn_is_active = True
            tenant.tn_document_description = request\
                .POST['tn_document_description']
            tenant.tn_reference_name = request\
                .POST['tn_reference_name']
            tenant.tn_reference_address = request\
                .POST['tn_reference_address']
            tenant.tn_status = 0
            if 'tn_profile' in request.FILES.keys():
                tenant.tn_profile = request.FILES['tn_profile']
                # print("Data hai:",request.FILES['tn_profile'])
            if 'tn_document' in request.FILES.keys():
                tenant.tn_document = request.FILES['tn_document']
                # print("\n\nIsme bhi hai data",request.FILES['tn_document'])
            tenant.save()

        else:
            form = TenantRegistratonForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    tenant = form.save(commit=False)
                    tenant.tn_agent = request.user
                    tenant.tn_joining_date = request.POST\
                        .get('date_joined')
                    tenant.tn_name = request.POST['tn_name']
                    print("\n\n", request.POST['tn_name'])
                    tenant.tn_is_active = True
                    tenant.save()
                    print(tenant)
                    plist = TblProperty.objects\
                        .select_related('pr_master')\
                        .select_related('pr_master__cln_master')\
                        .filter(pr_is_active=True,
                                pr_is_allocated=False,
                                pr_master__in=TblAgentAllocation
                                .objects.filter(al_agent=request.user)
                                .values('al_master'))
                    print(plist.values())
                    context = {'tenant': tenant, 'plist': plist}
                    return render(request,
                                  'agent/add_visit.html',
                                  context)
                except Exception as e:
                    print("Error:", e)
                    print(form.errors)
            else:
                print(form.errors)

    return render(request, 'agent/add_tenant.html', {'form': form})


def invoke_tenant(request):
    if request.method == 'GET':
        tenant = TblTenant.objects.get(id=request.GET['tid'])
        tenant.__dict__.pop('_state')
        return JsonResponse(tenant.__dict__, safe=False)


def get_deactivated_tenant(request):
    tenantlist = TblTenant.objects.filter(tn_is_active=False,
                                          tn_agent=request.user)\
        .values('id', 'tn_name')
    print(tenantlist)
    return JsonResponse({'tenantlist': list(tenantlist)})


'''List of properties allocated to a perticular agent by admin'''


@for_staff
def allocated_property_list(request):
    allocated_mpr = []
    allocated_pr = []
    if 'propertytype' in request.GET.keys():
        propertytype = request.GET['propertytype']

        if propertytype == "Allocatedproperty":
            allocated_mpr = TblMasterProperty.objects.filter(
                pk__in=TblAgentAllocation.objects
                .filter(al_agent=request.user,
                        al_master__in=TblProperty.objects
                        .filter(pr_is_allocated=True)
                        .order_by('pr_master').distinct('pr_master')
                        .values('pr_master'))
                .select_related('al_master')
                .values('al_master__cln_master'))

            allocated_pr = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation
                    .objects.filter(al_agent=request.user)
                    .values('al_master'), pr_is_allocated=True)\
                .annotate(
                    pr_tenant=Subquery(
                        TblPropertyAllocation.objects
                        .filter(pa_property=OuterRef('pk'),
                                pa_is_allocated=True)
                        .values('pa_tenant'))
                ).annotate(
                    pr_status=Subquery(
                        TblPropertyAllocation.objects
                        .filter(pa_property=OuterRef('pk'),
                                pa_is_allocated=True)
                        .values('pa_tenant__tn_status')[:1])
                )
            # print(allocated_pr.values())

        elif propertytype == "Unallocatedproperty":
            allocated_mpr = TblMasterProperty.objects\
                .filter(pk__in=TblAgentAllocation.objects.filter(
                    al_agent=request.user,
                    al_master__in=TblProperty.objects.filter(
                        pr_is_allocated=False).order_by('pr_master')
                    .distinct('pr_master').values('pr_master'))
                    .select_related('al_master')
                    .values('al_master__cln_master'))
            # print(allocated_mpr.values())

            allocated_pr = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation
                    .objects.filter(al_agent=request.user)
                    .values('al_master'), pr_is_allocated=False)\
                .annotate(
                    pr_tenant=Subquery(
                        TblPropertyAllocation.objects
                        .filter(pa_property=OuterRef('pk'),
                                pa_is_allocated=True)
                        .values('pa_tenant'))
                ).annotate(
                    pr_status=Subquery(
                        TblPropertyAllocation.objects
                        .filter(pa_property=OuterRef('pk'),
                                pa_is_allocated=True)
                        .values('pa_tenant__tn_status')[:1])
                )
            # print(allocated_pr.values())

        elif propertytype == "all":
            allocated_mpr = TblMasterProperty.objects.filter(
                pk__in=TblAgentAllocation.objects.filter(
                    al_agent=request.user,
                    al_master__in=TblProperty.objects.all()
                    .order_by('pr_master').distinct('pr_master')
                    .values('pr_master'))
                .select_related('al_master')
                .values('al_master__cln_master'))
        # print(allocated_mpr.values())

            allocated_pr = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation
                    .objects.filter(al_agent=request.user)
                    .values('al_master'))\
                .annotate(
                    pr_tenant=Subquery(
                        TblPropertyAllocation.objects
                        .filter(pa_property=OuterRef('pk'),
                                pa_is_allocated=True)
                        .values('pa_tenant'))
                ).annotate(
                    pr_status=Subquery(
                        TblPropertyAllocation.objects
                        .filter(pa_property=OuterRef('pk'),
                                pa_is_allocated=True)
                        .values('pa_tenant__tn_status')[:1])
                )
            # for p in allocated_pr:
            #     print(p.tn_status)
            # # print(allocated_pr.values())
        for p in allocated_pr:
            print(p.pr_tenant, p.pr_status)
        return render(request, 'agent/property.html',
                      {'allocated_pr': allocated_pr,
                       'allocated_mpr': allocated_mpr,
                       'propertytype': propertytype})

    allocated_mpr = TblMasterProperty.objects.filter(
        pk__in=TblAgentAllocation.objects.filter(
            al_agent=request.user,
            al_master__in=TblProperty.objects.all()
            .order_by('pr_master').distinct('pr_master')
            .values('pr_master'))
        .select_related('al_master').values('al_master__cln_master'))
    # print(allocated_mpr.values())

    allocated_pr = TblProperty.objects\
        .select_related('pr_master')\
        .select_related('pr_master__cln_master')\
        .filter(
            pr_master__in=TblAgentAllocation
            .objects.filter(al_agent=request.user)
            .values('al_master'))\
        .annotate(
            pr_tenant=Subquery(
                TblPropertyAllocation.objects
                .filter(pa_property=OuterRef('pk'),
                        pa_is_allocated=True)
                .values('pa_tenant'))
        ).annotate(
            pr_status=Subquery(
                TblPropertyAllocation.objects
                .filter(pa_property=OuterRef('pk'),
                        pa_is_allocated=True)
                .values('pa_tenant__tn_status')[:1])
        )
    # print(allocated_pr.values())
    for p in allocated_pr:
        print(p.pr_tenant, p.pr_status)

    return render(request, 'agent/agent_property.html',
                  {'allocated_pr': allocated_pr,
                   'allocated_mpr': allocated_mpr})


# @for_staff
# def rented_property_list(request):
#     allocated_pr = TblProperty.objects\
#                     .select_related('pr_master')\
#                     .select_related('pr_master__cln_master')\
#                     .filter(
#                         pr_master__in=TblAgentAllocation
#                         .objects.filter(al_agent=request.user).values('al_master'))

#     return render(request, 'agent/agent_property.html', {'allocated_pr': allocated_pr})


# '''view tenant Details'''


@for_staff
def TenantDetails(request, tid):
    history = {}
    tenant = {}
    count = 1

    tenant = TblTenant.objects.get(id=tid)
    history = TblPropertyAllocation.objects.filter(
        pa_tenant=tenant)\
        .select_related('pa_property__pr_master__cln_master')
    print(history.values())
    for h in history:
        if h.pa_is_allocated == True:
            count = 0
       
    return render(request, 'agent/view_tenant_detail.html',
                  {'tenant': tenant,
                   'history': history,
                   'count': count, })


# redirect to agent home
# @for_staff
# def agent_index(request):
#     return render(request, 'TM_template/Agent/ag_home.html')


'''To make tenant deactivate'''
@for_staff
def activation_change_tenant(request):
    print("\n\n\naya")
    tenant = TblTenant.objects.get(id=request.GET['id'])
    print(request.GET['change'])
    try:
        if request.GET['change'] == 'activate':
            tenant.tn_is_active = True
        elif request.GET['change'] == 'deactivate':
            tenant.tn_is_active = False
        tenant.save()
        return HttpResponse('1')
    except Exception as e:
        print("\n\nErorr:----------->", e)
    return HttpResponse('0')


@for_staff
def tenant_search_result(request):
    tenantlist = []
    starts_with = ''
    try:
        if request.method == 'GET':
            if 'suggestion' in request.GET.keys():
                status = request.GET['status']
                starts_with = request.GET['suggestion']
                tenantlist = tenant_search(request, starts_with, status)
            # print("\nTenant list:\n", tenantlist)
    except Exception as e:
        print(e)
    return render(request, 'agent/tenants.html', {'tenantlist': tenantlist, 'status': status})


@for_staff
def tenant_search(request, suggestion=None, status="all"):
    tn_list = []
    if suggestion:
        if status == 'all':
            tn_list = TblTenant.objects.filter(
                tn_name__istartswith=suggestion,
                tn_agent=request.user)
        elif status == "active":
            tn_list = TblTenant.objects.filter(
                tn_name__istartswith=suggestion,
                tn_agent=request.user,
                tn_is_active=True)
        elif status == "inactive":
            tn_list = TblTenant.objects.filter(
                tn_name__istartswith=suggestion,
                tn_agent=request.user,
                tn_is_active=False)
    else:
        if status == 'all':
            tn_list = TblTenant.objects.filter(
                tn_agent=request.user)
        elif status == 'active':
            tn_list = TblTenant.objects.filter(
                tn_agent=request.user,
                tn_is_active=True)
        elif status == 'inactive':
            tn_list = TblTenant.objects.filter(
                tn_agent=request.user,
                tn_is_active=False)
    return tn_list


@for_staff
def get_Tenant_list(request):
    if 'pid' in request.GET.keys():
        pobj = TblProperty.objects\
            .select_related('pr_master')\
            .select_related('pr_master__cln_master')\
            .get(pk=request.GET['pid'])

        Tenant_list = TblTenant.objects.filter(
            tn_is_active=True, tn_agent_id=request.user, tn_status=1)
        # print(Tenant_list)
        context = {'pobj': pobj,
                   'Tenant_list': Tenant_list, 'page': "pdetails"}
    elif 'tid' in request.GET.keys():
        ten = TblTenant.objects.get(id=request.GET['tid'],
                                    tn_is_active=True)
        if ten.tn_status == 2:
            prp = TblPropertyAllocation.objects\
                .select_related('pa_property')\
                .get(pa_tenant=ten, pa_is_allocated=True)
            context = {'ten': ten, 'prp': prp, 'page': "tdetails"}
        else:
            # Add filter for already allocated properties to the tenants.
            plist = TblVisit.objects.select_related('vs_property')\
                .select_related('vs_property__pr_master')\
                .select_related('vs_property__pr_master__cln_master')\
                .filter(
                vs_tenant=ten,
                vs_property__pr_is_allocated=False,
                vs_property__pr_is_active=True,
                vs_property__pr_master__in=TblAgentAllocation
                .objects.filter(al_agent=request.user)
                .values('al_master'),
            )\
                .distinct('vs_property')\
                .order_by('vs_property')
            # for p in plist:
            # print(p.msp_name)
            context = {'ten': ten, 'plist': plist, 'page': "tdetails"}
    # else:
    #     Tenant_list = TblTenant.objects.filter(
    #         tn_is_active=True, tn_agent_id=request.user, tn_status=1)
    #     plist = TblProperty.objects\
    #         .select_related('pr_master')\
    #         .select_related('pr_master__cln_master')\
    #         .filter(
    #             pr_master__in=TblAgentAllocation.objects
    #             .filter(al_agent=request.user).values('al_master'),
    #             pr_is_active=True,
    #             pr_is_allocated=False)
    #     print("\n\n\n\n\n\n",plist.values())
    #     print("\n\n\n")
    #     # agent_id=request.user, pr_is_active=True, pr_is_allocated=False)
    #     context = {'Tenant_list': Tenant_list, 'plist': plist, }
    return render(request, 'agent/allocate_property.html',
                  context)


@for_staff
def allocate_property(request):
    if request.method == 'POST':
        p = request.POST['page']
        # # print(p)
        # # print(type(p))
        tobj = TblTenant.objects.get(id=request.POST['tselect'])
        if tobj.tn_status == 2:
            for k in request.POST.keys():
                print(k, "\t", request.POST[k])
            allocation = TblPropertyAllocation.objects\
                .get(pk=request.POST['pselect'])
            print(type(allocation))
            allocation.pa_agreement_date = request\
                .POST['start_agreement_date']
            allocation.pa_agreement_end_date = request\
                .POST['end_agreement_date']
            allocation.pa_acceptance_letter = request\
                .FILES['pa_agreement_letter']
            allocation.pa_tenancy_agreement = request\
                .FILES['tenancy_agreement']
            allocation.pa_tenant.tn_status = 3
            allocation.pa_tenant.save()
            print(allocation.pa_tenant.tn_status)
            # breakpoint()
            # allocation.al_property.pr_is_allocated =
            # allocation.pa_final_rent = request.POST['final_rent'],
            allocation.save()
        else:
            objp = TblProperty.objects.get(id=request.POST['pselect'])
            # print(objp)

            # print(tobj)
            try:
                allocation = TblPropertyAllocation.objects.create(
                    pa_property=objp,
                    pa_tenant=tobj,
                    pa_agreement_date=request
                    .POST['start_agreement_date'],
                    pa_agreement_end_date=request
                    .POST['end_agreement_date'],
                    pa_acceptance_letter=request
                    .FILES['pa_agreement_letter'],
                    pa_tenancy_agreement=request
                    .FILES['tenancy_agreement'],
                    pa_final_rent=request.POST['final_rent'],
                    pa_is_allocated=True)
                allocation.save()
                objp.pr_is_allocated = True
                objp.save()
                tobj.tn_status = 3
                tobj.save()
            except Exception as e:
                print("\n\nError: ", e)

        if p == "pdetails":
            return notify(msg='Property Allocated Successfully',
                          url=reverse(allocated_property_list))
        if p == "tdetails":
            return notify(msg='Property Allocated Successfully',
                          url=reverse(view_tenants))
    return get_Tenant_list(request)


@for_staff
def deallocate_property(request):
    if 'tenant' in request.GET.keys():
        try:
            tid = request.GET['tenant']
            tobj = TblTenant.objects.get(id=tid)
            tobj.tn_status = 0
            tobj.save()
            pAllocation = TblPropertyAllocation.objects.get(
                pa_tenant=tobj, pa_is_allocated=True)
            pAllocation.pa_property.pr_is_allocated = False
            pAllocation.pa_property.save()
            pAllocation.pa_is_allocated = False
            pAllocation.save()
            return HttpResponse("1")
        except Exception as e:
            print("Error ", e)
    if 'property' in request.GET.keys():
        try:
            pid = request.GET['property']
            print("\n\n", pid, "\n\n")
            pobj = TblProperty.objects.get(id=pid)
            print(type(pobj))
            TblProperty.objects.filter(id=pid).update(
                pr_is_allocated=False)
            pAllocation = TblPropertyAllocation.objects.get(
                pa_property=pobj, pa_is_allocated=True)
            print(type(pAllocation))
            pAllocation.pa_tenant.tn_status = 0
            pAllocation.pa_tenant.save()
            pAllocation.pa_is_allocated = False
            pAllocation.save()
            return HttpResponse("1")
        except Exception as e:
            print("Error ", e)
    return HttpResponse("0")


@for_staff
def get_tenant_visit(request):
    id = request.GET.get('id')
    visits = TblVisit.objects.select_related('vs_property')\
        .select_related('vs_property__pr_master__cln_master')\
        .filter(vs_tenant=id,
                vs_property__pr_is_allocated=False,
                vs_property__pr_is_active=True,
                vs_property__pr_master__in=TblAgentAllocation
                .objects.filter(al_agent=request.user)
                .values('al_master'),
                )\
        .distinct('vs_property')\
        .order_by('vs_property')
    # TblVisit.objects.select_related('vs_property')\
    #         .select_related('vs_property__pr_master')\
    #         .select_related('vs_property__pr_master__cln_master')\
    #         .filter(
    #         vs_tenant=ten,
    #         vs_property__pr_is_allocated=False,
    #         vs_property__pr_is_active=True,
    #         vs_property__pr_master__in=TblAgentAllocation
    #                     .objects.filter(al_agent=request.user)
    #                     .values('al_master'),
    #     )\
    #         .distinct('vs_property')\
    #         .order_by('vs_property')
    if visits.first() is not None:
        response = """<option value="" selected="selected">
                    Select Proerty</option>
                    """
        for visit in visits:
            response += "<option  value="+str(visit.vs_property.id)\
                + "> " + visit.vs_property.pr_address+" " \
                + visit.vs_property.pr_master.cln_master.msp_name + " "\
                + visit.vs_property.pr_master.cln_master.msp_address +\
                "  Rent: " + str(visit.vs_property.pr_rent)\
                + " </option>"
        return HttpResponse(response)
    else:
        return HttpResponse(0)


@for_staff
def change_tenant_status(request):
    tenant = TblTenant.objects.get(id=request.POST['tid'])
    msg = ''
    code = 'success'
    try:
        if tenant.tn_is_active == False:
            tenant.tn_is_active = True
            tenant.save()
            msg = 'Tenant Activated Successfully.'
        else:
            tenant.tn_is_active = False
            tenant.tn_status = 0
            tenant.save()
            pAllocation = TblPropertyAllocation.objects.get(
                pa_tenant=tenant, pa_is_allocated=True)
            pAllocation.pa_property.pr_is_allocated = False
            pAllocation.pa_property.save()
            pAllocation.pa_is_allocated = False
            pAllocation.save()
            msg = 'Tenant Deactivated Successfully.'
    except Exception as e:
        msg = 'Something went wrong while changing status of tenant.'
        code = 'error'
        print("\n\nErorr:----------->", e)
    return notify(msg=msg, code=code, url=reverse(view_tenants))


@for_staff
def add_visit(request):

    if request.method == 'GET':
        if 'tid' in request.GET.keys():
            # print(request.GET['tid'])
            tenant = TblTenant.objects.get(id=request.GET['tid'])
            plist = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation.objects
                    .filter(al_agent=request.user).values('al_master'),
                    pr_is_active=True,
                    pr_is_allocated=False)
            context = {'tenant': tenant, 'plist': plist}
        else:
            tlist = TblTenant.objects.filter(
                tn_is_active=True, tn_agent_id=request.user)
            plist = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation.objects
                    .filter(al_agent=request.user).values('al_master'),
                    pr_is_active=True,
                    pr_is_allocated=False)
            context = {'tlist': tlist, 'plist': plist}
        return render(request, 'agent/add_visit.html',
                      context)
    if request.method == 'POST':
        tenant = TblTenant.objects.get(id=request.POST['selectedtn'])
        if tenant.tn_status == 0:
            tenant.tn_status = 1
            tenant.save()
        prop = TblProperty.objects.get(id=request.POST['selectedpr'])
        TblVisit.objects.create(vs_tenant=tenant,
                                vs_property=prop,
                                vs_date=request.POST['visitdate'],
                                vs_intrest_status=request.
                                POST['selectedin'])
        return notify(msg='Visit Rrecorded Successfully.',
                      url=reverse(view_tenants))
    else:
        agent_index(request)


def change_status(request):
    if request.method == 'GET':
        for k in request.GET.keys():
            print(k, "  ", request.GET[k])

        try:
            tenant = TblTenant.objects.get(pk=request.GET['id'])
            status = request.GET['status']
            current_status = tenant.tn_status
            if status == '0':
                if current_status == 1:
                    tenant.tn_status = '0'
                    tenant.save()
                elif current_status in [2, 3]:
                    allocation = TblPropertyAllocation.objects.get(
                        pa_tenant=tenant,
                        pa_is_allocated=True,
                    )
                    allocation.pa_property.pr_is_allocated = False
                    allocation.pa_property.save()
                    allocation.pa_tenant.tn_status = '0'
                    allocation.pa_tenant.save()
                    allocation.pa_is_allocated = False
                    allocation.save()
                return HttpResponse("1")
            elif status == '2':
                if request.GET['update'] == 'true':
                    allocation = TblPropertyAllocation.objects.get(
                        pa_tenant=tenant,
                        pa_is_allocated=True,
                    )
                    allocation.pa_tenant.tn_status = '2'
                    allocation.pa_tenant.save()
                    allocation.pa_is_allocated = False
                    allocation.save()

                    new_allocation = allocation
                    new_allocation.pk = None
                    new_allocation.pa_agreement_date = None
                    new_allocation.pa_agreement_end_date = None
                    new_allocation.pa_acceptance_letter = None
                    new_allocation.pa_tenancy_agreement = None
                    new_allocation.pa_is_allocated = True
                    # new_allocation.pa_final_rent = None
                    new_allocation.save()

                    # allocation.pa_property.pr_is_allocated = False
                    # allocation.pa_property.save()

                else:
                    prp = TblProperty.objects\
                        .get(pk=request.GET['property'])
                    allocation = TblPropertyAllocation.objects\
                        .create(
                            pa_property=prp,
                            pa_tenant=tenant,
                            pa_is_allocated=True,
                            pa_final_rent=request.GET['rent']
                        )
                    allocation.save()
                    prp.pr_is_allocated = True
                    prp.save()
                    tenant.tn_status = 2
                    tenant.save()

                return HttpResponse("1")

        except Exception as e:
            print('Error in updating the ststus of tenant.', e)
            return HttpResponse("0")


@for_staff
def view_visit(request):

    months = None
    visits = None
    if 'year' in request.GET.keys():
        year = request.GET['year']
    else:
        year = datetime.now().year
    try:
        status = request.GET.get('status')
    except Exception as e:
        print('Error at request', e)
        status = None
    if status == 'allocated':
        months = TblVisit.objects\
            .filter(vs_date__year=year,
                    
                    vs_property__pr_is_allocated=True)\
            .dates('vs_date', 'month', order='DESC')\
            .distinct('datefield').order_by('datefield')\
            .values('datefield')
        print(months)
        for d in months:
            print(d.get('datefield').strftime('%B, %Y'))
        visits = TblVisit.objects\
            .filter(vs_date__year=year,
                    vs_tenant__tn_agent=request.user,
                    vs_property__pr_is_allocated=True)\
            .select_related('vs_tenant')\
            .select_related('vs_property')\
            .annotate(
                vs_address=Subquery(
                    TblProperty.objects.filter(
                        pk=OuterRef('vs_property')
                    )
                    .select_related('pr_master__cln_master')
                    .values('pr_address',
                            'pr_master__cln_master__msp_name',
                            'pr_master__cln_master__msp_address')
                    .annotate(
                        address=Concat(
                            'pr_address',
                            Value(', '),
                            'pr_master__cln_master__msp_name',
                            Value(', '),
                            'pr_master__cln_master__msp_address'
                        )
                    )
                    .values('address'),
                    output_field=CharField()
                )
            )
        return render(request, 'agent/visit.html',
                      {'visits': visits,
                       'months': months})
    elif status == 'unallocated':
        months = TblVisit.objects\
            .filter(vs_date__year=year,
                    vs_property__pr_is_allocated=False)\
            .dates('vs_date', 'month', order='DESC')\
            .distinct('datefield').order_by('datefield')\
            .values('datefield')
        print(months)
        for d in months:
            print(d.get('datefield').strftime('%B, %Y'))
        visits = TblVisit.objects\
            .filter(vs_date__year=year,
            vs_tenant__tn_agent=request.user,
                    vs_property__pr_is_allocated=False)\
            .select_related('vs_tenant')\
            .select_related('vs_property')\
            .annotate(
                vs_address=Subquery(
                    TblProperty.objects.filter(
                        pk=OuterRef('vs_property')
                    )
                    .select_related('pr_master__cln_master')
                    .values('pr_address',
                            'pr_master__cln_master__msp_name',
                            'pr_master__cln_master__msp_address')
                    .annotate(
                        address=Concat(
                            'pr_address',
                            Value(', '),
                            'pr_master__cln_master__msp_name',
                            Value(', '),
                            'pr_master__cln_master__msp_address'
                        )
                    )
                    .values('address'),
                    output_field=CharField()
                )
            )
        return render(request, 'agent/visit.html',
                      {'visits': visits,
                       'months': months})
    elif status == 'all':
        months = TblVisit.objects.filter(vs_date__year=year,)\
            .dates('vs_date', 'month', order='DESC')\
            .distinct('datefield').order_by('datefield')\
            .values('datefield')
        print(months)
        for d in months:
            print(d.get('datefield').strftime('%B, %Y'))
        visits = TblVisit.objects.filter(vs_date__year=year,
        vs_tenant__tn_agent=request.user,)\
            .select_related('vs_tenant')\
            .select_related('vs_property')\
            .annotate(
            vs_address=Subquery(
                TblProperty.objects.filter(
                    pk=OuterRef('vs_property')
                )
                .select_related('pr_master__cln_master')
                .values('pr_address',
                        'pr_master__cln_master__msp_name',
                        'pr_master__cln_master__msp_address')
                .annotate(
                    address=Concat(
                        'pr_address',
                        Value(', '),
                        'pr_master__cln_master__msp_name',
                        Value(', '),
                        'pr_master__cln_master__msp_address'
                    )
                )
                .values('address'),
                output_field=CharField()
            )
        )
        return render(request, 'agent/visit.html',
                      {'visits': visits,
                       'months': months})
    else:

        months = TblVisit.objects.filter(vs_date__year=year)\
            .dates('vs_date', 'month', order='DESC')\
            .distinct('datefield').order_by('datefield')\
            .values('datefield')
        print(months)
        for d in months:
            print(d.get('datefield').strftime('%B, %Y'))
        visits = TblVisit.objects.filter(vs_date__year=year
        ,vs_tenant__tn_agent=request.user,)\
            .select_related('vs_tenant')\
            .select_related('vs_property')\
            .annotate(
            vs_address=Subquery(
                TblProperty.objects.filter(
                    pk=OuterRef('vs_property')
                )
                .select_related('pr_master__cln_master')
                .values('pr_address',
                        'pr_master__cln_master__msp_name',
                        'pr_master__cln_master__msp_address')
                .annotate(
                    address=Concat(
                        'pr_address',
                        Value(', '),
                        'pr_master__cln_master__msp_name',
                        Value(', '),
                        'pr_master__cln_master__msp_address'
                    )
                )
                .values('address'),
                output_field=CharField()
            )
        )
        # print(visits.values())
        return render(request, 'agent/view_visit.html',
                      {'visits': visits,
                       'months': months,
                       'year': year})


@for_staff
def getrent(request):
    rent = TblProperty.objects.get(id=request.GET['pid'])
    print(rent.pr_rent)
    return HttpResponse(rent.pr_rent)


@for_staff
def add_rent_collected(request):
    last_paid = None
    if request.method == 'GET':
        if 'pid' in request.GET.keys():
            propertyobj = TblPropertyAllocation.objects\
                .select_related('pa_property')\
                .select_related('pa_tenant')\
                .get(pa_property=request.GET['pid'],
                     pa_is_allocated=True)
            print(propertyobj)
            alloc_count = TblPropertyAllocation.objects\
                .filter(pa_property=propertyobj.pa_property,
                        pa_tenant=propertyobj.pa_tenant).count()
            print("\n\n\n\n", alloc_count)
            if alloc_count > 1:
                if propertyobj.pa_tenant.tn_status == 2:
                    prp = TblPropertyAllocation.objects\
                        .select_related('pa_property')\
                        .select_related('pa_tenant')\
                        .filter(pa_property=request.GET['pid'],
                                pa_is_allocated=False,
                                pa_tenant=propertyobj.pa_tenant)\
                        .order_by('pk')[:1]
                    if prp.first() is not None:
                        propertyobj = prp.first()
                    else:
                        return render(request, 'agent/add_rent.html',
                                      {'propertyobj': propertyobj,
                                       'unpaidflag': False})

                    print(propertyobj)

        elif 'tid' in request.GET.keys():
            propertyobj = TblPropertyAllocation.objects.select_related('pa_property').select_related(
                'pa_tenant').get(pa_tenant=request.GET['tid'], pa_is_allocated=True)

        # print("\n\nProperty:",propertyobj.id)
        rentdetails = TblRentCollection.objects.filter(
            rc_allocation=propertyobj)
        # length = (len(rentdetails.values()))
        print("\n\nRent Details:", rentdetails)
        # diff_month=(propertyobj.pa_agreement_end_date,propertyobj.pa_agreement_date)

        i = propertyobj.pa_agreement_date
        if i == None:
            result = []
            upflag = "Agreement Under Process"
        else:
            # print("start",i)
            # print("end",propertyobj.pa_agreement_end_date)
            months = []
            delta = timedelta(days=30)
            while i < propertyobj.pa_agreement_end_date:
                # print("i",i)
                months.append(i.strftime("%B, %Y"))
                # print(i.strftime("%B"))
                i += delta
            result = []

            recorded = False
            for m in months:
                # print("\n\naya")
                # print(len(rentdetails))
                if (len(rentdetails.values()) > 0):
                    rent = False
                    for r in rentdetails:
                        # print("\n\naya")
                        if m == r.rc_month.strftime("%B, %Y"):
                            rent = True
                            # print("Except")
                            # # last_paid = r.rc_month
                            # # last_paid += delta
                            break
                    if rent:
                        result.append([m, "Paid"])
                    else:
                        if not recorded:
                            last_paid = datetime.strptime(m, "%B, %Y")
                            recorded = True
                        result.append([m, "Unpaid"])

                else:
                    result.append([m, "Unpaid"])
                    if not last_paid:
                        last_paid = datetime.strptime(m, "%B, %Y")
            print(result)
            if last_paid is not None:
                last_paid = last_paid.strftime("%B, %Y")
            upflag = False
            for r in result:
                if "Unpaid" in r:
                    upflag = True
            print("\n\nUnpaid Flag", upflag)
        return render(request, 'agent/add_rent.html',
                      {'propertyobj': propertyobj,
                       'rentdetails': rentdetails,
                       'months': result,
                       'last_paid': last_paid,
                       'unpaidflag': upflag})

    elif request.method == 'POST':
        for k in request.POST.keys():
            print(k, "\t", request.POST[k])
        for k in request.FILES.keys():
            print(k, "\t", request.FILES[k])
        print(type(request.POST['payofmonth']))
        paymonth = datetime.strptime(request.POST['payofmonth'],
                                     "%B, %Y")
        print(paymonth)
        print(type(paymonth))
        allocation = TblPropertyAllocation.objects.get(
            id=request.POST['allocationid'])
        # print(allocation.id)
        addrent = TblRentCollection.objects\
            .create(rc_allocation=allocation,
                    rc_recipt_no=request.POST['reciptno'],
                    rc_recipt=request.FILES['reciptpic'],
                    rc_month=paymonth,
                    rc_pay_off_date=datetime.now(),
                    rc_agent=request.user)
        addrent.save()
        return redirect('/agent/add_rent/?pid='
                        + str(allocation.pa_property.id))


@for_staff
def check_allocation(request):
    if 'pid' in request.GET.keys():
        propertyobj = TblPropertyAllocation.objects\
            .select_related('pa_property')\
            .select_related('pa_tenant')\
            .get(pa_property=request.GET['pid'],
                 pa_is_allocated=True)
        if propertyobj.pa_tenant.tn_status == 3:
            return HttpResponse("1")
        else:
            return HttpResponse("0")


@for_staff
def getAllocatedtenants(request):
    response = ""
    if 'tenantid' in request.GET.keys():
        tenant = TblTenant.objects.get(id=request.GET['tenantid'])
        allocatedproperty = TblPropertyAllocation.objects\
            .filter(pa_tenant=tenant, pa_is_allocated=True)\
            .select_related('pa_tenant')\
            .select_related('pa_property__pr_master__cln_master')
        print(allocatedproperty)
        for allocation in allocatedproperty:
            response = allocation.pa_property.pr_address+" " \
                + allocation.pa_property.pr_master.cln_master.msp_name\
                + " "\
                + allocation.pa_property.pr_master.cln_master.msp_address

    else:
        tenantlist = TblPropertyAllocation.objects\
            .filter(pa_is_allocated=True,
                    pa_tenant__tn_agent=request.user
                    ).filter(~Q(pa_agreement_date=None))\
            .select_related('pa_tenant')\
            .select_related('pa_property__pr_master__cln_master')

        print(tenantlist)

        response += """<option value="" selected="selected">
                        Select Tenant</option>"""
        for tenant in tenantlist:
            response += "<option value=" + str(tenant.pa_tenant.id)\
                + ">" + tenant.pa_tenant.tn_name \
                + "</option>"
    return HttpResponse(response)


@for_staff
def viewallocationDetails(request):
    if 'pid' in request.GET.keys():
        allocatedproperty = TblProperty.objects.get(
            id=request.GET['pid'], pr_is_allocated=True)
        allocation = TblPropertyAllocation.objects\
            .filter(pa_property=allocatedproperty,
                    pa_is_allocated=True)\
            .select_related('pa_property__pr_master__cln_master')\
            .select_related('pa_tenant')

        # print(allocation.values())
        pr = []
        for a in allocation:
            pr = a
        rentdetails = TblRentCollection.objects.filter(rc_allocation=pr)
        # length = (len(rentdetails.values()))
        print("\n\nRent Details:", rentdetails)

        i = pr.pa_agreement_date
        # print("start",i)
        # print("end",propertyobj.pa_agreement_end_date)
        months = []
        delta = timedelta(days=30)
        try:
            while i < pr.pa_agreement_end_date:
                # print("i",i)
                months.append(i.strftime("%B, %Y"))
                # print(i.strftime("%B"))
                i += delta
            result = []

            recorded = False
            for m in months:
                if (len(rentdetails.values()) > 0):
                    rent = False
                    for r in rentdetails:
                        if m == r.rc_month.strftime("%B, %Y"):
                            rent = True
                            break
                    if rent:
                        result.append([m, "Paid"])
                    else:
                        if not recorded:
                            recorded = True
                        result.append([m, "Unpaid"])
                else:
                    result.append([m, "Unpaid"])
            upflag = False
            for r in result:
                if "Unpaid" in r:
                    upflag = True
            print("\n\nUnpaid Flag", upflag)
            return render(request, 'agent/allocation_details.html',
                          {'allocation': pr,
                           'months': result,
                           'unpaidflag': upflag})
        except Exception as e:
            print("No previous allocation ", e)
            return notify(msg='Tenant has no previous allocation',
                          url=reverse(allocated_property_list))


#######################################################################################################################
# Tenant site views
#######################################################################################################################


def tenant_index(request):
    return render(request, 'tenant_index.html')


def tenant_details(request, tenant_name):
    tenant_contact = request.GET['tenant_contact']
    tenant = None
    pa = None
    context = dict()
    rent_details = None
    rent_data = None
    try:
        tenant = TblTenant.objects\
            .get(tn_name__iexact=tenant_name,
                 tn_contact=tenant_contact)
    except Exception as e:
        print('Error at searching tenant-> ', e)
        tenant = None
        return render(request, 'tenant_details.html', context)

    if tenant and tenant.tn_status == 2 or tenant.tn_status == 3:
        if tenant.tn_status == 2:
            pa = TblPropertyAllocation.objects\
                .filter(pa_is_allocated=False,
                        pa_tenant=tenant)\
                .order_by('pk')[:1]
            if pa.first() is not None:
                pa = pa.first()
            else:
                return render(request, 'tenant_details.html',
                              {'tenant': tenant})
        elif tenant.tn_status == 3:
            pa = TblPropertyAllocation.objects\
                .get(pa_is_allocated=True,
                     pa_tenant=tenant)

        rent_details = TblRentCollection.objects\
            .filter(rc_allocation=pa)

        print(pa.pa_agreement_date)
        print(pa.pa_agreement_end_date)
        last_paid = None
        recorded = False
        i = pa.pa_agreement_date
        rent_data = []
        delta = timedelta(days=30)
        while i.month < pa.pa_agreement_end_date.month\
                or i.year < pa.pa_agreement_end_date.year:
            if (len(rent_details.values()) > 0):
                rent = False
                for r in rent_details:
                    if i.strftime("%B, %Y") ==\
                            r.rc_month.strftime("%B, %Y"):
                        rent = True
                        break
                if rent:
                    rent_data.append({
                        'month': i.strftime("%B, %Y"),
                        'status': 'Paid',
                        'date': r.rc_pay_off_date})
                else:
                    if not recorded:
                        last_paid = i.strftime("%B, %Y")
                        recorded = True
                    rent_data.append({
                        'month': i.strftime("%B, %Y"),
                        'status': 'Unpaid',
                        'date': 'Not Paid Yet.'})

            else:
                rent_data.append({
                    'month': i.strftime("%B, %Y"),
                    'status': 'Unpaid',
                    'date': 'Not Paid Yet.'})
                if not last_paid:
                    last_paid = datetime.strftime("%B, %Y")
            # rent_data.append(i)
            i += delta
        for rent in rent_data:
            print(rent)
    context = {
        'tenant': tenant,
        'allocation': pa,
        'rent_data': rent_data
    }
    return render(request, 'tenant_details.html', context)

    # else:
    #     return HttpResponse('You don\'t have any active data in the system')

    # print(tenant)
    # # return HttpResponse(tenant)
    # return HttpResponse('Something went wrong...')
