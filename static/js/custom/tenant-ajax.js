$('.accept_agent_request').live('click', function () {
    if (confirm('Are You sure you want to activate this Agent?')) {
        $.get('/admin/agent_request_accept/', { id: $(this).attr('data-id') }, function (data) {
            if (data == '1') {
                status = "Agent Request Accepted.";
                localStorage.setItem("Status", status);
                location.reload();
            }
            else {
                $.notify('Something went wrong while Accepting agent request.', 'error')
            }
        })
    }
});

$('.reject_agent_request').live('click', function () {
    if (confirm('Are You sure you want to Reject this Agent?\n You won\'t be able to revert the change.')) {
        $.get('/admin/agent_request_reject/', { id: $(this).attr('data-id') }, function (data) {
            if (data == '1') {
                status = "Agent Request Rejected.";
                localStorage.setItem("Status", status);
                location.reload();
            }
            else {
                $.notify('Something went wrong while deleting agent request.', 'error')
            }
        })
    }
});


// Function to handle the agents status on the click of agent-act button.
$('.agent-act').live("click", function () {
    var ag_id;
    var act;
    ag_id = $(this).attr("data-id");
    act = $(this).attr("data-act");
    var view = $(this).attr('data-view')
    var msg;
    if (act == "0") {
        msg = "Are you sure to retire this Agent?\nAll this agent's property and tenants will be unhandled."
    }
    else {
        msg = "Are you sure to Activate this Agent?"
    }
    if (window.confirm(msg)) {
        $.get('/admin/agent_action/', { id: ag_id, is_active: act }, function (data) {
            if (view == 'view') {
                location.href = '/admin/' + ag_id + '/agent_requests/agent_profile/';
            }

        });
        if (view != 'view') {
            if (act == "0") {
                $.notify("Agent Retired Successfully.", "success")
                $("#td" + ag_id).html("Retired")
                $(this).attr("data-act", "1");
                $(this).val("Activate");
                $(this).removeClass("btn-danger").addClass("btn-success");
                $(this).parent().siblings('.allocation').html('');
            }
            else {
                $.notify("Agent Activated Successfully.", "success")
                $("#td" + ag_id).html("Active")
                $(this).attr("data-act", "0");
                $(this).val("Retire");
                $(this).removeClass("btn-success").addClass("btn-danger");
                $(this).parent().siblings('.allocation').html('<input type="button"' +
                    ' class="agent-allocate btn-success btn-rounded"' +
                    ' data-id="' + ag_id + '" value="Allocate">');
            }
        }


    }
});

// Allocating property to agent if he is active
$('.agent-allocate').live("click", function () {
    var ag_id = $(this).attr("data-id");
    location.href = '/admin/allocate_clone/?agent=' + ag_id;
});


$(function () {
    $("select").select2();
});

// Searching in Agent request on search textbox
$('#search').keyup(function () {
    var query;
    query = $(this).val();
    $.get('/admin/agent_request_search/', { suggestion: query }, function (data) {
        $('#tbl_agents').html(data);
    });
});


// Searching in Agent request on search textbox
$('#search_agent').keyup(function () {
    var query;
    query = $(this).val();
    $.get('/admin/agent_active_search/', { suggestion: query }, function (data) {
        $('#tbl_agents').html(data);
    });
});

// Showing agent allocation details
$('.show_data_agent').click(function () {
    var id = $(this).attr('data-id');
    var hidden = $(this).attr('data-hidden');
    var act = $(this).attr('data-act');

    if (hidden == '1') {
        $(this).parent().siblings().children(
            '.show_data_agent').html('<i class="icon-angle-down"></i>');
        $(this).parent().siblings().children(
            '.show_data_agent').attr('data-hidden', '1');
        $(this).parent().parent().next().removeClass("hidden");
        $(this).html('<i class="icon-angle-up"></i>');
        $(this).attr('data-hidden', '0');
        $this = $(this)
        $.get('/admin/show_data_agent/', { id: id, act: act }, function (data) {
            $this.parent().parent().next().children().html(data);
        });
    }
    else if (hidden == '0') {
        $(this).parent().parent().next().addClass("hidden");
        $(this).html('<i class="icon-angle-down"></i>');
        $(this).attr('data-hidden', '1');
    }
})

// Enabling User to create clone 
// Showing user clone_div area to create clone
$("#create_clone").change(function () {
    if ($(this).attr("checked")) {
        $("#clone_div").removeClass("hidden");
    }
    else {
        $("#clone_div").addClass('hidden');
    }

});



$('.move_from').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_from option:selected').remove().appendTo('#move_to');
    $('#move_to option').attr('selected', 'selected');

});

$('.move_to').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_to option:selected').remove().appendTo('#move_from');
    $('#move_to option').attr('selected', 'selected');

});

$('.move_all_from').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_from option').remove().appendTo('#move_to');
    $('#move_to option').attr('selected', 'selected');

});

$('.move_all_to').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_to option').remove().appendTo('#move_from');
    $('#move_to option').attr('selected', 'selected');

});

function check_existance() {
    $('#move_to option').each(function () {
        $('#move_from option[value=' + ($(this).val()) + ']').remove();
    });

}

// Showing user clone_div area to create clone
$("#msp").change(function () {
    if ($(this).val() == "") {
        $("#property").addClass('hidden');
    }
    else {
        $("#property").removeClass("hidden");
        $.get('/admin/move_to_clone_list/', { msp: $(this).val() }, function (data) {
            $('#property').html(data);
            $('#to_clone').select2();
        });
    }


});

// Showing user clone_div area to create clone
$("#msp_create_clone").change(function () {
    if ($(this).val() == "") {
        $("#property").addClass('hidden');
    }
    else {
        $("#property").removeClass("hidden");

    }


});


// Showing user clones for selecting property
$("#to_clone").live('change', function () {

    $("#manage_by_property").removeAttr('checked')
    if ($(this).val() == "") {
        $("#clone_div").addClass("hidden");
    }
    else {
        $("#clone_div").removeClass("hidden");
        $("#property_list").addClass('hidden');
        $('#clone_list').removeClass('hidden');
        $.get('/admin/move_from_clone_list/', {
            msp: $('#msp').val(),
            cln: $('#to_clone').val()
        }, function (data) {
            $('#clone_list').html(data);
            $('#from_clone').select2();
        });
    }


});

// Showing user clones for selecting property
$("#from_clone").live('change', function () {
    if ($(this).val() == "") {
        $("#property_list").addClass("hidden");
    }
    else {
        $('#property_list').removeClass("hidden");
        $.get('/admin/show_properties/', {
            id: $('#from_clone').val(),
            is_master: false
        }, function (data) {
            $('#property_select').html(data);
            check_existance();
        });
    }


});

// Showing user properties area to create clone
$("#manage_by_property").change(function () {
    if ($(this).attr("checked")) {
        $("#clone_list").addClass('hidden');
        $('#property_list').removeClass("hidden");
        $.get('/admin/show_properties/', {
            id: $('#msp').val(),
            cln: $('#to_clone').val(),
            is_master: true
        }, function (data) {
            $('#property_select').html(data);
            check_existance();
        });
    }
    else {
        $("#property_list").addClass('hidden');
        $('#clone_list').removeClass('hidden');
        $.get('/admin/move_from_clone_list/', {
            msp: $('#msp').val(),
            cln: $('#to_clone').val()
        }, function (data) {
            $('#clone_list').html(data);
            $('#from_clone').select2();
        });
    }

});



// Creating the list of clones.
$('#clone_no').keyup(function () {
    var no = $(this).val();
    if (Number(no) > 50) {
        $('#clone_list').html("<strong> Can not create more than 50 clones</strong>");
    }
    else {
        $.get('/admin/master_clone_list/', { clone_no: no }, function (data) {
            $('#clone_list').html(data);
        });
    }
});


// Showing Admin clone list while allocating Agent to Property.
$("#msp_list").change(function () {

    if ($(this).val() == "") {
        $("#property").addClass('hidden');
    }
    else {
        $("#property").removeClass("hidden");
        // if(){
        //     alert($(this).attr('data-unallocated'))}
        $.get('/admin/property_clone_list/', {
            msp: $(this).val(),
            unallocated: $(this).attr('data-unallocated')
        }, function (data) {
            $('#property').html(data);
            $('#cln_list').select2();
        });
    }

});


$(".pr_address").live('keyup', function (e) {
    console.log(e.keyCode)
    if (e.keyCode === 13 && e.shiftKey) {
        var num = $("#num").val();
        // var new_html = '<input type="text" required name="pr_address'+num+'"/><a class="icon-minus-sign remove_address" ></a>';
        var new_html = '<div class="input-append" style="display:flex;" >' +
            '<input class="span2 pr_address" id="appendedInputButton" name="pr_address' +
            num + '" type="text"><button class="btn btn-theme remove_address"' +
            'id="add_address" type="button"><i class="icon-minus"></i></button></div>'
        var new_num = Number(num) + 1;
        $("#num").val(new_num);
        $("#addresses").append(new_html);
        $("#addresses").find('input').last().focus();
    }
    else if (e.keyCode === 8 && e.shiftKey && $('.pr_address').length > 1) {
        $(this).parent().prev().children('.pr_address').focus();
        $(this).parent().remove();
        $(this).remove();
    }
});

// Showing more textboxes when user clicks plus button
$("#add_address").click(function () {
    var num = $("#num").val();
    // var new_html = '<input type="text" required name="pr_address'+num+'"/><a class="icon-minus-sign remove_address" ></a>';
    var new_html = '<div class="input-append" style="display:flex;" >' +
        '<input class="span2 pr_address" id="appendedInputButton" name="pr_address' +
        num + '" type="text"><button class="btn btn-theme remove_address"' +
        'id="add_address" type="button"><i class="icon-minus"></i></button></div>'
    var new_num = Number(num) + 1;
    $("#num").val(new_num);
    $("#addresses").append(new_html);
    $("#addresses").find('input').last().focus();
});

// Removing the textbox on click of minus button
$(".remove_address").live("click", function () {
    $(this).parent().remove();
    $(this).remove();

});



$('.decimal_input').live('keyup', function () {
    var $this = $(this);

    // Get the value.
    var input = $this.val();

    var input = input.replace(/[\D\s\._\-]+/g, "");
    // input = input ? parseInt( input, 10 ) : 0;

    $this.val(function () {
        return (input === 0) ? "" : input.toLocaleString("en-IND");
    });
});

$('.show_data').click(function () {
    var id = $(this).attr('data-id');
    var hidden = $(this).attr('data-hidden');
    var act = $(this).attr('data-act');

    if (hidden == '1') {
        $(this).parent().siblings().children(
            '.show_data').html('<i class="icon-angle-down"></i>');
        $(this).parent().siblings().children(
            '.show_data').attr('data-hidden', '1');
        $("#tr" + id).removeClass("hidden");
        $(this).html('<i class="icon-angle-up"></i>');
        $(this).attr('data-hidden', '0');
        $.get('/admin/show_data/', { id: id, act: act }, function (data) {
            $('#td' + id).html(data);
        });
    }
    else if (hidden == '0') {
        $("#tr" + id).addClass("hidden");
        $(this).html('<i class="icon-angle-down"></i>');
        $(this).attr('data-hidden', '1');
    }
})

$('.edit_property').live('click', function () {
    $('#myModal').css('display', 'block');
    $tr = $(this).parent().parent();
    $("#id").val($(this).attr('data-id'))
    $("#pr_address").val($tr.children('.pr_address').html())
    $("#pr_clone").val($tr.children('.pr_clone').html())
    $("#pr_status").val($tr.children('.pr_status').html())
    $("#pr_rent").val($tr.children('.pr_rent').html())
    $("#pr_deposite").val($tr.children('.pr_deposite').html())
    $("#pr_description").val($tr.children('.pr_description').html())
    // alert($tr.children('.pr_address').html())
    // $('#pr_address').val();
    $ref = $tr;
})

$('#save').click(function () {
    $.get('/admin/edit_property/', {
        id: $("#id").val(),
        rent: parseFloat($("#pr_rent").val()),
        deposite: parseFloat($("#pr_deposite").val()),
        description: $("#pr_description").val()
    }, function (data) {
        if (data == '1') {
            $.notify("Data updated Successfully", "success")
            $tr.children('.pr_rent').html(parseFloat($("#pr_rent").val()).toFixed(2))
            $tr.children('.pr_deposite').html(parseFloat($("#pr_deposite").val()).toFixed(2))
            $tr.children('.pr_description').html($("#pr_description").val())
            $('#myModal').css('display', 'none')
        }
        else {

            $.notify("Data not updated Successfully", "error")
        }
    });

});

$('.close,#close,#close1').click(function () {
    $(this).closest('.modal,.modal2').css('display', 'none');
});

$('.deallocate_clone').live('click', function () {
    if (confirm("Are You sure You want to deallocate this clone?")) {
        $.get('/admin/deallocate_clone/', { id: $(this).attr('data-id') }, function (data) {
            if (data == '1') {
                status = 'Property deallocated ';
                localStorage.setItem("Status", status);
                location.reload('/admin/view_master_property/');
            }
            else {
                $.notify('Error accured while deallocating Property.', 'error')
            }
        })
    }
});
$('.delete_clone').live('click', function () {
    if (confirm("Are You sure You want to delete this clone?\nAll properties from this clone will be transfered to master clone.")) {
        $.get('/admin/delete_clone/', { id: $(this).attr('data-cln'), msp: $(this).attr('data-msp') }, function (data) {
            if (data == '1') {
                status = 'Clone deleted';
                localStorage.setItem("Status", status);
                location.reload('/admin/view_master_property/');
            }
            else {
                $.notify('Error accured while deleting Clone.', 'error')
            }
        })
    }
});

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
    $('#move_to').select2('destroy')
});

$('.allocate_clone').live('click', function () {
    var msp = $(this).attr('data-msp');
    var cln = $(this).attr('data-id');
    location.href = '/admin/allocate_clone/?msp=' + msp + '&cln=' + cln;
});

$('.delete_master').live('click', function () {
    if (confirm('Are you sure to remove this master property?')) {
        var $this = $(this);
        $.get('/admin/delete_master_property/', { id: $(this).attr('data-id') }, function (data) {
            if (data == '1') {
                // location.reload('/admin/view_master_property/');
                $this.parent().parent().next().remove();
                $this.parent().parent().remove();
                $.notify('Property Sold and Removed from system ', 'success');
            }
            else {
                $.notify('Error accured while Deleting Property.')
            }
        })
    }
});




function manage_form() {
    $('#move_to option').attr('selected', 'selected')
}


// Searching in Agent request on search textbox
$('#abc').keyup(function () {
    var query;
    query = $(this).val();
    $.get('/agent/tenant_search_list/', { suggestion: query }, function (data) {
        $('#tbl_tenants').html(data);
    });
});

$('.pimg').live('click', function () {
    $('#imgDiv').css('display', "block");
    $('#img01').attr('src', $(this).attr('src'));
    $('#caption').html($(this).attr('alt'));
});


$(document).ready(function () {
    //get it if Status key found
    var str;
    var code;
    if (localStorage.getItem("Status")) {
        str = localStorage.getItem("Status")
        code = localStorage.getItem('code')
        if (code == null) {
            code = 'success'
        }
        $.notify(str, code);
        // localStorage.setItem('code','success');
        localStorage.clear();
    }
});

$(".allocate_tenant").live('click', function () {
    if ($(this).attr('data-pid')) {
        pid = $(this).attr('data-pid');
        location.href = '/agent/get_Tenant_list/?pid=' + pid + '&page=' + 'pdetails';
    }
    if ($(this).attr('data-tid')) {
        tid = $(this).attr('data-tid');
        location.href = '/agent/get_Tenant_list/?tid=' + tid + '&page=' + 'tdetails';
    }
});

$('.deallocate_tenant').live('click', function () {
    if (confirm("Are you sure you want to deallocate Property?")) {
        if ($(this).attr('data-tid')) {

            tid = $(this).attr('data-tid');
            $.get('/agent/deallocate_property/', { tenant: tid }, function (data) {
                if (data == "1") {
                    status = "Property Deallocated";
                    localStorage.setItem("Status", status);
                    location.reload('/agent/ViewTenants/');
                }
                else {
                    $.notify("Error occured while Deallocation", "error")

                }
            });
        }
        if ($(this).attr('data-pid')) {
            pid = $(this).attr('data-pid');
            $.get('/agent/deallocate_property/', { property: pid }, function (data) {
                if (data) {
                    status = "Property Deallocated";
                    localStorage.setItem("Status", status);
                    location.reload('/agent/Agent_Properties/');
                }
                else {

                    $.notify("Error occured while Deallocation", "error")

                }

            });
        }
    }
});


$('#id_user_permissions_add_link').click(function (e) {
    move_selection(e, this, SelectBox.move, field_id + '_from', field_id + '_to');
});


$('.sold_property').live('click', function () {
    $.get('/admin/property_soldout', { pr_id: $(this).attr('data-id') }, function (data) {
        if (data == "1") {
            status = "Properties Are Alocated";
            localStorage.setItem("Status", status);
            location.reload('/Admin/view_master_property/');
        }
    }
    );
});

$('.addvisit').live('click', function () {
    location.href = '/agent/add_visit/?tid=' + $(this).attr('data-tid');

});

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});


$('.change_status').live('click', function () {
    $("#id").val($(this).attr('data-id'));
    $("#tn_name").val($(this).attr('data-tnname'));
    $("#tn_status").val($(this).attr('data-status'));
    $("#id").attr('data-id', $(this).attr('data-status'));
    $('#tenant_visit').parent().addClass('hidden')
    $('#select2-tn_status-container').html($(this).html())
    $('#myModal').css('display', 'block');
    $('#tenant_visit_label').remove();

});

$('#tn_status').live('change', function () {

    var current_status = $('#id').attr('data-id');
    $('#tenant_visit_label').remove();
    var id = $('#id').val()
    if ($(this).val() == "2") {
        if (current_status == 3 && confirm('Tenant is already allocated. \ndo you want to renew Agrement?')) {

        } else {
            $.get('/agent/get_tenant_visit', { id: id }, function (data) {
                if (data != 0) {

                    $('#tenant_visit').html(data)
                    $('#tenant_visit').select2()
                    $('#tenant_visit').removeClass('hidden')
                    $('#tenant_rent').removeClass('hidden')

                }
                else {
                    try {
                        $('#tenant_visit').select2('destroy')

                    } catch (error) {

                    }
                    $('<strong id = "tenant_visit_label">No unallocated visit found for this user.</strong>').insertAfter('#tenant_visit')
                    $('#tenant_visit').addClass('hidden')
                    $('#tenant_rent').addClass('hidden')
                }
                $('#tenant_visit').parent().removeClass('hidden')

            })
        }
    } else {
        $('#tenant_visit').parent().addClass('hidden')
    }
})

$('#save_tenant_status').live('click', function () {

    id = $('#id').val()
    status = $('#tn_status').val()
    if (status == '0') {
        $.get('/agent/tenant_status_change', { id: id, status: status }, function (data) {
            if (data == '1') {
                status = "Tenant updated";
                localStorage.setItem("Status", status);
                location.reload();
                $.notify("Tenant updated", "success")
            }
            else {
                $.notify("Error occured while updating Tenant Status", "error")
            }
        });
    }
    else if (status == 1) {
        location.href = '/agent/add_visit/?tid=' + id;
    }
    else if (status == 2) {

        var current_status = $('#id').attr('data-id');
        if ($('#tenant_visit_label').length) {
            console.log('now i will ask for adding new visit for this tenant')
            if (confirm('No unallocated visit found.\nDo you want to record a new visit?')) {
                location.href = '/agent/add_visit/?tid=' + id;
            }

        }
        else if (current_status == 3 && ($('#tenant_visit').hasClass('hidden') || $('#tenant_visit').parent().hasClass('hidden'))) {
            console.log('now i ll create new allocation for this tenant on same allocated property')
            $.get('/agent/tenant_status_change', { id: id, status: status, update: true, }, function (data) {
                if (data == '1') {
                    status = "Agreement renew process recorded.";
                    localStorage.setItem("Status", status);
                    location.reload();
                    // $.notify("Tenant updated","success")
                }
                else {
                    $.notify("Error occured while updating Tenant Status", "error")
                }
            });
        }
        else if (current_status != 2) {
            console.log('now will create new allocation on selected')
            if ($('#tenant_visit').val() == "") {
                $.notify('Please select Property to allocate', 'error')
            } else {
                $.get('/agent/tenant_status_change', {
                    id: id, status: status,
                    update: false, property: $('#tenant_visit').val(),
                    rent: $('#rent').val()
                },
                    function (data) {
                        if (data == '1') {
                            status = "New Agreement process recorded.";
                            localStorage.setItem("Status", status);
                            location.reload();
                            // $.notify("Tenant updated","success")
                        }
                        else {
                            $.notify("Error occured while updating Tenant Status", "error")
                        }
                    });
            }
        }
        else {
            console.log('Status of Tenant is not changed.')
            $.notify("Status of tenant is not changed.", "info")
        }
    }
    else if (status == 3) {
        location.href = '/agent/get_Tenant_list/?tid=' + id + '&page=' + 'tdetails';
    }
});

// function allocate_agent() {
//     // alert('before submitting form')
//     var cln = document.forms["agent_allocation"]["pr_msp"].innerText;
//     var msp = document.forms["agent_allocation"]["pr_msp_clone"].innerText;
//     var agent = document.forms["agent_allocation"]["agentx"].innerText;

//     return window.confirm('clone '+cln+' of Master Property '+
//         msp+' Will be alloacted to '+agent+' agent')
// }

// $('#btnsuccess').click(function () {
//     var agent, clone;
//     agent = $('#selectedagent').val();
//     clone = $('#cln_list').val();
//     csrf=$('[name="csrfmiddlewaretoken"]').val();
//         $.post('/admin/allocate_clone/', {csrfmiddlewaretoken:csrf, pr_msp_clone: clone, agentx: agent }, function (data) {
//         if (data) 
//         {
//         alert('Data Inserted Successfully');
//             location.reload();
//             $('#msp_list').get(0).selectedIndex = 0;
//             $('#selectedagent').get(0).selectedIndex = 0;

//         }
//         else {
//             alert('Error in Allocation process');

//         }
//     });
// });
// function mycall() 
// {
//    alert("aaya");
//    var num = $(this).attr("data-num");
//     $(this).prev('input').remove();
// }
//Make class visible for old tenants in insert tenant view
$('#old_tenant').click(function () {
    var response;
    $.get('/agent/get_deactivated_tenant/', function (data) {

        if (data != 0) {
            console.log(data);
            response = '<select id="selected_tenant" style="width:100%" name="tn_id" required>' +
                '<option value="" selected>Select Tenant to make him active.</option>';
            $.each(data, function (item, value) {
                $.each(value, function (i, v) {
                    console.log("Id = " + v.id)
                    console.log("Name = " + v.tn_name)
                    response += '<option value=' + v.id + '>' + v.tn_name + '</option>';
                });
            });
            response += '</select>';
        }
        else {
            response = '<strong id="selected_tenant">No Deactiavted tenant Found.</strong>'
        }
        console.log(response)
        $('#id_tn_name').replaceWith(response);
        $('#selected_tenant').select2();
    });

    // $('#id_tn_name').insertAfter(response);
    $('#id_tn_name').addClass('hidden');
    $('#Add_agent_again').removeClass("hidden");
    $('#Add_new_agent').addClass("hidden");
    $('#Add_agent_again').append("<input type='hidden' id='updatehide' name='update' value='update'></input>")


});

$('#new_tenant').click(function () {
    $('#selected_tenant').select2('destroy');
    $('#selected_tenant').replaceWith("<input type='text' name='tn_name' maxlength='25' id='id_tn_name'>");

    $('selected_tenant').addClass('hidden');

    $('#Add_agent_again').addClass("hidden");
    $('#Add_new_agent').removeClass("hidden");
    $('#id_tn_contact').val("");
    $('#updatehide').remove();
    $('#tenentimage').addClass('hidden');
    $('#id_tn_permanent_address').text("");
    $('#id_tn_reference_name').text("");
    $('#id_tn_reference_address').val("");
    $('#id_tn_reference_name').val("");
    $('#id_tn_document_description').val("");
    $('#select2-id_tn_document_description-container').text("Select");
    $('#id_tn_document').attr('required')
    $('#id_tn_profile').attr('required')
});

$('#selected_tenant').live('change', function () {
    tid = $(this).val()
    $.get('/agent/activate_tenant/', { tid: tid }, function (data) {
        $('#id_tn_contact').val(data.tn_contact);
        $('#id_tn_name').val(data.tn_name);
        $('#id_tn_permanent_address').text(data.tn_permanent_address);
        $('#id_tn_reference_name').text(data.tn_reference_name);
        $('#id_tn_reference_address').val(data.tn_reference_address);
        $('#id_tn_reference_name').val(data.tn_reference_name);
        $('#id_tn_document_description').val(data.tn_document_description);
        $('#select2-id_tn_document_description-container').text($('#id_tn_document_description option:selected').text());
        var url = '/media/';
        $('#tenant_profile').attr('src', url + data.tn_profile)
        $('#tenant_document').attr('src', url + data.tn_document)
        $('#tenentimage').removeClass('hidden')
        $('#id_tn_document').removeAttr('required')
        $('#id_tn_profile').removeAttr('required')
    })
});


// Searching in Agent request on search textbox
$('.search_tenant').live('keyup', function () {
    var status = $(this).attr('data-status');
    var query;
    query = $(this).val();
    $.get('/agent/tenant_search_list/', { suggestion: query, status: status }, function (data) {
        if (status == "all") {
            $('#tbl_tenants').html(data);
        }
        if (status == "active") {
            $('#tbl_active_tenants').html(data);
        }
        if (status == "inactive") {
            $('#tbl_inactive_tenants').html(data);
        }

    });
});


//view Property allocation vise
$('.propertyradio').live('click', function () {
    var propertytype = $(this).attr('data-value');
    $.get('/agent/Agent_Properties/', { propertytype: propertytype }, function (data) {
        $('#propertylist').html(data);
    })
});

//check if allocated and redirection for rent
$('.add_rent').live('click', function () {
    var pid = $(this).attr('data-pid');
    var tid = $(this).attr('data-tid');
    if (pid) {
        $.get('/agent/check_allocation/', { pid: pid }, function (data) {
            if (data == "1") {
                location.href = '/agent/add_rent/?pid=' + pid;
            }
            else {
                alert("This Property's Agreement is under Process.");
            }
        });

    };
    if (tid) {
        // $.get('/Agent/add_rent/', { tid: tid });
        location.href = '/agent/add_rent/?tid=' + tid;

    };
})

$('.view_visit').live('click', function () {
    $.get('/agent/view_visits/', { status: $(this).attr('data-req'), year: $('#visit_year').val() }, function (data) {
        $('#visitlist').html(data)
    });

})

$("#visit_year").change(function () {
    location.href = '/agent/view_visits/?year=' + $(this).val();
});

function addrentclick() {
    // alert("Hello")
    $.get('/agent/getAllocatedtenants/', {}, function (data) {
        // alert(data)
        console.log(data);
        $('#tenantid').html(data)
        $('#tenantid').select2()
        $('#mymodalforaddrent').css('display', 'block');
    })
};

$('#tenantid').live('change', function () {
    // alert($('#tenantid').val())
    $.get('/agent/getAllocatedtenants/', { tenantid: $('#tenantid').val() }, function (data) {
        console.log(data);
        $('#allocated_property_name').val(data)
        $('#allocated_property_name').removeClass('hidden')
    })
})

$('#addrent').live('click', function () {
    $('#allocated_property_name').addClass('hidden')
    $('#mymodalforaddrent').css('display', 'none');
    tid = $('#tenantid').val()
    location.href = '/agent/add_rent/?tid=' + tid;
})

$('.allocation_details').live('click', function () {
    pid = $(this).attr('data-pid');
    location.href = '/agent/viewallocationDetails/?pid=' + pid;
})



$('.deactivate').live('click', function () {
    if (confirm("Are you sure you want to deactivate this Tenant ?")) {
        var id = $(this).attr('data-id')
        $.get('/agent/activation_change_tenant/', { id: id, change: 'deactivate' }, function (data) {
            if (data == "1") {
                status = "Tenant Dectivated";
                localStorage.setItem("Status", status);
                location.reload('/agent/ViewTenants/');
            }
            else
                $.notify('Error occured during deactivation', 'error');
        })
    }
})

$('.activate').live('click', function () {
    if (confirm("Are you sure you want to activate this Tenant Again?")) {
        var id = $(this).attr('data-id')
        $.get('/agent/activation_change_tenant/', { id: id, change: 'activate' }, function (data) {
            if (data == '1') {
                status = "Tenant Activated";
                localStorage.setItem("Status", status);
                location.reload('/agent/ViewTenants/');
            }
            else
                $.notify('Error occured during deactivation', 'error');
        })
    }
});

$('.renew_agreement').live('click', function () {
    $.get('/agent/tenant_status_change', { id: $(this).attr('data-id'), status: 2, update: true, }, function (data) {
        if (data == '1') {
            status = "Agreement renew process recorded.";
            localStorage.setItem("Status", status);
            location.reload();
            $(this).remove();
            // $.notify("Tenant updated","success")
        }
        else {
            $.notify("Error occured while updating Tenant Status", "error")
        }
    });
});


$('#allocate_unmanaged_tenant').live('click', function () {
    if ($('#selectedagent').val() == "") {
        alert('Please select the agent first.')
    }
    else {
        if (confirm('Are you sure to allocate these tenents to selected agent?\nYou will not be able to undo this allocation.')) {
            var selected = new Array();
            $('.unmanaged_tenant:checked').each(function () {
                selected.push($(this).val())
            });
            $.get('/admin/allocate_unamanaged_tenant', { tenants: selected.toString(), agent: $('#selectedagent').val() }, function (data) {
                if (data == '1') {
                    status = "Selected tenants are allocated";
                    localStorage.setItem("Status", status);
                    location.reload();
                    // $.notify("Tenant updated","success")
                }
                else {
                    $.notify("Something went wrong while allocating agents", "error")
                }
            });
        }


    }

});

$('#id_ag_contact').live('keyup', function () {
    $(this).attr('maxlength', '10');
    var $this = $(this);

    // Get the value.
    var input = $this.val();

    var input = input.replace(/[\D\s\._\-]+/g, "");
    // input = input ? parseInt( input, 10 ) : 0;

    $this.val(function () {
        return (input === 0) ? "" : input.toLocaleString("en-IND");
    });
})

$('#tenant_contact').live('keyup', function () {
    $(this).attr('maxlength', '10');
    var $this = $(this);

    // Get the value.
    var input = $this.val();

    var input = input.replace(/[\D\s\._\-]+/g, "");
    // input = input ? parseInt( input, 10 ) : 0;

    $this.val(function () {
        return (input === 0) ? "" : input.toLocaleString("en-IND");
    });
})

$('#tenant_submit').click(function () {
    var name = $('#tenant_name').val();
    var contact = $('#tenant_contact').val();
    $.get('/tenant/'+name+'/', { tenant_contact: contact }, function (data) {
        $('#tenant_details').html(data);
    });
})

// $('#pselect_id').on("change.select2", function(e) { 
//     alert(this.value,$(this).attr('data-rent'))
//  });
            