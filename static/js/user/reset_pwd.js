;
var user_reset_pwd_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".user_reset_pwd_wrap #save").click(function(){
            var btn_target = $(this)
            if (btn_target.hasClass("disable")){
                common_ops.alert("正的处理中，请勿重复提交");
                return ;
            }

            var new_password_target = $("#new_password");
            var new_password = new_password_target.val();

            var old_password_target = $("#old_password");
            var old_password = old_password_target.val();

            console.log(new_password)
            if( !new_password || new_password.length <6){
                common_ops.alert("请输入合法的新密码123");
                return false;
            }

            if( !old_password || old_password.length <6){
                common_ops.alert("请输入合法的旧密码");
                return false;
            }

            if( old_password == new_password){
                common_ops.alert("新密码不能与旧密码相同")
                return false;
            }

            btn_target.addClass('disabled')

            $.ajax({
                url:common_ops.buildUrl("/user/reset-pwd"),
                type:"POST",
                data:{'new_password':new_password, "old_password":old_password},
                dataType:'json',
                success:function(res){
                    btn_target.removeClass('disabled')
                    var callback = null;
                    if (res.code == 200){
                        callback=function(){
                         window.location.href = common_ops.buildUrl("/");
                        }
                    }
                    common_ops.alert(res.msg,callback);
                }
            });

        });
    }
};

$(document).ready( function (){
    user_reset_pwd_ops.init();

}

)