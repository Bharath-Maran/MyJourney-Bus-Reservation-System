// Get the forms and buttons
const form1 = document.getElementById('form1');
const form2 = document.getElementById('form2');
const signInButton = document.getElementById('next-button');
const proceedButton = document.getElementById('proceed-button');
const DetailsInput = document.getElementById('signindetails');

// Disable the sign in button initially
signInButton.disabled = true;

proceedButton.addEventListener('click', () => {
  // Enable the sign in button
  signInButton.disabled = false;
});

// Add event listener to the sign in button
signInButton.addEventListener('click', (event) => {
  event.preventDefault();
  
  // Get the values from form1 and form2
  const username = form1.username.value;
  const password = form1.password.value;
  const firstName = form2.first_name.value;
  const lastName = form2.last_name.value;
  const dob = form2.dob.value;
  const email = form2.email.value;
  const phoneNumber = form2.phone_number.value;

  // Create a FormData object with the values
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  formData.append('first_name', firstName);
  formData.append('last_name', lastName);
  formData.append('dob', dob);
  formData.append('email', email);
  formData.append('phone_number', phoneNumber);

  // Set the value of the `signindetails` input field
  const signindetailsValue = JSON.stringify(Object.fromEntries(formData.entries()));
  DetailsInput.value = signindetailsValue;

  // Submit the form
  form1.submit();
});
