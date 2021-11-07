let values = {};
$('#cobra-form').submit((e) => {
  e.preventDefault();
  const serializedArray = $('#cobra-form').serializeArray();
  $.each(serializedArray, (index, field) => {
    values[field.name] = +field.value;
  });
  console.log(values);
});
