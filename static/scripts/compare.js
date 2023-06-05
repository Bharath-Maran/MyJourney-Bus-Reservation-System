var SelectedCompareOptions = []

function UpdateButton(){
  const CompareNowButton = document.getElementById('compare-now');
  if (SelectedCompareOptions.length>=2){
    CompareNowButton.removeAttribute('disabled')
  }
  else{
    CompareNowButton.setAttribute('disabled', 'disabled')
  }
}

function DisableButtons() {
  const buttons = document.getElementsByClassName('gradient-btn-searchbus-compare');
  const numSelected = SelectedCompareOptions.length;

  for (let i = 0; i < buttons.length; i++) {
    const button = buttons[i];
    const option = button.value;
    const index = SelectedCompareOptions.indexOf(option);

    if (index === -1 && numSelected >= 3) {
      button.setAttribute('disabled', 'disabled');
    } else {
      button.removeAttribute('disabled');
    }
  }
}


function AddCompare(button){
  const option = button.value;
  const index = SelectedCompareOptions.indexOf(option);

  if(index === -1){
    SelectedCompareOptions.push(option);
    button.classList.remove('gradient-btn-searchbus-compare');
    button.classList.add('gradient-btn-searchbus-compare-black');
    button.textContent = 'REMOVE COMPARE';
    console.log(SelectedCompareOptions);
  }
  else{
    SelectedCompareOptions.splice(index, 1);
    button.textContent = 'ADD TO COMPARE';
    button.classList.remove('gradient-btn-searchbus-compare-black');
    button.classList.add('gradient-btn-searchbus-compare');
    console.log(SelectedCompareOptions);
  }

  UpdateButton();
  DisableButtons();

  const CompareOptionsInput = document.getElementById('compare-options');
  CompareOptionsInput.value = JSON.stringify(SelectedCompareOptions);
}

UpdateButton();
DisableButtons();




