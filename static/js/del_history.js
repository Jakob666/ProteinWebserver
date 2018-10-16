// 删除历史记录
function del_history() {
    $("#history_record").empty();
    var username = get_uname();
    $.ajax({
        type: "post",
        url: "/user_history/del_history/",
        data: {"username": username},
        async: true,
        success: function () {
            console.log("删除用户历史任务记录");
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest.status);
            console.log(XMLHttpRequest.readyState);
            console.log(textStatus);
            console.log(errorThrown);
            console.log("历史任务删除失败");
        }
    })
}
