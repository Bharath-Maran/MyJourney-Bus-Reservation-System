const form = document.querySelector('form');
const usernameField = form.querySelector('#username');
const passwordField = form.querySelector('#password');
const errorMessage = 'Username & Password\n1 Capital Letter\n1 Numerical Value\n1 Special Character\nMinimum 4 Characters Mandatory';

const pattern = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{4,}$/;

form.addEventListener('submit', (event) => {
  if (!pattern.test(usernameField.value) || !pattern.test(passwordField.value)) {
    event.preventDefault();
    alert(errorMessage);
  }
});
