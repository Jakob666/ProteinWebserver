// 从cookie中获取username
function get_uname(){
    var cook_info = document.cookie;
    cook_info = cook_info.split(";");
    var username;
    // 首先从cookie中获取用户名
    for (var i = 0; i < cook_info.length; i++) {
        var info = cook_info[i].trim().split("=");
        if (info[0] == "cname") {
            username = info[2].split('"')[0];
            console.log(username);
        }
    }
    return username;
}
