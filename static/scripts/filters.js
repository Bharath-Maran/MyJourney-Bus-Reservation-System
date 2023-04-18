const today = new Date().toISOString().split('T')[0];
const dateInput = document.querySelector('#my-date-input');

dateInput.setAttribute('min', today);
dateInput.addEventListener('input', function () {
  if (this.value < today) {
    this.value = today;
  }
});


const checkboxes = document.querySelectorAll('#filters input[type="checkbox"]');
const myForm = document.querySelector('#myForm');
const nextButton = document.querySelector('#next-button');

let selectedOptions = [];

checkboxes.forEach((checkbox) => {
  checkbox.addEventListener('change', (event) => {
    if (event.target.checked) {
      selectedOptions.push(event.target.value);
      console.log(selectedOptions);
    } else {
      const index = selectedOptions.indexOf(event.target.value);
      if (index !== -1) {
        selectedOptions.splice(index, 1);
        console.log(selectedOptions);
      }
    }
    
    const hiddenInput = document.querySelector('input[name="selected_options"]');
    hiddenInput.value = selectedOptions.join(',');
    
    if (selectedOptions.length > 0) {
      nextButton.removeAttribute('disabled');
    } else {
      nextButton.setAttribute('disabled', true);
    }
  });
});

function SubmitFilter() {
  myForm.submit();
}



