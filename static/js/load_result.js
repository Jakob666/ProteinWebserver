// 加载分析结果，有两个方法分别加载最终结果和报错结果
function load_analysis_result() {
    var username = get_uname();
    $.ajax({
        type: "post",
        url: "/get_result/load_result/",
        dataType: "json",
        data: {"username": username},
        async: false,
        success: function (ret) {
            table_appear();
            summary_appear();
            loading_vanish();
            var row = ret.row_num;
            var data = ret.test_result;
            var summary = ret.summary;
            var detail_info = document.getElementById("table_body");
            var summary_info = document.getElementById("summary_tbody");

            // 将表格内容清空，仅留下表头
            $("#table_body").empty();
            for (var i = 0; i < row; i++){
                var tr = document.createElement("tr");
                for (var j = 0; j < 7; j++){
                    var td = document.createElement("td");
                    td.innerHTML = data[i][j];
                    tr.appendChild(td);
                }
                detail_info.appendChild(tr);
            }
            $("#result_table").append(detail_info);

            $("#summary_tbody").empty();
            for (var i = 0; i < summary.length; i++){
                var tr = document.createElement("tr");
                for (var j = 0; j < 5; j++){
                    var td = document.createElement("td");
                    td.innerHTML = summary[i][j];
                    tr.appendChild(td);
                }
                summary_info.appendChild(tr);
            }
            $("#summary_table").append(summary_info);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest.status);
            console.log(XMLHttpRequest.readyState);
            console.log(textStatus);
            console.log("加载分析结果失败");
        }
    })
}

// 如果分析失败，查看日志得到失败原因
function load_fail_result() {
    var username = get_uname();
    $.ajax({
        type: "post",
        url: "/get_result/check_reason/",
        dataType: "json",
        data: {"username": username},
        async: false,
        success: function (ret) {
            var reason = ret.fail_reason;
            loading_vanish();
            $("#fail_reason").css("visibility", "visible");
            $("#fail_reason p").text(reason);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest.status);
            console.log(XMLHttpRequest.readyState);
            console.log(textStatus);
            console.log("加载出错日志失败");
        }
    })
}
