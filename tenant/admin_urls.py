from django.contrib import admin
from django.urls import path, re_path
from tenant import views

urlpatterns = [
    # index page after login
    re_path('^$', views.admin_index, name="admin_index"),

    # Showing all agents requests
    path('agent_requests/', views.view_agent_request,
         name="admin_agent_requests"),

    # Showing all active agents
    path('agent_active/', views.view_agent_all,
         name="admin_agent_active"),

    # Accepting Agent requests
    path('agent_request_accept/', views.agent_request_accept,
         name='admin_agent_request_accept'),

    # Rejecting Agent Request
    path('agent_request_reject/', views.agent_request_reject,
         name='admin_agent_request_reject'),

    # Showing Agent Profile
    re_path(r'^(?P<tid>[\w\-]+)/agent_requests/agent_profile/',
         views.agent_profile, name='admin_agent_profile'),

    # Showing the data on master property
    path('show_data_agent/', views.show_data_agent,
         name='admin_show_data_agent'),

    # Activating and Retireing Agents
    path('agent_action/', views.agent_action,
         name='admin_agent_action'),

    # Searching agent in the agents requests
    path('agent_request_search/', views.agent_requests_search,
         name='admin_agent_requests_search'),

    # Searching agent in active agents list
    path('agent_active_search/', views.agent_active_search,
         name='admin_agent_active_search'),

    # Adding Master property in the System
    path('add_master_property/', views.add_master_property,
         name='admin_add_master_property'),

    # Showing the number of textboxes for
    #  adding clones in master property
    path('master_clone_list/', views.create_clone_list,
         name='admin_create_clone_list'),

    # Viewing Master Properties
    path('view_master_property/', views.view_master_property,
         name='admin_view_master_property'),

    # Deleting Master Properties
    path('delete_master_property/', views.delete_master_property,
         name='admin_delete_master_property'),

    # Adding property to selected clone of master property
    path('add_property/', views.add_property,
         name='admin_add_property'),

    # Showing clones of seleced master property
    path('property_clone_list/', views.clone_list,
         name='admin_show_clone_list'),

    # Showing the data on master property
    path('show_data/', views.show_data,
         name='admin_show_data'),

    # Editing property
    path('edit_property/', views.edit_property,
         name='admin_edit_property'),

    # Deallocating clone
    path('deallocate_clone/', views.deallocate_clone,
         name='admin_deallocate_clone'),

    # Deleteing clone
    path('delete_clone/', views.delete_clone,
         name='admin_delete_clone'),

    # Allocating clone
    path('allocate_clone/', views.allocate_clone,
         name='admin_allocate_clone'),

    # Creating clone
    path('create_clone/', views.create_clone,
         name='admin_create_clone'),

    # managing clones
    path('manage_clones/', views.manage_clones,
         name='admin_manage_clones'),

    # Showing properties of selected clone
    path('show_properties/', views.show_properties,
         name='admin_show_properties'),

    # Showing Clone list of selected Master property
    path('move_to_clone_list/', views.move_to_clone_list,
         name='admin_move_to_clone_list'),

    # Showing Clone list of selected Master property
    # excluding the selected clone
    path('move_from_clone_list/', views.move_from_clone_list,
         name='admin_move_from_clone_list'),

    # View all unmanaged tenants on admin side.
    path('unmanaged_tenants', views.view_unmanaged_tenants,
         name='admin_unmanaged_tenants'),

    # View all unmanaged tenants on admin side.
    path('allocate_unamanaged_tenant', views.allocate_unmanaged_tenant,
         name='admin_allocate_unamanaged_tenant'),
]
