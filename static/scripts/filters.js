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
    
    const SelectedOptionsInput = document.getElementById('selected_options');
    var NextButton = document.getElementById('next-button');

    SelectedOptionsInput.value = JSON.stringify(selectedOptions);
    if(selectedOptions.length >= 1){
      NextButton.removeAttribute('disabled');
    } else{
      nextButton.setAttribute('disabled', '');
    }
  });
});

// myForm.addEventListener('submit', (event) =>{
//   event.preventDefault()
// })

// let SelectedFilters = []
// var checkbox = document.querySelectorAll('input[name="checkbox_name"]');
// const SelectedOptionsInput = document.getElementById('selected_options');
// var NextButton = document.getElementById('next-button');

// checkbox.forEach(function(checkbox){
// checkbox.addEventListener('change', (event)=>{
//   if(event.target.checked){
//     SelectedFilters.push(event.target.value);
//     console.log(SelectedFilters)
//   } else{
//     const index = SelectedFilters.indexOf(event.target.value);
//     if (index !== -1){
//       SelectedFilters.splice(index, 1);
//       console.log(SelectedFilters)
//     }
//   }

//   SelectedOptionsInput.value = JSON.stringify(SelectedFilters);
//   if(SelectedFilters.length >= 1){
//     NextButton.removeAttribute('disabled');
//   }
//   else{
//     NextButton.setAttribute('disabled', '');
//   }
// });
// });

// var FilterCheckBoxes = document.querySelectorAll('input[type="checkbox"]');

// function filterfunc(){
//   var SelectedFilters = [];

//   FilterCheckBoxes.forEach(function(checkbox){
//     if(checkbox.checked){
//       if(!SelectedFilters.hasOwnProperty(checkbox.name)){
//         SelectedFilters[checkbox.name] = [];
        
//       }
//       SelectedFilters[checkbox.name].push(checkbox.value);
//       console.log(SelectedFilters);
//     }
//   })
// }

// FilterCheckBoxes.forEach((checkbox) => {
//   checkbox.addEventListener('change', filterfunc);
// });

