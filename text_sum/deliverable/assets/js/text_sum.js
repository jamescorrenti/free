"use strict";
var url = 'http://localhost:81/';
var file_data = {};
var ratio = 0.0;
update_summary();

//language=JQuery-CSS
$('#upload_form').submit(function() {
    var file = document.getElementById("file");
    if (file.files[0] !== undefined)
        var f = file.files[0];
    else{
        alert('Need to upload a file');
        return
    }

    if (!f.type.match('text/plain')) {
        alert('Not supported filetype');
        return;
    }


    ratio = document.getElementById("summary_ratio").value.replace('%', '') / 1000.0;
    var formData = new FormData();
    formData.append('file', f, f.name);

    var out = new XMLHttpRequest();
    out.onreadystatechange = function () {
        if (out.readyState === 4 && out.status === 200) {
            update_summary(out.responseText);
        }
    };

    out.open("POST", url + 'upload', true);
    out.send(formData);

});

$('#TabNav').click(function (e) {
  e.preventDefault();
  $(this).tab('show')
});

function update_summary(r){
    var summary_html, key_html, report_html;
    if (r !== undefined){
        file_data = JSON.parse(r);
        summary_html = "";
        var sentence_pass = 0;
        for (var i=0; i < file_data.total_sentences; i++){
            if (file_data.sentence_scores[i] > ratio){
                sentence_pass +=1;
                summary_html += `${file_data.all_sentences[i]}<br>`;
            }
        }
        if (!summary_html.length) summary_html = "No sentences meet the ratio";

        // keywords - words used more than three times
        key_html = "";

        for (var key in file_data.word_usage){
            if( file_data.word_usage[key] >=3 ){
                key_html += `${key} : ${file_data.word_usage[key]}<br>`;
            }
        }
        if (!key_html.length) key_html = "No words used over 3 times";

        // report - total number of sentences and words, sentences pass ratio
        report_html = `Total Number of words: ${file_data.total_word}<br>Total Number of nouns: ${file_data.total_nouns}<br>Total Number of sentences: ${file_data.total_sentences}<br>Total Number of sentences that pass ratio: ${sentence_pass}`;

    }
    else {
        summary_html = "No summmary yet, click Get Summary to run text summarization";
        key_html = "No analysis run yet, click Get Summary to run text summarization";
        report_html = "No Report run yet, click Get Summary to run text summarization";
    }

    document.getElementById('summary-inner').innerHTML = summary_html;
    document.getElementById('keywords-inner').innerHTML = key_html;
    document.getElementById('report-inner').innerHTML = report_html;

}