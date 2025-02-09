// $(document).ready(function(){
//     $('#show_password').change(function(){
//         var passwordField = $('#floatingPassword');
//         var passwordFieldType = passwordField.attr('type');
//         if ($(this).is(':checked')) {
//             passwordField.attr('type', 'text');
//         } else {
//             passwordField.attr('type', 'password');
//         }
//     });
// });

function showPassWrd(element) {
  var CheckBox = $(`#${element.id}`);
  var Password = $("#password");

  Password.attr("type", "password");
  if (CheckBox.is(":checked")) {
    Password.attr("type", "text");
  }
}

$(document).ready(function () {
  $("#Form").attr("action", UrlAction());
});

function UrlAction() {
  return $(location).attr("href");
}
