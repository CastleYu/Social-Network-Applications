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

})