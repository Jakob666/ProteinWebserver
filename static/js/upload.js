// 用户上传相关的方法
function upload(obj) {
    var input_text = $('#id_input_text').val();
    var elm_file = $('#id_elm_file')[0].files[0];
    var vcf_file = $('#id_vcf_file')[0].files[0];
    var tab_file = $('#id_tab_file')[0].files[0];
    var organism = $('#id_organism').val();
    var cancer = $('#id_cancer').val();
    var threshold = $('#id_threshold').val();
    var email = $('#id_email').val();
    var modification = $('#id_modification').val();

    $.ajax({
        method: "post",
        url: "/webserver/user_upload/",
        processData: false,
        data: {"input_text": input_text, "elm_file": elm_file, "vcf_file": vcf_file,
               "tab_file": tab_file, "modification": modification, "cancer": cancer,
               "threshold": threshold, "email": email, "organism": organism
        },
        async: true,
        success: function () {
          console.log("上传完成");
          obj.if_upload = true;
        },
        error:function (r1) {
            // 请求失败，if_upload变量的值为false
            obj.if_upload = false;
        }
    });
}
