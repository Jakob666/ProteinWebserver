// result.html页面中的一些效果
// 动态的running GIF图片消失
function running_img_vanish() {
    $("#processing_img").css("visibility", "hidden");
    $("#processing_img").hide("slow");
}

// 在最终结果加载出来之前loading GIF显现
function loading_appear(){
    $("#wait_loading").css("visibility", "visible");
}

// 在最终结果加载出来之前loading GIF显现
function loading_vanish(){
    $("#wait_loading").hide("fast");
}

// 分析成功后现实表格并加载结果文件
function table_appear() {
    $("#result_table").css("visibility", "visible");
}
function summary_appear() {
    $("#summary_table").css("visibility", "visible");
}