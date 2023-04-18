document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll("td[data-id]");
    console.log(rows);
    rows.forEach(row => {
        row.addEventListener("click", () => {
            var SeatNumber = row.getAttribute('data-id');
            SelectSeat(SeatNumber);
        });
    });
    const ids = Array.from(rows).map(row => row.getAttribute('data-id'));
    console.log('Element ids:', ids);
});

let selectedseats = []
const selectedSeatsInput = document.getElementById('selectedseats');
var NextButton = document.getElementById('next-button');

function SelectSeat(SeatNumber) {
    SeatNumber = SeatNumber.toString();
    const seat = document.getElementById(SeatNumber);
    console.log("Seat ID: " + seat.id); // new console log
    if (!seat) {
        console.log("Seat not found");
        return;
    }
    if (selectedseats.includes(SeatNumber)) {
        selectedseats.splice(selectedseats.indexOf(SeatNumber), 1);
        seat.classList.remove('seat-selected');
    } 
    else {
        selectedseats.push(SeatNumber);
        seat.classList.add('seat-selected');
    }
    console.log("Selected seats: " + selectedseats.join(', '));
    selectedSeatsInput.value = JSON.stringify(selectedseats);
    if (selectedseats.length >= 1) {
      NextButton.removeAttribute('disabled');
    } else {
      NextButton.setAttribute('disabled', '');
    }
}

// function FailedToSubmit(){
//     for (const seatId of selectedseats) {
//         const seat = document.getElementById(seatId);
//         if (seat) {
//           seat.classList.remove('seat-temporary');
//           seat.classList.add('seat-available');
//           seat.classList.add('seat-selected');
//         }
//       }
// }

function SubmitSelectedSeats() {
  for (const seatId of selectedseats) {
    const seat = document.getElementById(seatId);
    if (seat) {
      seat.classList.remove('seat-selected');
      seat.classList.remove('seat-available');
      seat.classList.add('seat-temporary');
    }
  }
}



