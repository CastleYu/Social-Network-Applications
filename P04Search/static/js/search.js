$(document).ready(function () {
    // 点击索引按钮，发请求
    $("#create_new_index").on("click", function () {
        $.ajax({
            type: "post",
            url: "/buildindex",
            data: {"id": $("#create_new_index").attr("id")},
            dataType: "json",
            beforeSend: function () {
                console.log("已发出建立索引的请求");
                $("#create_new_index").attr("disabled", "disabled");
            },
            complete: function () {
                $("#create_new_index").removeAttr("disabled");
            },
            success: function (result) {
                if (result.status === 200) {
                    console.log(result.text);
                } else {
                    alert("索引失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常：" + e);
            }
        });
    });

    // 点击检索按钮，发请求
    $("#search_btn").on("click", function () {
        let keyword = $.trim($('#input_box').val()); // 确保使用正确的输入字段id
        if (keyword === "")
            return;
        $.ajax({
            type: "get",
            url: "/searchindex",
            data: {
                "keyword": keyword
            },
            dataType: "json",
            beforeSend: function () {
                $("#search_btn").attr("disabled", "disabled");
            },
            complete: function () {
                $("#search_btn").removeAttr("disabled");
            },
            success: function (result) {
                if (result.status === 200) {
                    var weibo_list = result.text;
                    var weibo_oldlist = $("tr.weibo-entry");
                    if (weibo_oldlist && weibo_oldlist.length > 0) {
                        $("tr.weibo-entry").remove(); // 清空原有的微博条目
                    }
                    // 创建搜索结果的表格并插入到前端页面
                    for (var i = 0; i < weibo_list.length; i++) {
                        var search_html = '<tr class="weibo-entry" id="' + weibo_list[i].id + '">'
                            + '<td><a href="' + weibo_list[i].blogger_homepage + '">' + weibo_list[i].blogger_nickname + '</a></td>'
                            + '<td>' + weibo_list[i].weibo_content + '</td>'
                            + '<td>' + weibo_list[i].publish_time + '</td>'
                            + '<td>' + weibo_list[i].weibo_source + '</td>'
                            + '<td>' + weibo_list[i].repost_count + '</td>'
                            + '<td>' + weibo_list[i].comment_count + '</td>'
                            + '<td>' + weibo_list[i].like_count + '</td>'
                            + '<td>'
                            + '<input id="' + weibo_list[i].id + '" type="button" class="btn btn-success btn-pos" value="词性标注"/>'
                            + '<input id="' + weibo_list[i].id + '" type="button" class="btn btn-success btn-entity" value="实体识别"/>'
                            + '</td>'
                            + '</tr>';
                        $("#weibo-result-list-table").append(search_html);
                    }
                    console.log("检索成功");
                } else if (result.status === 201) {
                    alert("检索不到任何结果!");
                } else {
                    alert("检索失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常：" + e);
            }
        });
    });

    // 词性标注按钮响应事件
    $(document).on("click", "input.btn-pos", function () {
        $.ajax({
            type: "get",
            url: "/posannotation",
            data: {
                "id": $(this).attr("id")
            },
            dataType: "json",
            beforeSend: function () {
                // 设置disabled阻止用户继续点击
                $(this).attr("disabled", "disabled");
            },
            complete: function () {
                // 请求完成移除 disabled 属性
                $(this).removeAttr("disabled");
            },
            success: function (result) {
                if (result.status === 200) {
                    console.log("成功");
                    var data = result.data;
                    $("tr.weibo-entry#" + data.id + " td:eq(1)").html(data.weibo_content);
                } else {
                    alert("失败");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常：" + e);
            }
        });
    });


    $(document).on("click", "input.btn-rec", function () {
        let movie_id = $(this).attr("id");
        console.log(movie_id);
        $.ajax({
            type: "get",
            url: "/getrecmendation",
            data: {
                "id": movie_id
            },
            dataType: "json",
            beforeSend: function () {
                // 设置disabled阻止用户继续点击
                $(this).attr("disabled", "disabled");
            },
            complete: function () {
                // 请求完成移除 disabled 属性
                $(this).removeAttr("disabled");
            },
            success: function (result) {
                if (result.status == 200) {
                    console.log('successful');
                    var movie_data = result.data;
                    var replace_html = '<tr>'
                        + '<td>' + movie_data.id + '</td>'
                        + '<td>' + movie_data.movie_title + '</td>'
                        + '<td>' + movie_data.movie_directors + '</td>'
                        + '<td>' + movie_data.movie_actors + '</td>'
                        + '<td>' + movie_data.movie_description + '</td>'
                        + '</tr>';
                    $("#movie-rec").append(replace_html);
                } else {
                    alert("No result");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常：" + e);
            }
        });
    });

});
