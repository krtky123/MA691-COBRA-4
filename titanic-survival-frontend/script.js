let values = {};

const getAgeGroup = (age) => {
  const ageGroupList = [-1, 0, 5, 12, 18, 24, 35, 60, Infinity];
  if (age < 0) return 0;
  if (age >= 0 && age < 5) return 1;
  else if (age >= 5 && age < 12) return 2;
  else if (age >= 12 && age < 18) return 3;
  else if (age >= 18 && age < 24) return 4;
  else if (age >= 24 && age < 35) return 5;
  else if (age >= 35 && age < 60) return 6;
  else return 7;
};

$('#cobra-form').submit((e) => {
  // Show loading results
  $('#result').removeClass('visually-hidden');
  $('#message').html(
    '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>'
  );

  e.preventDefault();
  const serializedArray = $('#cobra-form').serializeArray();

  $.each(serializedArray, (index, field) => {
    if (field.name === 'Age') {
      ageGroup = getAgeGroup(field.value);
      values['AgeGroup'] = ageGroup;
    } else values[field.name] = +field.value;
  });

  // send a POST request
  axios({
    method: 'post',
    url: 'https://pacific-dawn-32033.herokuapp.com/predict',
    data: {
      Pclass: values.Pclass,
      Sex: values.Sex,
      SibSp: values.SibSp,
      Parch: values.Parch,
      Embarked: values.Embarked,
      AgeGroup: values.AgeGroup,
      Title: values.Title,
      FareBand: values.FareBand,
    },
  }).then(
    (response) => {
      const { survived_bool, survived_proba } = response.data;

      if ($('#result').hasClass('alert-success')) $('#result').removeClass('alert-success');
      if ($('#result').hasClass('alert-danger')) $('#result').removeClass('alert-danger');

      if (survived_bool) {
        $('#result').addClass('alert-success');
        $('#message').html(`Yes you would survive! Your survival probability will be ${survived_proba}`);
      } else {
        $('#result').addClass('alert-danger');
        $('#message').html(`Alas! You won't survive! Your death probability will be ${survived_proba}`);
      }
    },
    (error) => {
      console.log(error);
    }
  );
});
