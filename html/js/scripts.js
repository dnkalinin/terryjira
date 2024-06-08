$("document").ready(function () {
    /* вешаем событие на ранее созданную форму */
    $("#upload").on("submit", function () {
      /* создаём объект с данными из полей */
      let formData = new FormData(upload)
      /* добавляем дополнительные данные для отправки */
      formData.append("url_query", "prog-time");
      /* записываем в переменные данные из формы */
      let allfiles = $(this).find('input[name="file"]');
      formData.append("file", allfiles[0].files[0]);
      let offset = new Date().getTimezoneOffset();
      let offsetHours = -(offset / 60); // Преобразуем в часы и меняем знак на противоположный
      formData.append("timezone", offsetHours);
      formData.append("projects", document.getElementById('column-projects').value);
      formData.append("work", document.getElementById('column-work').value);
      formData.append("startdate", document.getElementById('column-startdate').value);
      formData.append("starttime", document.getElementById('column-starttime').value);
      formData.append("enddate", document.getElementById('column-enddate').value);
      formData.append("endtime", document.getElementById('column-endtime').value);
      /* отправляем AJAX запрос */
      $.ajax({
        type: "POST",
        url: '/upload',
        contentType: false,
        processData: false,
        data: formData,
        success: function (data) {
          document.getElementById('worklogs').innerHTML = data;
          document.getElementById('upload2jira').style.visibility = "visible";
          document.getElementById('progress-bar').innerHTML = '0';
          document.getElementById('progress-bar').setAttribute("style", "width: 0%");
        },
        error: function (error) {
          document.getElementById('upload2jira').style.visibility = "hidden";
          document.getElementById('worklogs').innerHTML = "File not uploaded: " + error.responseText;
          document.getElementById('progress-bar').innerHTML = '0';
          document.getElementById('progress-bar').setAttribute("style", "width: 0%");
        }
      });
    }),
    /* вешаем событие на ранее созданную форму */
    $("#upload2jira").on("submit", function () {
      /* создаём объект с данными из полей */
      let formData = new FormData(upload)
      /* добавляем дополнительные данные для отправки */
      formData.append("url_query", "prog-time");
      formData.append("jiraurl", document.getElementById('jira-url').value);
      formData.append("jiratoken", document.getElementById('jira-token').value);
      formData.append("worklogs", document.getElementById('worklogs').innerHTML);
      document.getElementById('upload2jira').style.visibility = "hidden";
      document.getElementById('bd-spinner').style.visibility = "visible";

      var object = {};
      formData.forEach((value, key) => {
          // Reflect.has in favor of: object.hasOwnProperty(key)
          if(!Reflect.has(object, key)){
              object[key] = value;
              return;
          }
          if(!Array.isArray(object[key])){
              object[key] = [object[key]];    
          }
          object[key].push(value);
      });
      var json = JSON.stringify(object);
      var total = 0;
      var i = 0;

      $.ajax({
        type: 'POST',
        url: '/upload2jira',
        data: json,
        chunking: true,
        contentType: 'application/json; charset=utf-8',        
        success: function (data) {
          document.getElementById('progress-bar').innerHTML = 'Success!';
        },
        progress: function (e, context) {
          var responseData = e.currentTarget.responseText.split(' ')
          total = responseData[0];
          dataLen = responseData.length;
          if (dataLen > 1) {
            i = dataLen - 2
            if (i - 2 >= total) {
              i = total
            }
            document.getElementById('bd-spinner').style.visibility = "hidden";
            document.getElementById('progress').style.visibility = "inherit";
            document.getElementById('progress-bar').innerHTML = i + "/" + total;
            document.getElementById('progress-bar').setAttribute("style", "width: " + Math.round((i * 100) / total) + '%; visibility: visible;');
          }
        }
      });
    });
    $(".custom-file-input").on("change", function () {
      var fileName = $(this).val().split("\\").pop();
      $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    });
    $.ajax({
      type: "GET",
      url: '/init',
      contentType: false,
      processData: false,
      success: function (data) {
        var values = JSON.parse(data)
        document.getElementById('column-projects').placeholder = values.columns.jiraprojects;
        document.getElementById('column-work').placeholder = values.columns.work;
        document.getElementById('column-startdate').placeholder = values.columns.startdate;
        document.getElementById('column-starttime').placeholder = values.columns.starttime;
        document.getElementById('column-enddate').placeholder = values.columns.enddate;
        document.getElementById('column-endtime').placeholder = values.columns.endtime;
        document.getElementById('jira-url').placeholder = values.jiraurl;
        document.getElementById('jira-token').placeholder = values.jiratoken;
      }
    });
});
