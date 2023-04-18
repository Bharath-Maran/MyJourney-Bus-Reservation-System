function SubmitForm(){
var form = document.getElementById('passenger-form');
var passenger_forms = form.getElementsByClassName('PassengerForm');
var passenger_details = []

for (var i=0; i<passenger_forms.length; i++){
  var passenger_form = passenger_forms[i];
  var passenger = {
    first_name: passenger_form.querySelector('input[name="first_name"]').value,
    last_name: passenger_form.querySelector('input[name="last_name"]').value,
    age: passenger_form.querySelector('input[name="age"]').value,
    gender: passenger_form.querySelector('input[name="gender"]').value,
  };
  passenger_details.push(passenger);
}

const PassengerDetailsInput = document.getElementById('passengerdetails');
PassengerDetailsInput.value = JSON.stringify(passenger_details);
console.log(passenger_details)
form.submit()}