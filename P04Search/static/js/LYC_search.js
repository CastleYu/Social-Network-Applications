$(document).ready(function(){
    // 点击索引按钮，发请求
    $("#submit2index").on("click", function () {
        $.ajax({
            type: "post",
            url: "/buildindex",
            data: {"id": $("#submit2index").attr("id")},
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $("#submit2index").attr("disabled", "disabled");
            }, 
            complete: function () {
                // 请求完成移除 disabled 属性
                $("#submit2index").removeAttr("disabled");
            },  
            success: function(result){
                if(result.status === 200){
                    console.log(result.text);
                }else{
                    alert("索引失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })
    // 点击检索按钮，发请求
    $("#btn-submit2search").on("click", function () {
        var keyword = $.trim($('input[name="submit2search"]').val());
        if (keyword == "")
            return;
        $.ajax({
            type: "get",
            url: "/searchindex",
            data: {
                "id": $("#submit2search").attr("id"), 
                "keyword": keyword
            },
            dataType: "json",
            beforeSend: function() {
                // 设置disabled阻止用户继续点击
                $("#btn-submit2search").attr("disabled", "disabled");
            }, 
            complete: function () {
                // 请求完成移除 disabled 属性
                $("#btn-submit2search").removeAttr("disabled");
            },  
            success: function(result){
                if(result.status == 200){
                    var movie_list = result.text;
                    var movie_oldlist = $("tr.movie-entry");
                    if (movie_oldlist && movie_oldlist.length>0) {
                        // 清空原有表格
                        $("tr.movie-entry").remove();
                        $("ul.pagination").remove();
                    }
                    // 创建搜索结果的表格并插入到前端页面
                    for (var i = 0; i < movie_list.length; i++) {
                        var search_html = '<tr class="movie-entry">' 
                        + '<td>' + movie_list[i].id + '</td>' 
                        + '<td>' + movie_list[i].movie_title + '</td>'
                        + '<td>' + movie_list[i].movie_directors + '</td>'
                        + '<td>' + movie_list[i].movie_actors + '</td>'
                        + '<td>' + movie_list[i].movie_description + '</td>' 
                        + '</tr>';
                        $("table#moview-result-list-table").append($(search_html))
                    }
                    console.log("检索成功");
                }else if(result.status == 201){
                    alert("检索不到任何结果!");
                }
                else{
                    alert("检索失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常："+e);
            }
        });
    })
})
