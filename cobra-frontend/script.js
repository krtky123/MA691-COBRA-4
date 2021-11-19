let values = {};

$('#cobra-form').submit((e) => {
  // Show loading results
  $('#result').removeClass('visually-hidden');
  $('#message').html(
    '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>'
  );

  e.preventDefault();
  const serializedArray = $('#cobra-form').serializeArray();

  $.each(serializedArray, (index, field) => {
    if (['age', 'amount', 'duration'].includes(field.name)) values[field.name] = +field.value;
    else values[field.name] = field.value;
  });

  console.log(values);

  // send a POST request
  axios({
    method: 'post',
    url: 'https://pacific-dawn-32033.herokuapp.com/predict_german',
    data: values,
  }).then(
    (response) => {
      response_object = JSON.parse(response.data);
      response_bool = response_object['Predicted Status']['0'];

      if ($('#result').hasClass('alert-success')) $('#result').removeClass('alert-success');
      if ($('#result').hasClass('alert-danger')) $('#result').removeClass('alert-danger');

      if (response_bool) {
        $('#result').addClass('alert-success');
        $('#message').html(`The customer is a good customer. Granting his application will be a wise decision.`);
      } else {
        $('#result').addClass('alert-danger');
        $('#message').html(
          `The customer is a bad customer. Statistically speaking, it would be unwise to grant his application.`
        );
      }
    },
    (error) => {
      console.log(error);
    }
  );
});
