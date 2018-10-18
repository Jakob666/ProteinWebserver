// 用于加载示例文件
function showExample(exampleType) {
    $.ajax({
        type: "post",
        url: "/get_example/",
        data: {"exampleType": exampleType},
        asyns: false,
        success: function (ret) {
            $("#id_input_text").val(ret);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log(XMLHttpRequest.status);
            console.log(XMLHttpRequest.readyState);
            console.log(textStatus);
            console.log(errorThrown);
            console.log("样例文件导出失败");
        }
    });
}