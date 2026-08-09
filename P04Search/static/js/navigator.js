$(document).ready(function () {

    const defaultConfig = {
        map: {
            type: 'get',
            dataType: 'json',
        }
    }
    const appenderConfig = {
        beforeSendDo: function (button) {
            button.attr("disabled", "disabled");
        },
        completeDo: function (button) {
            button.removeAttr("disabled");
        },
        errorDo: function (jqXHR, textStatus, e) {
            console.log("请求时异常");
            console.log({"jqXHR": jqXHR, "textStatus": textStatus, "e": e});
            alert("失败：请求时异常")
        }
    }

    function doFunctionOrLog(obj, source) {
        if (obj === undefined) {

        } else if (typeof obj === 'function') {
            obj(source);
        } else if (typeof obj === 'string') {
            console.log(obj);
        }
    }

    function buildRequest(config) {
        let sendData = config.dataProvider ? config.dataProvider(config.source) : {};
        let urlMap = {
            ...defaultConfig.map,
            ...config.map,
            data: sendData
        }
        let behavior = {
            beforeSend: function () {
                doFunctionOrLog(config.behavior.beforeSendDo, config.source);
                appenderConfig.beforeSendDo(config.source.button);
            },
            complete: function () {
                doFunctionOrLog(config.behavior.completeDo, config.source)
                appenderConfig.completeDo(config.source.button);
            },
            success: function (result) {
                (config.behavior.successDo[result.status] || config.behavior.successDo.default || function () {
                })(result, config.source);
            },
            error: function (jqXHR, textStatus, e) {
                doFunctionOrLog(config.errorDo, config.source)
                appenderConfig.errorDo(jqXHR, textStatus, e);
            },
        }
        return {...urlMap, ...behavior}
    }

    function sendRequest(config) {
        let options = buildRequest(config)
        $.ajax(options);
    }

    function setButtonCall(trigger, config, type = "click") {
        trigger.on(type, function () {
            config.source.button = trigger;
            sendRequest(config)
        });
    }

    //业务函数
    function updateForm(result, targets) {
        let dataList = result.text;
        let dataOldList = targets.formField();
        if (dataOldList && dataOldList.length > 0) {
            dataOldList.remove();
        }
        // 创建搜索结果的表格并插入到前端页面
        for (let i = 0; i < dataList.length; i++) {
            let rowHtml = '<tr class="weibo-entry">'
                + '<td><a href="' + dataList[i].blogger_homepage + '">' + dataList[i].blogger_nickname + '</a></td>'
                + '<td>' + dataList[i].weibo_content + '</td>'
                + '<td>' + dataList[i].publish_time + '</td>'
                + '<td>' + dataList[i].weibo_source + '</td>'
                + '<td>' + dataList[i].repost_count + '</td>'
                + '<td>' + dataList[i].comment_count + '</td>'
                + '<td>' + dataList[i].like_count + '</td>'
                + '</tr>';
            targets.formBody.append(rowHtml);
        }
    }

    //配置区
    setButtonCall($('#create_new_index'), {
        map: {
            type: 'post',
            url: '/buildindex',
        },
        dataProvider: (source) => ({
            "id": source.button.attr("id")
        })
    })

    setButtonCall($('#search_btn'), {
        map: {
            type: 'get',
            url: '/searchindex',
        },
        behavior: {
            beforeSendDo: (source) => {
                console.log(`正在搜索${source.inputBox.val()}`)
            },
            successDo: {
                200: updateForm,
                201: () => alert("检索不到任何结果!"),
                default: () => alert("检索失败")
            },
        },
        dataProvider: (source) => ({
            "keyword": $.trim(source.inputBox.val()),
            "searchMethod": 0
        }),
        source: {
            inputBox: $('#input_box'),
            formField: () => $('tr.weibo-entry'),
            formBody: $("#weibo-result-list-table")
        }
    })


    $(document).on("click", "input.btn-rec", function () {
        let weibo_id = $(this).attr("id");
        $.ajax({
            type: "get",
            url: "/getrecmendation", // URL需要与你Django视图中的URL匹配
            data: {
                "id": weibo_id
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
                    console.log('successful');
                    var weibo_data = result.data;
                    var replace_html = '<table id="weibo-result-list-table" border="1" cellspacing="1" cellpadding="1">        <tr>\n' +
                        '            <th>博主昵称</th>\n' +
                        '            <th>微博内容</th>\n' +
                        '            <th>发布时间</th>\n' +
                        '            <th>微博来源</th>\n' +
                        '            <th>转发</th>\n' +
                        '            <th>评论</th>\n' +
                        '            <th>赞</th>\n' +
                        '            <th>操作</th>\n' +
                        '        </tr>' +
                        '<tr class="weibo-entry" id="' + weibo_data.id + '">'
                        + '<td width="200px"><a href="' + weibo_data.blogger_homepage + '">' + weibo_data.blogger_nickname + '</a></td>'
                        + '<td>' + weibo_data.weibo_content + '</td>'
                        + '<td>' + weibo_data.publish_time + '</td>'
                        + '<td>' + weibo_data.weibo_source + '</td>'
                        + '<td>' + weibo_data.repost_count + '</td>'
                        + '<td>' + weibo_data.comment_count + '</td>'
                        + '<td>' + weibo_data.like_count + '</td>'
                        + '<td>'
                        + '<input id="' + weibo_data.id + '" type="button" class="btn btn-success btn-pos" value="词性标注"/>'
                        + '<input id="' + weibo_data.id + '" type="button" class="btn btn-success btn-entity" value="实体识别"/>'
                        + '<input id="' + weibo_data.id + '" type="button" class="btn btn-success btn-rec" value="相关推荐"/>'
                        + '</td>'
                        + '</tr>' +
                        '</table>';
                    $("#entry-rec").append(replace_html);
                } else {
                    alert("No result");
                }
            },
            error: function (jqXHR, textStatus, e) {
                alert("提交异常：" + e);
            }
        });
    });


})