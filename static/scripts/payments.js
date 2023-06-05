var input = document.getElementById('card_number');
input.onkeydown = function (){
    if(input.value.length>0){
        if((input.value.length == 4) || (input.value.length == 9) || (input.value.length == 14)){
            input.value += " ";
        }
    }
}

function setContainerId(container) {
    // Get the container ID
    const containerId = container.getAttribute('id');
    // Set the container ID in the hidden input field
    document.getElementById('container_id_input').value = containerId;
    // Submit the form
    document.forms[0].submit();
  }
