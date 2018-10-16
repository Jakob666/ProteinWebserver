// 读取日志获取相关数据
// 定义一个读取日志的方法，检测是否分析成功，成功返回true；不成功返回false
function readLog() {
    var username = get_uname();
    $.ajax({
        type: "post",
        url: "/check_log/log_res/",
        dataType: "json",
        data: {"username": username},
        async: true,
        success: function (ret) {
            running_img_vanish();
            $("#task_status").text("finished");
            loading_appear();
            console.log("日志查询成功");
            obj.if_check = ret.log_result;
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest.status);
            console.log(XMLHttpRequest.readyState);
            console.log(textStatus);
            console.log("日志查询失败");
            obj.if_check = false;
        }
    });
}
