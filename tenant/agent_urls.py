from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    # index page after login
    re_path('^$', views.agent_index, name='agent_index'),

    # Adding new tenant to system
    re_path('AddTenant/', views.addTenant, name='addTenant'),

    # Viewing Details of all tenants
    path('ViewTenants/', views.view_tenants, name='view_tenants'),

    # Viewing search result of tenants
    path('tenant_search_list/', views.tenant_search_result,
         name='tenant_search_result'),

    # Viewing details of all properties allocated to agent.
    path('Agent_Properties/', views.allocated_property_list,
         name='allocated_property_view'),

    # Viewing tenant profile.
    re_path(r'^(?P<tid>[\w\-]+)/Tenant_Profile_view/',
            views.TenantDetails, name='TenantDetails'),

    # Activating or deactivating tenant.
    path('activation_change_tenant/', views.activation_change_tenant,
         name='activation_change_tenant'),

    # Loading alocate property with proper data.
    path('get_Tenant_list/', views.get_Tenant_list,
         name='get_Tenant_list'),

    # Allocating property to tenant.
    path('allocate_property/', views.allocate_property,
         name='allocate_property'),

    # Deallocating property.
    path('deallocate_property/', views.deallocate_property,
         name='deallocate_property'),

    # Adding new visit of tenant.
    path('add_visit/', views.add_visit, name='add_visit'),

    # Changing tenant status after
    # property allocation or deallocation.
    path('tenant_status_change/', views.change_status,
         name='change_status'),

    # Return list of tenants visits in select html.
    path('get_tenant_visit/', views.get_tenant_visit,
         name='tenant_visit_select'),

    # Returning list of inactive tenants.
    path('get_deactivated_tenant/', views.get_deactivated_tenant,
         name='get_deactivated_tenant'),

    # Acivating previously deactivated tenants.
    path('activate_tenant/', views.invoke_tenant),

    # Adding data of collected rent.
    path('add_rent/', views.add_rent_collected,
         name='add_rent'),

    # Checking if property is allocated or not.
    path('check_allocation/', views.check_allocation,
         name='check_allocation'),

    # Viewing all visits to property.
    path('view_visits/', views.view_visit, name='view_visit'),
    path('getAllocatedtenants/',views.getAllocatedtenants),
    path('viewallocationDetails/',views.viewallocationDetails),

]
