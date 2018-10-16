// 下载用户最新记录
function latest_download() {
    var username = get_uname();
    console.log(username);
    var target_url = "/user_download/" + username + "/latest_download/";
    console.log(target_url);
    window.location.href = target_url;
}

// 下载用户历史记录
function history_download() {
    var username = get_uname();
    var submit_time = $("#submit_time").text();
    submit_time = submit_time.split("\s");
    console.log(submit_time);
    var target_url = "/user_download/" + submit_time + "/" + username + "/history_download/";
    console.log(target_url);
    window.location.href = target_url;
}